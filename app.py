from flask import Flask, request, abort
import os
import gspread
import base64
import os, json
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
CREDENTIALS_B64 = 'ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicHJvamVjdHRlc3Rib3QtNDc3MzEyIiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiM2NhZTkxNjk5MTRhZTRjN2Q4ZGQzN2UwZDJiZDgyODI4MzQ4Nzc5NiIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZ3SUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2t3Z2dTbEFnRUFBb0lCQVFDeVQ5RE05d3lyKzFiSVxuMldLalp5L3k4NkR2RTFKK0dVRlFkZU12RDJOYm44UFhRZ01oR3RUbUtyaENWVnRlL3ZMVDlIUS92S0JqeU9kT1xucWRNdy8raTRoRHFEWktpd20xRjFyTkFBcHkvOWYweDUyMnZNeGZEdCtzMGswVmVLcDFSUWJaSWxhMUN4ZXdSQlxuZ1BsNlV0bHdUcGVKOHhTMGhSbi9aanZHMWFUYkR6SmVsNnNtYi9TcUp4c1dXT1lwUDhTRWhkZjk0c2hzTk9yS1xudmxvTVArWVpYWkJuRzVLK0hLQmVFYUV3dUthbk9idFVCUHlXRHlxaGY5ZkV1V3A2Tk1md0gvY3BkTk8xQ0hlSFxueDZRNHYvaEN4NmcrM1h1RjQrd3pRbURrTU03WjN5ZkNvWnlrZ1MyZGM3SWg2d3gySjhzbFdhOUlHQlgrTmZvRFxubEVpcXhVa1BBZ01CQUFFQ2dnRUFSZXlPMFJIQVltRDVzMkdzRUxBU1dZKzRlSWgzUFFQaVhROGR2QUtvei9GaVxuOXpMbnp6K2FaWGd6TWJBUFdMMVp0RXlVbWJuNm02YlpManZpbWNDQkhucWNCNUtkcEVRRU9jVSsvRUtUeXpEMFxuYUlUblRUSUNQUkN4Q2RNZUpUMWhEdmtvNm91ZTVUcDhmTU43RWNFVGk3c0dLZzZzKysyR09HVjY0NG84VDdxSlxuc0R3b0FQbFdHQXRDTzU4OXY4VitCNEZUdkR5L1hMY0FLTU9lSEM2Yit6TUx1NnpCMlpaRVZEVmZHSmdNOS9yaFxuRVB4OG51K2duNVByUTFEMDl5S0xMb01xQ2hudUJYeDhOTGhKZ09MSkxOSk9QaEZteFppVEl2c2FJNjdtZEpMalxuYnQrbzNZVG15UC9od01QenAwTGw2Tmxxb3pKeFk3N0kzMzhXMDlsbUlRS0JnUURvNzM5NHZwM3V2UWpJSTY3b1xucU00RW05TzJ4WlhhRWYwRitSOUlaMWdHbnJHYUtnOE1DLzBrTmlOT0ZYNFhxSTNQVmRSRitOdlNTSlE5cEV4SlxuNHZtSE0vWjdvWXd4b0paQ0FReHNSbTBhNTA0blpZdXZFWlIwM1VvbHBlU0dXTXZnT2JsVFN1MTdSdWsrSHlHSlxueEtWVWdUb3N1OWxzeVZVbDdvQW1zcG1iSXdLQmdRREQ5N1BUbXNTYTJjZk1tcGZqSW5XRVZPdGt4OFoxMlRmMlxuL1g0Q1lzSEh0c1JIRGpvWHlSeXRRbWtYank4djl6amhlYkU4Tjh0UTNWRldGSUs0VzJQZS9IekFjdk51QWxUeVxuUy83dWlxVlNiSWgrZm83QWpRVTZrOTJRZTRkRmV6UnVDL2JwZVA4ZExvS3lLV0VkTjdoSUVNa05oTkt0U2VvUVxuOFJsOUVHNy9KUUtCZ1FDMk92L0hyNkNRc0ZTWmRza1VmVk5IYWIwMHhOa2FGRzZWYUxNZmlySGo0K3pmeGIybFxuMkE4L2NCY290RW5FS25wZTFTL1BXZ1JuTzU2MXByNkVJMHpCaUZaeG5BMjRtWUJUdk14Q1BNcUlmS0s0MFlsNFxuK2REaHFHbWtrR2I2NzZiNEVWQzZKK2tvUTI2ZnllME1BY3F5RkxNMVlmU1VWZUlHWGRMbDgxMldid0tCZ1FDQlxuNWtZTGRFSHlxMzJuZ0twQjQydW1wbXZLeUNvam9ETmF3N210ZHkwZ1oyUS8vWXhBakEwNFJCZEppSjRzMjJHWFxuQklXWmR4cU1wY2Z1bVhYMUlvOVhGbUxUWnQ4NkFzMndOdlByeDNmQzVUS3ROdE1GaS9UMVdXSzdEVWNqcFlHaFxubU1pNUJuMkZLSGwyQTd2ZUZEdFJlZDdyMlNtVnVMTXhPOEE3aUpNckNRS0JnUUMwZUYwSWxSS3ZQemM4NW1yZ1xuZ3ZpRHdVQTBya015UTY2a0tYVGU1OUdHNlNlRWN0d0lGRXhIeXRyVi9UVGFScEUzU2kwb3ZpS3AvNU4xdlFoMlxuYzFrTVdIb1I2dnBUcHpZbXlQM2FWdmw3UTdvT1B4Tzg1Z2dwZ3ZyQUJ1TDRpc01jUjZXRU9zWExGdFA5UGpXVlxua1NvMXhkL1BQM2dmMVVtRGxiRXZnODN1bHc9PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogInRlc3Rib3RAcHJvamVjdHRlc3Rib3QtNDc3MzEyLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNTM3MTcyNTMyODM0MjUxMDgxOCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvdGVzdGJvdCU0MHByb2plY3R0ZXN0Ym90LTQ3NzMxMi5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo'
CHANNEL_ACCESS_TOKEN = '0JHzuf9YlOGA7xZgkeuQjeAk9s9feQ/SDOoUd977jKXjKTn1UlSeRD9gEVYLdjI2LDhM1ps3Nawjp7/AW/qaxyvyScv03ZtAFRtCyx2s/2kiMz+QFkE/m9BXg86/vg1wuSE6I+wp1pzDZF6JhWk+5AdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '9a74e13876fe461c98809f0ffcacdd39'

