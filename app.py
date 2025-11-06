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
    import datetime
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
    today = datetime.date.today()

    # ✅ สร้างตัวเชื่อมกับ Google Sheet
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.sheet1
    records = worksheet.get_all_records()

    # -------------------------------------------------
    # ✅ ฟังก์ชันดึงยอดรายวัน / รายเดือน
    # -------------------------------------------------
    
    def get_daily_total(date_str):
        for r in records:
            if str(r.get('วันที่')).strip() == date_str:
                result_lines = [f"📅 ยอดวันที่ {date_str}"]
                for k, v in r.items():
                    if k not in ['วันที่', 'date'] and str(v).strip():
                        result_lines.append(f"{k}: {v}")
                return "\n".join(result_lines)
        return f"❌ ไม่พบข้อมูลวันที่ {date_str}"

    def get_month_total(month_num):
        month_sum = {}
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue
            # แยกวันที่เป็นส่วน ๆ
            m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
            if m:
                _, m_str, _ = m.groups()
                if int(m_str) == int(month_num):
                    for k, v in r.items():
                        if k not in ['วันที่', 'date', 'ยอดเงินสด']:
                            try:
                                month_sum[k] = month_sum.get(k, 0) + int(v)
                            except:
                                pass
        if not month_sum:
            return f"❌ ไม่พบข้อมูลเดือน {month_num}"
        text = [f"📆 ยอดรวมเดือน {month_num}"]
        for k, v in month_sum.items():
            text.append(f"{k}: {v}฿")
        text.append(f"💰 รวมทั้งหมด: {sum(month_sum.values())}฿")
        return "\n".join(text)

    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “เช็คยอดรายวัน” เช่น "ยอดเงินวันที่ 6/11/68"
    # -------------------------------------------------
    if re.search(r'ยอดเงินวันที่', user_message):
        msg = user_message.replace('ยอดเงินวันที่', '').strip()
        msg = msg.replace('-', '/')
        parts = msg.split('/')
        if len(parts) == 3:
            date_str = msg
        elif len(parts) == 1 and parts[0].isdigit():
            day = int(parts[0])
            date_str = f"{day}/{today.month}/{today.year % 100}"
        else:
            reply_text = "⚠️ รูปแบบไม่ถูกต้อง เช่น ยอดเงินวันที่ 6/11/68"
            send_reply(event, reply_text)
            return

        reply_text = get_daily_total(date_str)
        send_reply(event, reply_text)
        return

    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ยอดเงินรวมเดือน”
    # -------------------------------------------------
    if re.search(r'ยอดเงินรวมเดือน', user_message):
        month_match = re.search(r'ยอดเงินรวมเดือน\s*(\d+)', user_message)
        if month_match:
            month_num = int(month_match.group(1))
        else:
            month_num = today.month
        reply_text = get_month_total(month_num)
        send_reply(event, reply_text)
        return

    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ยอดเงินรวม” (เดือนปัจจุบัน)
    # -------------------------------------------------
    if re.fullmatch(r'ยอดเงินรวม', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return

    if re.fullmatch(r'ยอดเงินเดือนนี้', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return
    if re.fullmatch(r'ยอดเดือนนี้', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return
    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ยอดเงินสด”
    # -------------------------------------------------
    if re.search(r'ยอดเงินสด', user_message):
        date_match = re.search(r'ยอดเงินสด\s*([0-9/]+)', user_message)
        if not date_match:
            reply_text = "กรุณาระบุวันที่หลังคำว่า 'ยอดเงินสด' เช่น ยอดเงินสด5/11/68"
        else:
            date_str = date_match.group(1).strip()
            # ถ้า date_str ไม่มีปี (เช่น 6/11 หรือ 06/11) ให้เติมปีไทยปัจจุบัน
            import datetime
            parts = date_str.split('/')
            if len(parts) == 2:
                thai_year = str(datetime.datetime.now().year + 543)[-2:]
                date_str = f"{parts[0]}/{parts[1]}/{thai_year}"
            text_after = user_message.split('ยอดเงินสด', 1)[1].strip()
            text_after = re.sub(r'^\s*[0-9/]+\s*', '', text_after).strip()

            all_names = set()
            for r in records:
                for k in r.keys():
                    if k not in ['วันที่', 'date', '']:
                        all_names.add(k)
            all_names.add('ยอดเงินสด')
            all_names = sorted(list(all_names))

            date_dict = {}
            for r in records:
                d = r.get('วันที่') or r.get('date')
                if d and str(d).strip() != 'รวม':
                    date_dict[d] = {n: r.get(n, '') for n in all_names}

            if date_str not in date_dict:
                date_dict[date_str] = {n: '' for n in all_names}

            date_dict[date_str]['ยอดเงินสด'] = text_after

            # ✅ เขียนกลับชีต
            header = ['วันที่'] + all_names
            rows = [header]
            for d in sorted(date_dict.keys()):
                row = [d] + [date_dict[d].get(n, '') for n in all_names]
                rows.append(row)

            worksheet.clear()
            worksheet.append_rows(rows)

            reply_text = (
                f"💰 บันทึกยอดเงินสดวันที่ {date_str} เรียบร้อยแล้ว!\n\n"
                f"เนื้อหาที่เก็บ:\n{text_after}"
            )
        send_reply(event, reply_text)
        return

    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ส่งยอดขาย ร้าน Your Nails”
    # -------------------------------------------------
    elif re.search(r'ส่งยอดขาย', user_message):
        user_message = user_message.split('ยอดเงินสด', 1)[0].strip()

        date_match = re.search(r'วันที่\s*[🎉\s]*([\d/]+)', user_message)
        if not date_match:
            reply_text = "กรุณาระบุวันที่ เช่น 🎉วันที่ 6/11/68"
        else:
            date_str = date_match.group(1).strip()
            lines = user_message.splitlines()
            sales = {}
            current_person = None

            for line in lines:
                line = line.strip()
                if not line or 'วันที่' in line:
                    continue
                line = re.sub(r'ส่งยอดขาย\s*ร้าน\s*', '', line)
                line = re.sub(r'Your\s*Nails\s*💅🏻?', '', line, flags=re.IGNORECASE)
                line = re.sub(r'^\d+\.', '', line).strip()
                if not re.search(r'\d', line):
                    current_person = line
                    sales[current_person] = []
                    continue
                if current_person:
                    m = re.search(r'([\d,]+)', line)
                    if m:
                        num_str = m.group(1).replace(',', '').replace('.', '')
                        try:
                            value = int(num_str)
                        except:
                            value = 0
                        sales[current_person].append(value)

            total_by_person = {p: sum(v) for p, v in sales.items() if p.strip()}

            all_names = set()
            for r in records:
                for k in r.keys():
                    if k not in ['วันที่', 'date', '', 'Your Nails 💅🏻']:
                        all_names.add(k)
            for n in total_by_person.keys():
                if n.strip():
                    all_names.add(n)
            all_names.add('ยอดเงินสด')
            all_names = sorted(list(all_names))

            date_dict = {}
            for r in records:
                d = r.get('วันที่') or r.get('date')
                if d and str(d).strip() != 'รวม':
                    date_dict[d] = {n: r.get(n, 0) for n in all_names}

            if date_str in date_dict:
                for n in all_names:
                    if n != 'ยอดเงินสด':
                        date_dict[date_str][n] = total_by_person.get(n, date_dict[date_str].get(n, 0))
            else:
                date_dict[date_str] = {n: total_by_person.get(n, 0) for n in all_names}
                date_dict[date_str]['ยอดเงินสด'] = ''

            header = ['วันที่'] + all_names
            rows = [header]
            for d in sorted(date_dict.keys()):
                row = [d] + [date_dict[d].get(n, '') for n in all_names]
                rows.append(row)
            worksheet.clear()
            worksheet.append_rows(rows)

            reply_text = (
                f"📅 บันทึกยอดขายวันที่ {date_str} เรียบร้อยแล้ว!\n\n"
                + "\n".join([f"{n}: {v}฿" for n, v in total_by_person.items()])
            )
    FAQ = {
        "ร้านอยู่ที่ไหน": "ร้านอยู่ที่เซ็นทรัล พระราม 2 ชั้น 2 ข้างร้านกาแฟ Cafe Amazon ค่ะ 💅",
        "ร้านเปิดกี่โมง": "ร้านเปิดทุกวัน 10:00 - 20:00 น. ค่ะ 💕",
        "ร้านปิดกี่โมง": "ร้านปิดเวลา 20:00 น. ทุกวันค่ะ 🕗",
        "เบอร์โทร": "สามารถติดต่อร้านได้ที่ 081-234-5678 📞",
        "ต่อขนตากี่บาท": "ราคาต่อขนตาเริ่มต้นที่ 499 บาทค่ะ 😍",
        "ทำเล็บกี่บาท": "ทำเล็บเริ่มต้นที่ 299 บาทค่ะ 💅🏻",
        "ล้างเล็บเท่าไหร่": "ล้างเล็บ 100 บาทค่ะ",
        "มีต่อเล็บไหม": "มีค่ะ ต่อเล็บอะคริลิกและเจล ราคาเริ่มต้น 899 บาท 💅",
        "รับบัตรเครดิตไหม": "รับบัตรเครดิตทุกธนาคารค่ะ 💳",
        "มีที่จอดรถไหม": "มีที่จอดรถที่ศูนย์การค้าค่ะ 🚗",
        "ร้านชื่ออะไร": "ร้านชื่อ Your Nails 💅🏻 ค่ะ",
        "ขนตาร่วงทำไง": "ไม่ต้องกังวลนะคะ ถ้าขนตาร่วงใน 7 วันแรกสามารถเข้ามาแก้ฟรีค่ะ 💖",
        "ทำผมไหม": "ขณะนี้รับเฉพาะทำเล็บและต่อขนตาค่ะ 💅",
        "โปรโมชั่น": "ตอนนี้มีโปรต่อขนตา 599 บาท จาก 799 บาท ถึงสิ้นเดือนนี้เท่านั้น 🎉",
        "นัดหมายยังไง": "สามารถจองคิวผ่าน LINE นี้ได้เลยค่ะ หรือโทร 081-234-5678 ☎️",
        "จองคิวได้ไหม": "ได้เลยค่ะ พิมพ์วันที่และเวลาที่ต้องการมาได้เลย 💕",
        "มีต่อขนตาแบบไหนบ้าง": "เรามีต่อแบบธรรมชาติ ฟูวิ้ง และวอลลุ่มค่ะ 😍",
        "รับบัตรสวัสดิการไหม": "ขออภัยค่ะ ยังไม่รับบัตรสวัสดิการแห่งรัฐนะคะ",
        "รับโอนผ่านแอปไหม": "ได้ค่ะ รับทุกธนาคารผ่าน QR พร้อมเพย์เลย 💸",
        "วันนี้วันอะไร": f"วันนี้คือวัน{today.strftime('%A')} ที่ {today.day}/{today.month}/{today.year + 543} ค่ะ 📅",
        "ใครเป็นเจ้าของร้าน": "เจ้าของร้านคือพี่ชมคนสวยค่ะ 💖",
        "ทำเล็บเท้าไหม": "มีค่ะ ทำเล็บเท้าเริ่มต้นที่ 350 บาท 👣",
        "ทาสีเจลไหม": "มีค่ะ ทาสีเจลเริ่มต้น 399 บาท 💅",
        "เคลือบเล็บได้ไหม": "ได้ค่ะ เคลือบเล็บด้วยเจลใสหรือสีโปร่งใส ราคา 299 บาทค่ะ ✨",
        "แก้ขนตาได้ไหม": "ได้ค่ะ ถ้าใน 7 วันแรกแก้ฟรีนะคะ 💕",
        "ร้านหยุดวันไหน": "ร้านเปิดทุกวันค่ะ ไม่มีวันหยุด 🥰",
        "อยู่โซนไหนของเซ็นทรัล": "อยู่โซนบิวตี้ ชั้น 2 ข้างร้านกาแฟ Cafe Amazon ค่ะ ☕",
        "รับนักเรียนฝึกงานไหม": "ตอนนี้ยังไม่รับฝึกงานค่ะ แต่สามารถฝากประวัติไว้ได้ค่ะ 📋",
        "ต่อเล็บเจลไหม": "มีค่ะ ต่อเล็บเจลราคาเริ่มต้น 899 บาท 💅",
        "มีต่อเล็บอะคริลิคไหม": "มีค่ะ ต่ออะคริลิกเริ่มต้นที่ 999 บาท 💅",
        "ทำสีเล็บได้ไหม": "ได้เลยค่ะ มีให้เลือกกว่า 200 สี 🎨",
        "รับทำเล็บเจ้าสาวไหม": "มีแพ็กเกจเล็บเจ้าสาวพิเศษค่ะ เริ่มต้น 1,299 บาท 💍",
        "ต่อขนตาใช้เวลากี่นาที": "ประมาณ 1 ชั่วโมงค่ะ ⏰",
        "ทำเล็บใช้เวลากี่นาที": "ประมาณ 45 นาที - 1 ชั่วโมงค่ะ ⏰",
        "ร้านใกล้ MRT ไหม": "ใกล้รถไฟฟ้า MRT บางแคค่ะ เดินทางสะดวก 🚇",
        "มีสาขาอื่นไหม": "ตอนนี้มีสาขาเดียวที่เซ็นทรัลพระราม 2 ค่ะ 🏠",
        "รับลูกค้าผู้ชายไหม": "รับค่ะ ยินดีต้อนรับทุกเพศทุกวัยเลย 💕",
        "มีบริการทำสปาไหม": "มีค่ะ สปามือและเท้า ราคาเริ่มต้น 399 บาท 🛁",
        "ต่อขนตาเจ็บไหม": "ไม่เจ็บเลยค่ะ หลับสบายเหมือนนอนพักเลย 😴",
        "ล้างขนตาได้ไหม": "ได้ค่ะ มีบริการล้างขนตา 150 บาท 👁️",
        "ขนตาหลุดเองปกติไหม": "ถ้าหลุดนิดหน่อยภายใน 3 วันถือว่าปกติค่ะ 💖",
        "ใช้เวลาต่อขนตานานไหม": "ประมาณ 1 ชั่วโมงค่ะ ⏱️",
        "ร้านสะอาดไหม": "สะอาดมากค่ะ ฆ่าเชื้อทุกครั้งก่อนบริการ 🧼",
        "มีบริการหลังการขายไหม": "มีค่ะ ภายใน 7 วันแรกแก้ฟรีทุกกรณี 💕",
        "จอดรถตรงไหน": "จอดได้ที่ลานจอดของเซ็นทรัลเลยค่ะ 🚗",
        "รับโอนผ่านพร้อมเพย์ไหม": "รับค่ะ พร้อมเพย์ชื่อร้าน Your Nails 💅",
        "ทำเล็บเจลติดนานไหม": "ประมาณ 3-4 สัปดาห์ค่ะ 💅🏻",
        "ล้างเล็บเจลได้ไหม": "ได้ค่ะ บริการล้างเล็บเจล 100 บาทค่ะ 💅",
        "มีสีเจลให้เลือกไหม": "มีค่ะ มากกว่า 200 สีเลย 🎨",
        "ทำนอกสถานที่ไหม": "ตอนนี้ยังไม่รับนอกสถานที่ค่ะ 🏠",
        "มีส่วนลดไหม": "ลูกค้าเก่าลด 10% ค่ะ ❤️",
        "รับแต้มสมาชิกไหม": "ตอนนี้ยังไม่มีระบบสมาชิกค่ะ แต่มีโปรพิเศษทุกเดือน 🥰",
        "ใช้เวลาทำเล็บเท่าไหร่": "ประมาณ 1 ชั่วโมงค่ะ 💅",
        "ทำเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ นั่งสบาย ๆ 💕",
        "ทำเล็บก่อนงานแต่งได้ไหม": "ได้เลยค่ะ มีแพ็กเกจเจ้าสาวพิเศษ 💍",
        "มีเพจไหม": "มีค่ะ Facebook: Your Nails 💅🏻",
        "มี IG ไหม": "มีค่ะ IG: @your_nails.official 💅",
        "สามารถจองคิวล่วงหน้าได้ไหม": "ได้เลยค่ะ จองได้ล่วงหน้า 1 เดือน 💕",
        "ร้านรับ walk-in ไหม": "รับค่ะ แต่แนะนำจองคิวไว้ก่อนนะคะ 😊",
        "ต่อขนตากี่วันอยู่ได้": "ประมาณ 3-4 สัปดาห์ค่ะ 👁️",
        "มีล้างสปาเท้าไหม": "มีค่ะ ราคาเริ่มต้น 399 บาท 🦶",
        "มีทาสีธรรมดาไหม": "มีค่ะ 199 บาท 💅",
        "ต่อเล็บธรรมชาติไหม": "มีค่ะ 💕",
        "รับเงินสดไหม": "แน่นอนค่ะ รับเงินสดได้เลย 💵",
        "ต่อขนตาล่างไหม": "มีค่ะ เพิ่มเพียง 200 บาท 👁️",
        "ร้านเปิดทุกวันไหม": "ใช่ค่ะ เปิดทุกวัน 10:00 - 20:00 🕗",
        "มี wifi ไหม": "มีค่ะ ฟรี Wi-Fi สำหรับลูกค้าเลย 📶",
        "มีที่นั่งรอไหม": "มีค่ะ โซฟานุ่มสบายเลย 🛋️",
        "บอทชื่ออะไร": "หนูชื่อ Your Nails Bot 💅 ยินดีให้บริการค่ะ 💖",
        "สวัสดี": "สวัสดีค่ะ ยินดีต้อนรับสู่ร้าน Your Nails 💅🏻",
        "ขอบคุณ": "ขอบคุณค่ะ 💕",
        "คิดถึง": "หนูก็คิดถึงค่ะ 😍",
        "ดีจ้า": "ดีจ้า 💕 วันนี้จะทำเล็บแบบไหนดีคะ?",
    }

    user_lower = user_message.lower()
    matched = None
    for q, a in FAQ.items():
        if q in user_lower:
            matched = a
            break

    if matched:
        send_reply(event, matched)
        return
    else:
        reply_text = (
            "พิมพ์:\n"
            "• ส่งยอดขาย ร้าน Your Nails → บันทึกยอดขาย\n"
            "• ยอดเงินสด5/11/68 → บันทึกยอดเงินสด\n"
            "• ยอดเงินวันที่ 6/11/68 → ดูยอดวันนั้น\n"
            "• ยอดเงินรวมเดือน 11 → ดูยอดรวมทั้งเดือน\n"
            "• ยอดเงินรวม → เดือนปัจจุบัน"
        )

    send_reply(event, reply_text)


# ✅ ฟังก์ชันส่งข้อความกลับ
def send_reply(event, text):
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
