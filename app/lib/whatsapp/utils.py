import os
import logging
import json
import aiohttp
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.lib.whatsapp.message import WhatsAppMessageHandler


class WhatsAppWebhook:
    def __init__(
        self,
        verify_token: str = None,
        access_token: str = None,
        phone_number_id: str = None,
        version: str = None,
        media_static_url: str = None,
    ):
        self.verify_token = verify_token or os.getenv("VERIFY_TOKEN")
        self.access_token = access_token or os.getenv("ACCESS_TOKEN")
        self.phone_number_id = phone_number_id or os.getenv("PHONE_NUMBER_ID")
        self.version = version or os.getenv("VERSION")
        self.media_static_url = media_static_url or os.getenv(
            "MEDIA_STATIC_URL", "http://localhost:8000"
        )
        self.message_handler = WhatsAppMessageHandler(
            self.access_token, self.phone_number_id, self.version, self.media_static_url
        )

    def verify(self, request: Request):
        # Parse query parameters from the webhook verification request
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == self.verify_token:
                logging.info("WEBHOOK_VERIFIED")
                return Response(
                    content=challenge, media_type="text/plain", status_code=200
                )
            else:
                logging.info("VERIFICATION_FAILED")
                return JSONResponse(
                    content={"status": "error", "message": "Verification failed"},
                    status_code=403,
                )
        else:
            logging.info("MISSING_PARAMETER")
            return JSONResponse(
                content={"status": "error", "message": "Missing parameters"},
                status_code=400,
            )

    async def handle_message(self, request: Request):
        """
        Handle incoming webhook events from the WhatsApp API.
        Processes incoming WhatsApp messages (or status updates) and returns appropriate responses.
        """
        try:
            body = await request.json()
        except Exception as e:
            logging.error("Failed to decode JSON: %s", e)
            return JSONResponse(
                content={"status": "error", "message": "Invalid JSON provided"},
                status_code=400,
            )

        # Check if it's a WhatsApp status update
        if (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        ):
            logging.info("Received a WhatsApp status update.")
            return JSONResponse(content={"status": "ok"}, status_code=200)

        try:
            if self.is_valid_whatsapp_message(body):
                await self.message_handler.process_message(body)
                return JSONResponse(content={"status": "ok"}, status_code=200)
            else:
                return JSONResponse(
                    content={"status": "error", "message": "Not a WhatsApp API event"},
                    status_code=404,
                )
        except Exception as e:
            logging.error("Error processing WhatsApp message: %s", e)
            return JSONResponse(
                content={"status": "error", "message": "Error processing message"},
                status_code=400,
            )

    def is_valid_whatsapp_message(self, body):
        """
        Check if the incoming webhook event has a valid WhatsApp message structure.
        """
        return (
            body.get("object")
            and body.get("entry")
            and body["entry"][0].get("changes")
            and body["entry"][0]["changes"][0].get("value")
            and body["entry"][0]["changes"][0]["value"].get("messages")
            and body["entry"][0]["changes"][0]["value"]["messages"][0]
        )
