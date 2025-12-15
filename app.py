
from flask import Flask, request, abort
import os
import gspread
import base64
import os, json
import difflib
import re
import matplotlib
import unicodedata
import datetime
matplotlib.use('Agg')  # ✅ ปิด GUI mode สำหรับ server
import matplotlib.pyplot as plt

from google.oauth2.service_account import Credentials

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from faq_data import FAQ

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
# LINE SDK config2
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
    user_message = event.message.text.strip()
    today = datetime.date.today()
    thai_year_short = (today.year + 543) % 100


    
   
    # ...existing code....

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS_FILE = 'credentials.json'
    SPREADSHEET_ID = '12WFiY5OpzRsqgagld_pOqSeknaYcWtVv1iKie3JvonY'

    
    today = datetime.date.today()
    thai_year_short = (today.year + 543) % 100

    # ✅ สร้างตัวเชื่อมกับ Google Sheet
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.sheet1
    records = worksheet.get_all_records()

    # -------------------------------------------------
    # ✅ คำนวนคำไกล้เคียง
    # -------------------------------------------------
    def find_closest_question(user_input, faq_dict, cutoff=0.6):
        """
        ค้นหาคำถามใน FAQ ที่คล้ายกับข้อความของผู้ใช้
        cutoff = 0.6 หมายถึงความคล้ายขั้นต่ำ (0-1)
        """
        questions = list(faq_dict.keys())
        matches = difflib.get_close_matches(user_input, questions, n=1, cutoff=cutoff)
        if matches:
            return matches[0]
        return None

    # -------------------------------------------------
    # ✅ ฟีเจอร์สอนบอท: "ถ้าถาม [คำถาม] ให้ตอบ [คำตอบ]"
    # -------------------------------------------------
    teach_match = re.search(r'ถ้าถาม\s+(.+?)\s+ให้ตอบ\s+(.+)', user_message)
    if teach_match:
        teach_q = teach_match.group(1).strip()
        teach_a = teach_match.group(2).strip()
        # เปิด/สร้างชีต FAQ_Sheet
        try:
            faq_sheet = sh.worksheet('FAQ_Sheet')
        except Exception:
            faq_sheet = sh.add_worksheet(title='FAQ_Sheet', rows=100, cols=2)
            faq_sheet.append_row(['question', 'answer'])
        # ตรวจสอบว่ามีคำถามนี้อยู่แล้วหรือยัง
        faq_records = faq_sheet.get_all_records()
        found = False
        for r in faq_records:
            if r.get('question', '').strip() == teach_q:
                found = True
                break
        if not found:
            faq_sheet.append_row([teach_q, teach_a])
            reply_text = f"✅ สอนบอทเรียบร้อย! ถ้าถาม '{teach_q}' จะตอบ '{teach_a}'"
        else:
            reply_text = f"⚠️ มีคำถามนี้ในระบบแล้ว"
        send_reply(event, reply_text)
        return

    # -------------------------------------------------
