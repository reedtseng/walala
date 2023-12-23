import os
import sys

import aiohttp

from fastapi import Request, FastAPI, HTTPException

from common import chat_llm

from linebot import (
    AsyncLineBotApi, WebhookParser
)

app = FastAPI()


@app.get("/")
def hello():
    return {"status": "hello"}


@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        # tool_result = open_ai_agent.run(event.message.text)

        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='tool_result')
        )
