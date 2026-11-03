import logging
import os
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request
from aiogram.types import Update

from bot import dp, get_bot

logging.basicConfig(level=logging.INFO)

app = FastAPI()
bot = get_bot()
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')


@app.get('/api/webhook')
async def health():
    return {'status': 'ok'}


@app.post('/api/webhook')
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail='WEBHOOK_SECRET is not configured')
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail='Invalid webhook secret')

    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dp.feed_webhook_update(bot, update)
    return {'ok': True}
