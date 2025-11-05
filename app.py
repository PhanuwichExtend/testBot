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
    except InvalidSignatureError as e:
        app.logger.error(f"InvalidSignatureError: {e}")
        abort(400)
    except Exception as e:
        app.logger.error(f"Webhook error: {e}")
        abort(400)

    return 'OK'


# ✅ ฟังก์ชันเมื่อมีคนส่งข้อความถึงบอท
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    import re
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS_FILE = 'credentials.json'
    SPREADSHEET_ID = '11HghFTGYjjw9Guel1Twux64f6TfgeON11qyHEQDZktA'

    user_message = event.message.text.strip()

    # 1. ดึงวันที่
    date_match = re.search(r'วันที่[\s🎉]*([\d/]+)', user_message)
    if not date_match:
        reply_text = "กรุณาระบุวันที่ เช่น 🎉วันที่ 🎉 4/11/6"
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        return
    date_str = date_match.group(1).strip()

    # 2. แยกแต่ละชื่อและยอดรวม
    lines = user_message.splitlines()
    data_lines = []
    found_date = False
    for line in lines:
        if found_date:
            data_lines.append(line)
        if 'วันที่' in line:
            found_date = True
    # data_lines จะเริ่มที่บรรทัดแรกหลังวันที่

    sales = {}
    current_name = None
    for line in data_lines:
        line = line.strip()
        if not line:
            continue
        # ถ้าเป็นชื่อใหม่
        if not re.match(r'^[0-9]', line):
            current_name = line.replace(' ', '')
            sales[current_name] = []
        elif current_name:
            # พยายามดึงตัวเลขยอดขายจากแต่ละบรรทัด
            nums = re.findall(r'[\d,]+', line)
            for n in nums:
                n = n.replace(',', '')
                try:
                    sales[current_name].append(int(n))
                except:
                    pass

    summary = {name: sum(vals) for name, vals in sales.items()}

    # 4. อัปเดต Google Sheets (แทนที่ยอดเดิมถ้ามีวันที่+ชื่อซ้ำ)
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.sheet1
        records = worksheet.get_all_records()
        for name, total in summary.items():
            # หา row ที่ตรงกับวันที่และชื่อ
            found_idx = None
            for idx, row in enumerate(records, start=2):  # start=2 เพราะ row 1 เป็น header
                if str(row.get('date')).strip() == date_str and str(row.get('name')).strip() == name:
                    found_idx = idx
                    break
            if found_idx:
                worksheet.delete_rows(found_idx)
            worksheet.append_row([date_str, name, total])
        reply_text = '\n'.join([f"{date_str} {name}: {total}" for name, total in summary.items()])
    except Exception as e:
        reply_text = f"เกิดข้อผิดพลาดในการบันทึกข้อมูลลง Google Sheets: {e}"

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
