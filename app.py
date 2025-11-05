from flask import Flask, request, abort

import csv
import os
from linebot.v3.messaging import MessagingApi
from linebot.v3.webhook import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 🔑 ใส่ค่า Channel Access Token และ Channel Secret ของคุณที่นี่
CHANNEL_ACCESS_TOKEN = '2008421597'
CHANNEL_SECRET = '9a74e13876fe461c98809f0ffcacdd39'

line_bot_api = MessagingApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# ✅ Route หลัก สำหรับทดสอบ
@app.route("/", methods=['GET'])
def index():
    return "LINE Bot is running!"


# ✅ Webhook ที่ LINE จะยิงมาหา
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# ✅ เมื่อมีคนส่งข้อความมาหา Bot

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    csv_file = 'data.csv'

    # พยายามแยกชื่อและจำนวนเงิน เช่น "มิ้น 500"
    try:
        name, amount = user_message.split()
        amount = int(amount)
    except Exception:
        reply_text = "กรุณาพิมพ์ในรูปแบบ: ชื่อ จำนวนเงิน (เช่น มิ้น 500)"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return

    # อ่านข้อมูลเก่า ถ้ามี
    rows = []
    total = 0
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                try:
                    total += int(row['amount'])
                except Exception:
                    pass

    # เพิ่มข้อมูลใหม่
    total += amount
    rows.append({'name': name, 'amount': amount, 'total': total})

    # เขียนข้อมูลใหม่ลงไฟล์
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'amount', 'total'])
        writer.writeheader()
        writer.writerows(rows)

    reply_text = f"บันทึกแล้ว: {name} {amount}\nยอดรวมล่าสุด: {total}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    app.run(port=3000)
