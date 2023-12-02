from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

ticker_tracks = {
    "1723.tw": {
        "symbol": "1723",
        "name": "中碳",
        "target": 110,
        "date": None
    },
    "6279.tw": {
        "symbol": "6279",
        "name": "胡連",
        "target": 150,
        "date": None
    }
}

# 設定接收 Line Bot 的 Webhook


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if "WALA" in event.message.text.upper():
        text = f"指令內容: {event.message.text}\n"
        match event.message.text:
            case value if "追蹤清單" in value:
                text += "\n追蹤清單如下："
                for ticker in ticker_tracks.values:
                    text += f"\n股票名: {ticker.name}\n目標價: {ticker.target}"
            case _:
                text += "\n不好意思，能力有限，目前無法做到。"
        message = TextSendMessage(text=text)
        line_bot_api.reply_message(event.reply_token, message)


@app.route('/')
def hello():
    return "Hello, I'm Walala."


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
