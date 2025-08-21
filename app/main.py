import os

from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.utils.logging import setup_logging
from app.router.whatsapp import router as whatsapp_router
from app.router.llm import router as llm_router
from dotenv import load_dotenv, find_dotenv
_: bool = load_dotenv(find_dotenv())

setup_logging()
from langchain_core.messages import HumanMessage
from app.interfaces.llm import ChatLLM
from app.interfaces.airtable import PostgresClient
db_client = PostgresClient()



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app():
    app = FastAPI(lifespan=lifespan, prefix="/api/v1")
    app.include_router(whatsapp_router,prefix="/webhook/whatsapp")
    app.include_router(llm_router,prefix="/llm")

    # Only mount static files if directory exists
    static_dir = "static/media"
    if os.path.exists(static_dir):
        app.mount("/media", StaticFiles(directory=static_dir), name="media")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

@app.on_event("startup")
async def startup():
    await db_client.initialize()

@app.get("/")
def root():
    return {"message": "OK"}


@app.get("/health")
def health():
    return {"message": "I am Healthy :)"}