if not os.path.exists('credentials.json'):
    try:
        missing_padding = len(CREDENTIALS_B64) % 4
        if missing_padding:
            CREDENTIALS_B64 += '=' * (4 - missing_padding)
        decoded = base64.b64decode(CREDENTIALS_B64)
        with open('credentials.json', 'wb') as f:
            f.write(decoded)
    except Exception as e:
        print("❌ Error decoding base64:", e)

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
    import gspread
    from google.oauth2.service_account import Credentials
    from linebot.v3.messaging import (
        ReplyMessageRequest, TextMessage
    )
    from linebot.v3.messaging import ApiClient, MessagingApi

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS_FILE = 'credentials.json'
    SPREADSHEET_ID = '12WFiY5OpzRsqgagld_pOqSeknaYcWtVv1iKie3JvonY'

    user_message = event.message.text.strip()

    # ✅ ตรวจสอบว่าผู้ใช้ส่งยอดเงินสด
    if re.search(r'ยอดเงินสด', user_message):
        # ดึงวันที่ เช่น "ยอดเงินสด5/11/68"
        date_match = re.search(r'ยอดเงินสด\s*([0-9/]+)', user_message)
        if not date_match:
            reply_text = "กรุณาระบุวันที่หลังคำว่า 'ยอดเงินสด' เช่น ยอดเงินสด5/11/68"
        else:
            date_str = date_match.group(1).strip()

            # ✅ เก็บข้อความทั้งหมดต่อจาก "ยอดเงินสด"
            text_after = user_message.split('ยอดเงินสด', 1)[1].strip()
            # ลบคำวันที่ออก (เช่น '5/11/68')
            text_after = re.sub(r'^\s*[0-9/]+\s*', '', text_after)
            # ลบช่องว่างเกิน
            text_after = re.sub(r'\s+', ' ', text_after).strip()

            # ✅ เขียนลง Google Sheet
            creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(SPREADSHEET_ID)
            worksheet = sh.sheet1

            records = worksheet.get_all_records()

            # ดึงรายชื่อคอลัมน์ทั้งหมด
            all_names = set()
            for r in records:
                for k in r.keys():
                    if k not in ['วันที่', 'date', '']:
                        all_names.add(k)
            all_names.add('ยอดเงินสด')
            all_names = sorted(list(all_names))

            # รวมข้อมูลเก่าเป็น dict
            date_dict = {}
            for r in records:
                d = r.get('วันที่') or r.get('date')
                if d and str(d).strip() != 'รวม':
                    date_dict[d] = {n: r.get(n, '') for n in all_names}

            # ถ้าวันที่ยังไม่มี ให้สร้างใหม่
            if date_str not in date_dict:
                date_dict[date_str] = {n: '' for n in all_names}

            # ✅ บันทึกข้อความทั้งหมดลงในช่อง "ยอดเงินสด"
            date_dict[date_str]['ยอดเงินสด'] = text_after

            # ✅ สร้างตารางใหม่
            header = ['วันที่'] + all_names
            rows = [header]
            for d in sorted(date_dict.keys()):
                row = [d] + [date_dict[d].get(n, '') for n in all_names]
                rows.append(row)

            # ✅ แถวรวม (คำนวณเฉพาะช่องที่เป็นตัวเลข)
            total_row = ['รวม']
            for n in all_names:
                col_sum = 0
                for d in date_dict.keys():
                    val = date_dict[d].get(n, '')
                    try:
                        col_sum += int(val)
                    except:
                        pass
                total_row.append(col_sum if col_sum else '')
            rows.append(total_row)

            worksheet.clear()
            worksheet.append_rows(rows)

            reply_text = (
                f"💰 บันทึกข้อความยอดเงินสดวันที่ {date_str} เรียบร้อยแล้ว!\n\n"
                f"เนื้อหาที่เก็บ:\n{text_after}"
            )

        # ✅ ส่งข้อความกลับ LINE
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        return

    # ✅ ถ้าเป็นข้อความรายงานยอดขาย (ทั่วไป)
    date_match = re.search(r'วันที่\s*[🎉\s]*([\d/]+)', user_message)
    if not date_match:
        reply_text = "กรุณาระบุวันที่ เช่น 🎉วันที่ 4/11/68"
    else:
        date_str = date_match.group(1).strip()

        lines = user_message.splitlines()
        sales = {}
        current_person = None
        cash_block = []
        in_cash = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # ถ้าเจอหัวข้อยอดเงินสด ให้เริ่มเก็บ block
            if re.match(r'ยอดเงินสด', line):
                in_cash = True
            if in_cash:
                cash_block.append(line)
                if '=' in line:
                    in_cash = False
                continue

            # ข้ามบรรทัดที่มีคำว่า "วันที่"
            if 'วันที่' in line:
                continue

            # ตัดคำนำหน้า
            line = re.sub(r'ส่งยอดขาย\s*ร้าน\s*', '', line)
            line = re.sub(r'Your\s*Nails\s*💅🏻?', '', line, flags=re.IGNORECASE)

            # ถ้าไม่มีตัวเลขเลย -> ชื่อพนักงาน
            if not re.search(r'\d', line):
                current_person = line
                sales[current_person] = []
            elif current_person:
                m = re.search(r'([\d.,]+)', line)
                if m:
                    num_str = m.group(1)
                    num_str = num_str.replace('.', '').replace(',', '')
                    try:
                        value = int(num_str)
                    except:
                        value = 0
                    sales[current_person].append(value)

        # รวมยอดต่อคน
        total_by_person = {p: sum(v) for p, v in sales.items() if p.strip()}
        if cash_block:
            total_by_person['ยอดเงินสด'] = "\n".join(cash_block)

        # ✅ เขียนลง Google Sheet
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.sheet1

        records = worksheet.get_all_records()

        all_names = set()
        for r in records:
            for k in r.keys():
                if k not in ['วันที่', 'date', '']:
                    all_names.add(k)
        all_names.update(total_by_person.keys())
        all_names = sorted(list(all_names))

        date_dict = {}
        for r in records:
            d = r.get('วันที่') or r.get('date')
            if d and str(d).strip() != 'รวม':
                date_dict[d] = {n: r.get(n, '') for n in all_names}

        if date_str not in date_dict:
            date_dict[date_str] = {n: '' for n in all_names}

        for n, v in total_by_person.items():
            date_dict[date_str][n] = v

        header = ['วันที่'] + all_names
        rows = [header]
        for d in sorted(date_dict.keys()):
            row = [d] + [date_dict[d].get(n, '') for n in all_names]
            rows.append(row)

        total_row = ['รวม']
        for n in all_names:
            col_sum = 0
            for d in date_dict.keys():
                val = date_dict[d].get(n, '')
                try:
                    col_sum += int(val)
                except:
                    pass
            total_row.append(col_sum if col_sum else '')
        rows.append(total_row)

        worksheet.clear()
        worksheet.append_rows(rows)

        reply_text = f"✅ บันทึกยอดขายวันที่ {date_str} เรียบร้อยแล้ว!"

    # ✅ ตอบกลับ LINE
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
