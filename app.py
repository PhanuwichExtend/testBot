from flask import Flask, request, abort
import os
import gspread
from google.oauth2.service_account import Credentials

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 🔑 Channel Access Token และ Secret
CHANNEL_ACCESS_TOKEN = '0JHzuf9YlOGA7xZgkeuQjeAk9s9feQ/SDOoUd977jKXjKTn1UlSeRD9gEVYLdjI2LDhM1ps3Nawjp7/AW/qaxyvyScv03ZtAFRtCyx2s/2kiMz+QFkE/m9BXg86/vg1wuSE6I+wp1pzDZF6JhWk+5AdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '9a74e13876fe461c98809f0ffcacdd39'

# LINE SDK config
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def index():
    return "✅ LINE Bot is running!"

# ✅ Webhook route ต้องตรงกับ URL ที่ตั้งใน LINE Developers
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    app.logger.info("Received webhook body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# ✅ ฟังก์ชันเมื่อมีคนส่งข้อความถึงบอท
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.strip()

    # Google Sheets config
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS_FILE = 'credentials.json'  # ต้องวางไฟล์นี้ไว้ในโฟลเดอร์เดียวกับ app.py
    SPREADSHEET_ID = '11HghFTGYjjw9Guel1Twux64f6TfgeON11qyHEQDZktA'

    try:
        name, amount = user_message.split()
        amount = int(amount)
    except Exception:
        reply_text = "กรุณาพิมพ์ในรูปแบบ: ชื่อ จำนวนเงิน (เช่น มิ้น 500)"
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        return


    # อ่านและบันทึกข้อมูลลง Google Sheets
    try:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.sheet1
        records = worksheet.get_all_records()
        total = sum(int(row['amount']) for row in records if str(row['amount']).isdigit()) if records else 0
        total += amount
        worksheet.append_row([name, amount, total])
        reply_text = f"บันทึกแล้ว: {name} {amount}\nยอดรวมล่าสุด: {total}"
    except Exception as e:
        reply_text = f"เกิดข้อผิดพลาดในการบันทึกข้อมูลลง Google Sheets: {e}"

    # ✅ ตอบกลับผู้ใช้
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
