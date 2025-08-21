import os
from dotenv import load_dotenv, find_dotenv

from typing import Literal
import logging
from langchain_openai import ChatOpenAI

_: bool = load_dotenv(find_dotenv())
from openai import Client

client = Client()

class ChatLLM:
    def __init__(self):
        pass

    def get_openai_llm(
        self,
        model_name: Literal["gpt-4o-2024-11-20", "gpt-4o-mini"],
        temprature: float | None = 0.5,
    ):
        api_key = os.getenv("OPENAI_API_KEY")
        model = ChatOpenAI(
            temperature=temprature,
            model=model_name,
            streaming=True,
            max_retries=5,
            api_key=api_key,
        )
        return model

    def transcribe_audio(self,audio_path):
        with open(audio_path, "rb") as audio_file:  # Open the file in binary mode
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        print(response)
        return response.text      
        
          
    def process_image(self,image_url):
        response = client.chat.completions.create(
            model= "gpt-4o",
            messages= [{"role":"user", "content":[{"type":"text","text":"Extract product, quantity and location from this image."},{"type":"image_url", "image_url":image_url}]}]
        )
        return response.choices[0].message.content