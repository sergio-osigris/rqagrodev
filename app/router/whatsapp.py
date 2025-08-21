from fastapi import APIRouter, Request
from app.lib.whatsapp.utils import WhatsAppWebhook

router = APIRouter()
whatsapp_webhook = WhatsAppWebhook()


@router.get("")
async def verify_webhook(request: Request):
    return whatsapp_webhook.verify(request)


@router.post("")
async def handle_webhook(request: Request):
    return await whatsapp_webhook.handle_message(request)
