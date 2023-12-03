from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

ticker_tracks = {
    "1723.tw": {
        "code": "1723",
        "name": "中碳",
        "target": 110,
        "date": None
    },
    "6279.tw": {
        "code": "6279",
        "name": "胡連",
        "target": 150,
        "date": None
    }
}

TRACK_ADD_TIP = "格式應為 股票:[台股代號或名稱] 目標價:[價格]"

tw_stocks = {}
reversed_stocks = {}


def load_tw_stocks():
    with open('tw_stocks.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(':')
            tw_stocks[key] = value
    print(tw_stocks)
    for key, value in tw_stocks.items():
        reversed_stocks[value] = key
    print(reversed_stocks)


def process_command(command):

    response = f"指令內容: {command}\n"
    match command:
        case value if "追蹤清單" in value:
            response += "\n追蹤清單如下："
            for ticker in ticker_tracks.values():
                print(ticker)
                response += f"\n股票名: {ticker['name']}\n目標價: {ticker['target']}"
        case value if value.startswith('新增追蹤'):
            track_body = value[4:]
            lines = re.split(r'\s|,|，|;', track_body)
            symbol, target = None, None
            for line in lines:
                match line:
                    case v if v.startswith("股票"):
                        stock = v.split(':')[1].strip()
                    case v if v.startswith("目標價"):
                        target = int(v.split(':')[1].strip())
                    case _:
                        pass
            if stock is None:
                response += f"\n不好意思！沒按照正確格式新增股票。" + TRACK_ADD_TIP
            elif target is None:
                response += f"\n不好意思！沒按照正確格式設定目標價。" + TRACK_ADD_TIP
            else:
                stock_code, stock_name = None, None
                if stock in tw_stocks:
                    stock_code, stock_name = stock, tw_stocks[stock]
                if stock in reversed_stocks:
                    stock_code, stock_name = reversed_stocks[stock], stock
                if stock_code is None:
                    response += f"\n抱歉！無該股票資訊 {stock}"
                else:
                    ticker_tracks[f"{stock_code}.tw"] = {
                        "code": stock_code,
                        "name": stock_name,
                        "target": target,
                        "date": None,
                    }
                    response += f"\n已新增股票追蹤 {stock_code}{
                        stock_name}，目標價為 {target}"
        case value if value.startswith('刪除追蹤'):
            stock = value[4:]
            ticker = ticker_tracks.pop(stock + ".tw", None)
            if ticker is None:
                stock_code = reversed_stocks.get(stock, None)
                if stock_code is not None:
                    ticker = ticker_tracks.pop(stock_code + ".tw", None)
            if ticker is None:
                response += f"\n無追蹤此股票 {stock}!"
            else:
                response += f"\n已刪除此追蹤 {stock}!"
        case _:
            response += "\n不好意思，能力有限，目前無法做到。"
    return response


@app.route("/text", methods=['POST'])
def handle_text():
    body = request.get_data(as_text=True)
    return process_command(body)

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
        command = event.message.text[4:]
        response = process_command(command)
        message = TextSendMessage(text=response)
        line_bot_api.reply_message(event.reply_token, message)


@app.route('/')
def hello():
    return "Hello, I'm Walala."


if __name__ == "__main__":
    load_tw_stocks()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
