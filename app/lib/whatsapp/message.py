import os, json, aiohttp, logging, aiofiles, uuid
from app.lib.graphs.agent_with_tools.state import ChatState
from app.router.llm import agent_with_tools_graph
from app.interfaces.llm import ChatLLM
import logging
from app.interfaces.airtable import PostgresClient
from app.interfaces.optimly import OptimlyClient
from typing import Dict
from app.prompts import AGENT_WITH_TOOLS_NODE
from app.utils.pydantic_formatters import generar_listado_campos
from app.models.record import RecordRequest
import datetime
# Define tokens and IDs from environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

OPTIMLY_API_KEY = os.getenv("OPTIMLY_API_KEY")
OPTIMLY_BASE_URL = os.getenv("OPTIMLY_BASE_URL")
USE_OPTIMLY = os.getenv("USE_OPTIMLY", "false").lower() in ("true", "1", "yes")
import re

BUTTON_REGEX = r"\[button:([^\]]+)\]"

def extract_buttons(text):
    match = re.search(BUTTON_REGEX, text)
    if match:
        titles = match.group(1).split("|")
        return [title.strip() for title in titles]
    return []

class WhatsAppMessageHandler:
    def __init__(
        self,
        access_token: str = None,
        phone_number_id: str = None,
        version: str = None,
        media_static_url: str = None,
    ):
        self.access_token = access_token or os.getenv("ACCESS_TOKEN")
        self.phone_number_id = phone_number_id or os.getenv("PHONE_NUMBER_ID")
        self.version = version or os.getenv("VERSION")
        self.media_static_url = media_static_url or os.getenv(
            "MEDIA_STATIC_URL", "http://localhost:8000"
        )
        self.chat_history = {}  # In-memory chat history store
        self.chat_ids = {}

        self.db_client = PostgresClient()
        self.optimly_client = OptimlyClient(api_key=OPTIMLY_API_KEY,base_api_url=OPTIMLY_BASE_URL)
        
        
    async def _getUserInfo(self,phone_number):
        userInfo = await self.db_client.find_user(phone_number)

        if len(userInfo)==0:
            return {}
        return userInfo[0]

    async def generate_response(
        self, userInfo: dict, chat_history: list[Dict[str,str]], phone_number:str
    ) -> str:
        
        logging.debug(f"Current user info: {userInfo}")
        # state = ChatState(
        #     messages=chat_history,
        #     user_id=str(userInfo.get("user_id", "unknown_user")),
        #     name=str(userInfo.get("name", "Desconocido")),
        # )
        state = self.get_prev_state(phone_number)
        logging.debug(f"Current state: {state}")
        response = await agent_with_tools_graph.ainvoke(state)
        self.update_state(phone_number, response)
        output_text= response["messages"][-1]['content']
        logging.info(f"Assistant response: {output_text}")
        # self.add_to_history(phone_number, output_text, "assistant")
        if response.get("record_added",False) == True:
            logging.info("Detected new record added. Deleting chat history")
            self.clear_chat_history(phone_number)
        return output_text
    
    def build_button_payload(self,recipient:str, text:str, button_titles:dict):
        buttons = [
            {"type": "reply", "reply": {"id": f"btn_{i}", "title": title}}
            for i, title in enumerate(button_titles, 1)
        ]
        # Remove the [button:...] part from the text
        clean_text = re.sub(BUTTON_REGEX, "", text).strip()
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": clean_text},
                "action": {"buttons": buttons}
            }
        }
    
    def build_list_payload(self, recipient: str, text: str, options: list):
        rows = [{"id": opt, "title": opt[:24]} for opt in options]  # título máx 24 chars
        # Remove the [button:...] part from the text
        clean_text = re.sub(BUTTON_REGEX, "", text).strip()
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": clean_text},
                "action": {
                    "button": "Ver opciones",  # texto del botón que abre el menú
                    "sections": [
                        {
                            "title": "Cultivos disponibles",
                            "rows": rows
                        }
                    ],
                },
            },
        }

    def get_text_message_input(self, recipient: str, text: str) -> str:
        """
        Prepare the JSON payload for a text message.
        """
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )

    async def send_whatsapp_message(self, recipient: str, text: str):
        """
        Send a WhatsApp text message using the Facebook Graph API.
        """
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        url = (
            f"https://graph.facebook.com/{self.version}/{self.phone_number_id}/messages"
        )
        button_titles = extract_buttons(text)
        if button_titles:
            # Si hay más de 3 opciones o alguna supera 20 caracteres → usar menú
            if len(button_titles) > 3 or any(len(t) > 20 for t in button_titles):
                payload = self.build_list_payload(recipient, text, button_titles)
            else:
                payload = self.build_button_payload(recipient, text, button_titles)
            data = json.dumps(payload)
        else:
            data = self.get_text_message_input(recipient, text)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    print("Message sent successfully")
                else:
                    resp_text = await response.text()
                    print(
                        f"Failed to send message, status {response.status}, response: {resp_text}"
                    )

    async def process_message(self, body):
        """
        Process the incoming WhatsApp message and send a dynamic reply.
        """
        await self.db_client.initialize()
        #logging.debug(body)
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        msg_type = message.get("type")
        logging.info(f"New message from {wa_id}")
        # Extract and immediately store the user message into chat history
        if msg_type == "text":
            user_message = message.get("text", {}).get("body", "")
        elif msg_type == "interactive":
            # WhatsApp interactive replies (button, list, etc.)
            interactive = message.get("interactive", {})
            if "button_reply" in interactive:
                user_message = interactive["button_reply"].get("title", "")
            elif "list_reply" in interactive:
                user_message = interactive["list_reply"].get("title", "")
            else:
                user_message = "Received an interactive message"
        elif msg_type == "image":
            media_id = message.get("image", {}).get("id")
            if media_id:
                file_url = await self.download_media_file(media_id)
                logging.info(f"Downloaded image URL: {file_url}")
                
                user_message = "Sent an image"
            else:
                user_message = "Sent an image but no media ID"
        elif msg_type == "audio":
            media_id = message.get("audio", {}).get("id")
            if media_id:
                file_url = await self.download_media_file(media_id)
                logging.info(f"Downloaded audio URL: {file_url}")
                ## Transcript audio

                user_message = ChatLLM().transcribe_audio(file_url)
            else:
                user_message = "Sent an audio but no media ID"
        else:
            user_message = f"Unsupported message type: {msg_type}"

        # Add the incoming user message to chat history
        userInfo = await self._getUserInfo(wa_id)

        self.add_to_history(wa_id, user_message, "user",userInfo=userInfo)

        current_history = self.get_chat_history(wa_id)

        # Process the message to generate bot response
        if msg_type == "text" or msg_type == "interactive":
            response_text = await self.generate_response(userInfo, current_history,wa_id)
        elif msg_type == "image":
            if media_id:
                response_text = f"Received image: {file_url}"
            else:
                response_text = "Received an image but could not extract media ID."
        elif msg_type == "audio":
            if media_id:
                response_text = await self.generate_response(userInfo, current_history,wa_id)
            else:
                response_text = "Received an audio but could not extract media ID."
        else:
            response_text = user_message

        # Add the bot's response to history
        

        await self.send_whatsapp_message(wa_id, response_text)

    async def get_media_url(self, media_id: str) -> str:
        """
        Retrieve the media URL from the WhatsApp Cloud API.
        """
        url = f"https://graph.facebook.com/{self.version}/{media_id}/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.info(f"Media URL from API: {data}")
                    return data.get("url", "No URL found")
                else:
                    logging.error(
                        "Failed to get media URL, status: %s", response.status
                    )
                    return "Error fetching media URL"

    async def download_media_file(self, media_id: str) -> str:
        """
        Download media file and return accessible URL.
        - Saves file to static/media directory.
        - Returns URL in format: {MEDIA_STATIC_URL}/media/{filename}
        """
        temp_url = await self.get_media_url(media_id)
        if not temp_url or temp_url.startswith("Error"):
            return temp_url

        async with aiohttp.ClientSession() as session:
            async with session.get(
                temp_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                allow_redirects=True,
            ) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    content_type = resp.headers.get("Content-Type", "")
                    os.makedirs("static/media", exist_ok=True)
                    ext = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "audio/mpeg": ".mp3",
                        "audio/ogg": ".ogg",
                    }.get(content_type.split(";")[0], "")
                    filename = f"{media_id}{ext}"
                    filepath = f"static/media/{filename}"
                    async with aiofiles.open(filepath, "wb") as f:
                        await f.write(data)
                    return f"static/media/{filename}"

                logging.error(f"Failed to download media: {resp.status}")
                return "Error downloading media file"

    def add_to_history(self, user_id: str, message: str, sender: str,id:str = "",userInfo:Dict = None):
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
            self.chat_ids[user_id] = None
        if len(self.chat_history[user_id])==0:
            logging.info(f"Initializing chat with system prompt")
            self.chat_history[user_id].append({"role":"system", "content":AGENT_WITH_TOOLS_NODE.format(
                user_id=userInfo.get("user_id", "Desconocido"),
                name=userInfo.get("name", "Desconocido"),
                size=userInfo.get("Hectáreas", "Desconocido"),
                listado_campos=generar_listado_campos(RecordRequest),current_date=datetime.datetime.now().strftime("%Y-%m-%d")
                    ),"tool_call_id":"",
                })
        self.chat_history[user_id].append({"role":sender, "content":message,"tool_call_id":id})

    def update_state(self,user_id:str,state:ChatState):
        self.chat_history[user_id] = state.messages

    def get_prev_state(self, user_id: str):
        raw_state = self.chat_history.get(user_id)
        if not raw_state:
            # No hay historial, devuelvo nuevo estado vacío
            return ChatState(messages=[], user_id=user_id, name="Desconocido")

        # Si raw_state ya es un ChatState, devuélvelo
        if isinstance(raw_state, ChatState):
            return raw_state

        # Si es dict o similar, intenta construir ChatState limpiando mensajes
        if isinstance(raw_state, dict):
            messages = raw_state.get("messages", [])
        else:
            # raw_state es probablemente una lista de mensajes (tu chat_history)
            messages = raw_state

        # Limpia los mensajes: solo role y content
        clean_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        return ChatState(messages=clean_messages, user_id=user_id, name="Desconocido")



    def get_chat_history(self, user_id: str):
        return self.chat_history.get(user_id, [])
    
    def clear_chat_history(self, user_id: str):
        if user_id in self.chat_history: 
            self.chat_history[user_id] = []
            self.chat_ids[user_id] = None
        else:
            logging.warning(f"User {user_id} not found in chat history")

    def convert_chat_history_to_messages(
        self, chat_history: list[Dict[str, str]]
    ) -> list[Dict[str, str]]:
        return chat_history