# ตรวจสอบคำถามที่สอนใน FAQ_Sheet ก่อนตอบ
# -------------------------------------------------
    def normalize_text(text: str) -> str:
        if text is None:
            return ""
        text = unicodedata.normalize("NFC", text)  # รวมสระ/วรรณยุกต์ให้เป็นก้อนเดียว
        text = text.replace("\u200b", "")         # zero-width space
        text = text.replace("\u200c", "")
        text = text.replace("\u200d", "")
        text = text.replace("\ufeff", "")
        return text.strip().lower()
    try:
        faq_sheet = sh.worksheet('FAQ_Sheet')
        faq_records = faq_sheet.get_all_records()
        user_msg_norm = normalize_text(user_message)

        for r in faq_records:
            q_raw = str(r.get('question', ''))
            question_norm = normalize_text(q_raw)

            if question_norm and question_norm in user_msg_norm:
                reply_text = r.get('answer', '')
                send_reply(event, reply_text)
                return

    except Exception:
        pass
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
            date_str = f"{day}/{today.month}/{thai_year_short}"
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
    if re.fullmatch(r'ยอดเงินรวม|ยอด', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return

    if re.fullmatch(r'ยอดเงินเดือนนี้|ยอดรวม|ยอดรวมเดือนนี้', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return
    if re.fullmatch(r'ยอดเดือนนี้', user_message.strip()):
        reply_text = get_month_total(today.month)
        send_reply(event, reply_text)
        return

          # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ยอดเงินชื่อคน” เช่น "ยอดเงินมิน"
    # -------------------------------------------------
    if re.search(r'ยอดเงิน', user_message) and not re.search(r'วันที่|รวม|สด', user_message):
        # รองรับรูปแบบ 'ยอดเงิน<ชื่อ>เดือน <เลขเดือน>'
        match = re.search(r'ยอดเงิน\s*([^\d]+?)(?:เดือน\s*(\d+))?$', user_message)
        if match:
            person_name = match.group(1).strip()
            month_num = match.group(2)
        else:
            person_name = ""
            month_num = None

        if not person_name:
            reply_text = "⚠️ กรุณาระบุชื่อหลังคำว่า 'ยอดเงิน' เช่น 'ยอดเงินมิน'"
            send_reply(event, reply_text)
            return

        # ✅ ค้นหาชื่อในคอลัมน์
        available_names = set()
        for r in records:
            for k in r.keys():
                if k not in ['วันที่', 'date', '', 'ยอดเงินสด']:
                    available_names.add(k.strip())

        # ตรวจสอบชื่อว่าอยู่ใน Sheet ไหม
        found_name = None
        for n in available_names:
            if person_name in n or n in person_name:
                found_name = n
                break

        if not found_name:
            reply_text = f"❌ ไม่พบชื่อ '{person_name}' ในข้อมูลค่ะ\nมีชื่อเหล่านี้: {', '.join(available_names)}"
            send_reply(event, reply_text)
            return

        # ✅ ดึงยอดของคนนั้นทุกวัน (ถ้าไม่ระบุเดือน)
        lines = []
        total = 0
        total_income = 0
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue
            # ถ้าระบุเดือน ให้กรองเฉพาะเดือนนั้น
            if month_num:
                m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
                if not m:
                    continue
                _, m_str, _ = m.groups()
                if int(m_str) != int(month_num):
                    continue
            val = r.get(found_name)
            try:
                num = int(val)
            except:
                num = 0
            if num:
                income = int(num * 0.4)
                if income < 600:
                    income = 600
                lines.append(f"{d} : {num}฿ (รายได้ {income}฿)")
                total += num
                total_income += income

        if not lines:
            if month_num:
                reply_text = f"❌ ไม่พบยอดของ '{found_name}' ในเดือน {month_num} ในชีตค่ะ"
            else:
                reply_text = f"❌ ไม่พบยอดของ '{found_name}' ในชีตค่ะ"
        else:
            if month_num:
                reply_text = f"📊 ยอดของ {found_name} เดือน {month_num}\n" + "\n".join(lines)
            else:
                reply_text = "📊 ยอดของ " + found_name + "\n" + "\n".join(lines)
            reply_text += f"\n\n💰 รวมทั้งหมด: {total}฿"
            reply_text += f"\n💰 รวมรายได้ {total_income}฿"

        send_reply(event, reply_text)
        return
    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี "อันดับ" "อันดับรายได้" "อันดับยอดเงิน"
    # -------------------------------------------------
    if re.fullmatch(r'(อันดับ|อันดับรายได้|อันดับยอดเงิน)', user_message.strip()):
        # สร้าง dict รวมยอดเงินแต่ละคน
        person_totals = {}
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue
            for k, v in r.items():
                if k not in ['วันที่', 'date', '', 'ยอดเงินสด']:
                    try:
                        person_totals[k] = person_totals.get(k, 0) + int(v)
                    except:
                        pass
        # จัดอันดับจากมากไปน้อย
        ranking = sorted(person_totals.items(), key=lambda x: x[1], reverse=True)
        if not ranking:
            reply_text = "❌ ไม่พบข้อมูลยอดเงินของแต่ละคนค่ะ"
        else:
            lines = []
            for name, total in ranking:
                # คำนวณรายได้รวมแบบใหม่
                person_income = 0
                for r in records:
                    d = str(r.get('วันที่') or '').strip()
                    if not d or d == 'รวม':
                        continue
                    val = r.get(name)
                    try:
                        num = int(val)
                    except:
                        num = 0
                    if num:
                        income = int(num * 0.4)
                        if income < 600:
                            income = 600
                        person_income += income
                lines.append(f"{name}: {total} รายได้รวม {person_income}")
            reply_text = "\n".join(lines)
        send_reply(event, reply_text)
        return
      # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “อันดับเดือน X” เช่น "อันดับเดือน 11"
    # -------------------------------------------------
    if re.search(r'อันดับเดือน', user_message):
        month_match = re.search(r'อันดับเดือน\s*(\d+)', user_message)
        if not month_match:
            reply_text = "⚠️ กรุณาระบุเดือน เช่น 'อันดับเดือน 11'"
            send_reply(event, reply_text)
            return

        month_num = int(month_match.group(1))

        # ✅ รวมยอดเฉพาะเดือนนั้น
        person_totals = {}
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue

            # ดึงเลขเดือนจากวันที่
            m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
            if not m:
                continue
            _, m_str, _ = m.groups()
            if int(m_str) != month_num:
                continue  # ข้ามถ้าไม่ตรงเดือน

            # รวมยอดรายชื่อ
            for k, v in r.items():
                if k not in ['วันที่', 'date', '', 'ยอดเงินสด']:
                    try:
                        person_totals[k] = person_totals.get(k, 0) + int(v)
                    except:
                        pass

        if not person_totals:
            reply_text = f"❌ ไม่พบข้อมูลของเดือน {month_num}"
            send_reply(event, reply_text)
            return

        # ✅ จัดอันดับมากไปน้อย
        ranking = sorted(person_totals.items(), key=lambda x: x[1], reverse=True)
        lines = [f"🏆 อันดับรายได้เดือน {month_num}"]
        for i, (name, total) in enumerate(ranking, start=1):
            # คำนวณรายได้รวมแบบใหม่ เฉพาะเดือนนั้น
            person_income = 0
            for r in records:
                d = str(r.get('วันที่') or '').strip()
                if not d or d == 'รวม':
                    continue
                m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
                if not m:
                    continue
                _, m_str, _ = m.groups()
                if int(m_str) != month_num:
                    continue
                val = r.get(name)
                try:
                    num = int(val)
                except:
                    num = 0
                if num:
                    income = int(num * 0.4)
                    if income < 600:
                        income = 600
                    person_income += income
            lines.append(f"{i}. {name}: {total}฿ (รายได้ {person_income}฿)")

        reply_text = "\n".join(lines)
        send_reply(event, reply_text)
        return
    # -------------------------------------------------
    # ✅ กราฟอันดับรวมทั้งหมด
    # -------------------------------------------------
    if re.fullmatch(r'(กราฟอันดับ|กราฟอันดับรวม)', user_message.strip()):
        person_totals = {}
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue
            for k, v in r.items():
                if k not in ['วันที่', 'date', '', 'ยอดเงินสด']:
                    try:
                        person_totals[k] = person_totals.get(k, 0) + int(v)
                    except:
                        pass

        if not person_totals:
            reply_text = "❌ ไม่มีข้อมูลยอดรายชื่อ"
            send_reply(event, reply_text)
            return

        chart_path = generate_rank_chart(person_totals, "กราฟอันดับรวมทั้งหมด", "rank_all.png")
        full_url = request.url_root + chart_path.replace('\\', '/')
        reply_text = f"📊 กราฟอันดับรวมทั้งหมด\n{full_url}"
        send_reply(event, reply_text)
        return
    # -------------------------------------------------
    # ✅ กราฟอันดับรายเดือน
    # -------------------------------------------------
    if re.search(r'กราฟอันดับเดือน', user_message):
        month_match = re.search(r'กราฟอันดับเดือน\s*(\d+)', user_message)
        if not month_match:
            reply_text = "⚠️ กรุณาระบุเดือน เช่น 'กราฟอันดับเดือน 11'"
            send_reply(event, reply_text)
            return

        month_num = int(month_match.group(1))
        person_totals = {}
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue

            m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
            if not m:
                continue
            _, m_str, _ = m.groups()
            if int(m_str) != month_num:
                continue

            for k, v in r.items():
                if k not in ['วันที่', 'date', '', 'ยอดเงินสด']:
                    try:
                        person_totals[k] = person_totals.get(k, 0) + int(v)
                    except:
                        pass

        if not person_totals:
            reply_text = f"❌ ไม่พบข้อมูลเดือน {month_num}"
            send_reply(event, reply_text)
            return

        chart_path = generate_rank_chart(person_totals, f"กราฟอันดับเดือน {month_num}", f"rank_month_{month_num}.png")
        full_url = request.url_root + chart_path.replace('\\', '/')
        reply_text = f"📊 กราฟอันดับเดือน {month_num}\n{full_url}"
        send_reply(event, reply_text)
        return
     # -------------------------------------------------
    # ✅ เพิ่มฟังก์ชันเก็บยอดทิป เช่น "ส่งยอดทิป 100"
    # -------------------------------------------------
    # -------------------------------------------------
    # ✅ ฟังก์ชันบันทึกยอดทิป (ทั้งวันปัจจุบันและวันที่ระบุ)
    # -------------------------------------------------
    if re.search(r'ส่งยอดทิป', user_message):

        # 🔍 ตรวจว่ามีระบุวันที่ไหม เช่น "ส่งยอดทิป 11/11/68" หรือ "ส่งยอดทิป11/11/68 200"
        date_match = re.search(r'ส่งยอดทิป\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})', user_message)
        amount_match = re.search(r'(\d+)\s*$', user_message.strip())

        if date_match:
            date_str = date_match.group(1).replace("-", "/").strip()
        else:
            # ถ้าไม่ระบุวันที่ → ใช้วันที่วันนี้
            date_str = f"{today.day:02d}/{today.month:02d}/{thai_year_short:02d}"
        # ปรับวันที่ให้เป็น 2 หลักเสมอ เช่น 01/11/68
        parts = date_str.split("/")
        if len(parts) == 3:
            day, month, year = parts
            date_str = f"{int(day):02d}/{int(month):02d}/{year}"

        if not amount_match:
            reply_text = "⚠️ กรุณาระบุจำนวนทิป เช่น 'ส่งยอดทิป 100' หรือ 'ส่งยอดทิป 11/11/68 200'"
            send_reply(event, reply_text)
            return

        tip_amount = int(amount_match.group(1))

        # ✅ ดึงข้อมูลทั้งหมดจากชีต
        all_values = worksheet.get_all_values()
        found_row = None

        # ✅ หาว่ามีแถวของวันนั้นหรือยัง
        for i, row in enumerate(all_values):
            if len(row) > 0 and str(row[0]).strip() == date_str:
                found_row = i + 1
                break

        # ✅ ถ้ายังไม่มีคอลัมน์ทิป → สร้าง
        header = all_values[0] if all_values else []
        if "ทิป" not in header:
            worksheet.update_cell(1, len(header) + 1, "ทิป")
            header.append("ทิป")
        tip_col = header.index("ทิป") + 1

        # ✅ บันทึกทิป
        if found_row:
            # ถ้ามีอยู่แล้ว → บวกเพิ่มยอดทิปเดิม
            current_value = worksheet.cell(found_row, tip_col).value
            try:
                new_value = int(current_value or 0) + tip_amount
            except:
                new_value = tip_amount
            worksheet.update_cell(found_row, tip_col, new_value)
        else:
            # ถ้ายังไม่มีแถวของวันนั้น → เพิ่มใหม่
            new_row = [date_str]
            while len(new_row) < len(header):
                new_row.append("")
            new_row[tip_col - 1] = str(tip_amount)
            worksheet.append_row(new_row)

        reply_text = f"💰 บันทึกยอดทิป {tip_amount}฿ สำหรับวันที่ {date_str} เรียบร้อยแล้ว!"
        send_reply(event, reply_text)
        return


    # -------------------------------------------------
    # ✅ เรียกดูยอดทิปทั้งหมด
    # -------------------------------------------------
    if re.fullmatch(r'ยอดทิป', user_message.strip()):
        total_tip = 0
        for r in records:
            val = r.get('ทิป')
            try:
                total_tip += int(val)
            except:
                pass
        reply_text = f"💸 ยอดทิปทั้งหมด: {total_tip}฿"
        send_reply(event, reply_text)
        return


    # -------------------------------------------------
    # ✅ เรียกดูยอดทิปเฉพาะเดือน เช่น “ยอดทิปเดือน 11”
    # -------------------------------------------------
    if re.search(r'ยอดทิปเดือน', user_message):
        month_match = re.search(r'ยอดทิปเดือน\s*(\d+)', user_message)
        if not month_match:
            reply_text = "⚠️ กรุณาระบุเดือน เช่น 'ยอดทิปเดือน 11'"
            send_reply(event, reply_text)
            return

        month_num = int(month_match.group(1))
        total_tip = 0

        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
                continue
            m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', d)
            if not m:
                continue
            _, m_str, _ = m.groups()
            if int(m_str) != month_num:
                continue
            val = r.get('ทิป')
            try:
                total_tip += int(val)
            except:
                pass

        reply_text = f"💸 ยอดทิปเดือน {month_num}: {total_tip}฿"
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
            parts = date_str.split('/')
            if len(parts) == 2:
                thai_year = str(datetime.datetime.now().year + 543)[-2:]
                date_str = f"{int(parts[0]):02d}/{int(parts[1]):02d}/{thai_year}"
            elif len(parts) == 3:
                day, month, year = parts
                date_str = f"{int(day):02d}/{int(month):02d}/{year}"
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

        # รองรับ "วันที่ 10/12/68", "วันที่ 10.12.68", "วันที่ 10"
        today = datetime.date.today()
        thai_year_short = (today.year + 543) % 100
        date_match = re.search(r'วันที่\s*[🎉\s]*([\d]{1,2}(?:[/.]\d{1,2})?(?:[/.]\d{2,4})?)', user_message)
        if not date_match:
            reply_text = "กรุณาระบุวันที่ เช่น 🎉วันที่ 6/11/68 หรือ วันที่ 10"
        else:
            raw_date = date_match.group(1).strip()
            if re.fullmatch(r'\d{1,2}', raw_date):
                # ถ้าเป็นแค่ตัวเลข เช่น "10" ให้เติมเดือนและปีปัจจุบัน
                date_str = f"{int(raw_date):02d}/{today.month:02d}/{thai_year_short:02d}"
            else:
                # แปลง . เป็น / เพื่อให้ format เดียวกัน
                date_str = raw_date.replace('.', '/')
                # ปรับวันที่ให้เป็น 2 หลักเสมอ เช่น 01/11/68
                parts = date_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    date_str = f"{int(day):02d}/{int(month):02d}/{year}"
            lines = user_message.splitlines()
            # --- กำหนด mapping ชื่อหลัก ---
            name_aliases = {
                "เป๊ปซี่": ["เป๊ปซี่", "เป๊ปชี่", "เป๊ป","pepsi","Pepsi"],
                "อีฟ": ["อีฟ"]
                # เพิ่มชื่ออื่น ๆ ได้ตามต้องการ
            }

            def normalize_name(name):
                for main, aliases in name_aliases.items():
                    for alias in aliases:
                        if alias in name:
                            return main
                # กรณีชื่อมีคำว่า "อีฟ" อยู่ที่ไหนก็ได้
                if "อีฟ" in name:
                    return "อีฟ"
                return name

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
                    normalized = normalize_name(line)
                    current_person = normalized
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
            send_reply(event, reply_text)
            return

    # -------------------------------------------------
    # ✅ ตรวจสอบกรณี “ลบข้อมูลชื่อคน” เช่น "ลบข้อมูลอีฟ"
    # -------------------------------------------------
    if re.search(r'^ลบข้อมูล', user_message):
        name_match = re.search(r'ลบข้อมูล\s*(.+)', user_message)
        if not name_match:
            reply_text = "⚠️ กรุณาระบุชื่อพนักงานที่ต้องการลบ เช่น 'ลบข้อมูลอีฟ'"
            send_reply(event, reply_text)
            return

        person_name = name_match.group(1).strip()
        if not person_name:
            reply_text = "⚠️ กรุณาระบุชื่อพนักงาน เช่น 'ลบข้อมูลมิน'"
            send_reply(event, reply_text)
            return

        # ✅ โหลดข้อมูลทั้งหมดจากชีต
        all_data = worksheet.get_all_values()
        if not all_data:
            reply_text = "❌ ไม่พบข้อมูลในชีต"
            send_reply(event, reply_text)
            return

        header = all_data[0]
        if person_name not in header:
            reply_text = f"❌ ไม่พบชื่อ '{person_name}' ในชีตค่ะ"
            send_reply(event, reply_text)
            return

        # ✅ หา index ของคอลัมน์ที่จะลบ
        idx = header.index(person_name)

        # ✅ ลบคอลัมน์นั้นออกจากทุกแถว
        new_data = []
        for row in all_data:
            new_row = [v for i, v in enumerate(row) if i != idx]
            new_data.append(new_row)

        # ✅ เขียนกลับไปที่ชีตใหม่
        worksheet.clear()
        worksheet.append_rows(new_data)

        reply_text = f"🗑️ ลบข้อมูลทั้งหมดของ '{person_name}' ออกจากชีตเรียบร้อยแล้วค่ะ!"
        send_reply(event, reply_text)
        return

    if user_message in FAQ:
        reply_text = FAQ[user_message]
        send_reply(event, reply_text)
        return
    closest = find_closest_question(user_message, FAQ)
    if closest:
        reply_text = FAQ[closest]
        send_reply(event, reply_text)
        return

    # --- เพิ่มตัวนับจำนวนครั้งที่ไม่เข้าใจ (per user) ---
    # ใช้ Google Sheet ในการเก็บ count ต่อ user_id (หรือ user display name ถ้าไม่มี user_id)
    user_id = getattr(event.source, 'user_id', None) or getattr(event.source, 'userId', None) or getattr(event.source, 'user', None) or 'unknown'
    try:
        # เปิด/สร้างชีตชื่อ 'Unknown_Count'
        try:
            count_sheet = sh.worksheet('Unknown_Count')
        except Exception:
            count_sheet = sh.add_worksheet(title='Unknown_Count', rows=100, cols=2)
            count_sheet.append_row(['user_id', 'count'])
        count_records = count_sheet.get_all_records()
        found = False
        for idx, r in enumerate(count_records, start=2):
            if r.get('user_id') == user_id:
                found = True
                count = int(r.get('count', 0)) + 1
                count_sheet.update_cell(idx, 2, count)
                break
        if not found:
            count = 1
            count_sheet.append_row([user_id, count])
            idx = len(count_records) + 2
        # ตอบกลับตามจำนวนครั้ง
        if count < 5:
            reply_text = "ขอโทษค่ะ หนูไม่เข้าใจคำถาม"
            send_reply(event, reply_text)
            return
        if count == 5:
            reply_text = (
                "ขอโทษค่ะ หนูไม่เข้าใจคำถาม ลองพิมพ์ใหม่อีกครั้งได้นะคะ 💕\n"
                "พิมพ์:\n"
                "• ส่งยอดขาย ร้าน Your Nails → บันทึกยอดขาย\n"
                "• ยอดเงินสด5/11/68 → บันทึกยอดเงินสด\n"
                "• ยอดเงินวันที่ 6/11/68 → ดูยอดวันนั้น\n"
                "• ยอดเงินรวมเดือน 11 → ดูยอดรวมทั้งเดือน\n"
                "• ยอดเงินรวม → เดือนปัจจุบัน\n"
                "• ยอดเงินมิน → ยอดเงินของมิน"
            )
            send_reply(event, reply_text)
            # reset count
            count_sheet.update_cell(idx, 2, 0)
            return
        if count > 5:
            count_sheet.update_cell(idx, 2, 1)
            return
    except Exception:
        # ถ้า error ในการนับ ให้ตอบแบบเดิม
        reply_text = (
            "ขอโทษค่ะ หนูไม่เข้าใจคำถาม ลองพิมพ์ใหม่อีกครั้งได้นะคะ 💕\n"
            "พิมพ์:\n"
            "• ส่งยอดขาย ร้าน Your Nails → บันทึกยอดขาย\n"
            "• ยอดเงินสด5/11/68 → บันทึกยอดเงินสด\n"
            "• ยอดเงินวันที่ 6/11/68 → ดูยอดวันนั้น\n"
            "• ยอดเงินรวมเดือน 11 → ดูยอดรวมทั้งเดือน\n"
            "• ยอดเงินรวม → เดือนปัจจุบัน\n"
            "• ยอดเงินมิน → ยอดเงินของมิน"
        )
        send_reply(event, reply_text)

# ✅ ฟังก์ชันสร้างกราฟอันดับ
def generate_rank_chart(person_totals, title, filename):
    if not os.path.exists('static'):
        os.makedirs('static')

    names = list(person_totals.keys())
    totals = list(person_totals.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(names, totals)
    plt.title(title)
    plt.xlabel('ชื่อพนักงาน')
    plt.ylabel('ยอดรวม (บาท)')
    plt.xticks(rotation=30, ha='right')

    # เพิ่ม label บนกราฟ
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9)

    path = os.path.join('static', filename)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path

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
