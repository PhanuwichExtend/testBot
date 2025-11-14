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
    user_message = event.message.text.strip()
    today = datetime.date.today()
    thai_year_short = (today.year + 543) % 100


    
   
    # ...existing code...

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
        # ดึงชื่อหลังคำว่า 'ยอดเงิน'
        name_match = re.search(r'ยอดเงิน\s*(.+)', user_message)
        if name_match:
            person_name = name_match.group(1).strip()
        else:
            person_name = ""

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

        # ✅ ดึงยอดของคนนั้นทุกวัน
        lines = []
        total = 0
        total_income = 0
        for r in records:
            d = str(r.get('วันที่') or '').strip()
            if not d or d == 'รวม':
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
            reply_text = f"❌ ไม่พบยอดของ '{found_name}' ในชีตค่ะ"
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

        date_match = re.search(r'วันที่\s*[🎉\s]*([\d/]+)', user_message)
        if not date_match:
            reply_text = "กรุณาระบุวันที่ เช่น 🎉วันที่ 6/11/68"
        else:
            date_str = date_match.group(1).strip()
            # ปรับวันที่ให้เป็น 2 หลักเสมอ เช่น 01/11/68
            parts = date_str.split("/")
            if len(parts) == 3:
                day, month, year = parts
                date_str = f"{int(day):02d}/{int(month):02d}/{year}"
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
            send_reply(event, reply_text)
            return
    FAQ = {
    
    
        "ร้านอยู่ที่ไหน": "แฟชั่นไอซ์แลน ค่ะ 💅",
        "ร้านเปิดกี่โมง": "ร้านเปิดทุกวัน 10:00 - 20:00 น. ค่ะ 💕",
        "ร้านปิดกี่โมง": "ร้านปิดเวลา 20:00 น. ทุกวันค่ะ 🕗",
        "เบอร์โทร": "สามารถติดต่อร้านได้ที่ เบอร์...... 📞",
        "ต่อขนตากี่บาท": "ตอนนี้ยังไม่มีบริการนี้ค่ะ 😍",
        "ทำเล็บกี่บาท": "ทำเล็บเริ่มต้นที่ 299 บาทค่ะ 💅🏻",
        "ล้างเล็บเท่าไหร่": "ล้างเล็บ 100 บาทค่ะ",
        "มีต่อเล็บไหม": "มีค่ะ ต่อเล็บอะคริลิกและเจล ราคาเริ่มต้น 899 บาท 💅",
        "รับบัตรเครดิตไหม": "รับบัตรเครดิตทุกธนาคารค่ะ 💳",
        "มีที่จอดรถไหม": "มีที่จอดรถที่ศูนย์การค้าค่ะ 🚗",
        "ร้านชื่ออะไร": "ร้านชื่อ Your Nails 💅🏻 ค่ะ",
        "ขนตาร่วงทำไง": "ทำใจค่ะ เอ้ย ไม่ต้องกังวลนะคะ ถ้าขนตาร่วงใน 7 วันแรกสามารถเข้ามาแก้ฟรีค่ะ 💖",
        "ทำผมไหม": "ขณะนี้รับเฉพาะทำเล็บและต่อขนตาค่ะ 💅",
        "โปรโมชั่น": "ตอนนี้มีโปรต่อขนตา 599 บาท จาก 799 บาท ถึงสิ้นเดือนนี้เท่านั้น 🎉",
        "นัดหมายยังไง": "สามารถจองคิวผ่าน LINE นี้ได้เลยค่ะ หรือโทร ....... ☎️",
        "จองคิวได้ไหม": "ได้เลยค่ะ พิมพ์วันที่และเวลาที่ต้องการมาได้เลย 💕",
        "มีต่อขนตาแบบไหนบ้าง": "เรามีต่อแบบธรรมชาติ ฟูวิ้ง และวอลลุ่มค่ะ 😍",
        "รับบัตรสวัสดิการไหม": "ขออภัยค่ะ ยังไม่รับบัตรสวัสดิการแห่งรัฐนะคะ",
        "รับโอนผ่านแอปไหม": "ได้ค่ะ รับทุกธนาคารผ่าน QR พร้อมเพย์เลย 💸",
    "วันนี้วันอะไร": f"วันนี้คือวัน{today.strftime('%A')} ที่ {today.day}/{today.month}/{thai_year_short} ค่ะ 📅",
        "ใครเป็นเจ้าของร้าน": "เจ้าของร้านคือพี่เมย์คนสวยค่ะ 💖",
        "ทำเล็บเท้าไหม": "มีค่ะ ทำเล็บเท้าเริ่มต้นที่ 350 บาท 👣",
        "ทาสีเจลไหม": "มีค่ะ ทาสีเจลเริ่มต้น 399 บาท 💅",
        "เคลือบเล็บได้ไหม": "ได้ค่ะ เคลือบเล็บด้วยเจลใสหรือสีโปร่งใส ราคา 299 บาทค่ะ ✨",
        "แก้ขนตาได้ไหม": "ได้ค่ะ ถ้าใน 7 วันแรกแก้ฟรีนะคะ 💕",
        "ร้านหยุดวันไหน": "ร้านเปิดทุกวันค่ะ ไม่มีวันหยุด 🥰",
        "อยู่โซนไหนของเซ็นทรัล": "อยู่โซนบิวตี้ ชั้น ที่มีรถไฟค่ะ ☕",
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
        "ทำเล็บราคาเท่าไหร่": "ทำเล็บเริ่มต้น 299 บาทค่ะ 💅🏻",
    "ต่อขนตาราคาเท่าไหร่": "ต่อขนตาเริ่มต้น 599 บาทค่ะ 👁️",
    "ทำเล็บเท้าเท่าไหร่": "ทำเล็บเท้าเริ่มต้น 350 บาทค่ะ 👣",
    "สปามือราคาเท่าไหร่": "สปามือเริ่มต้น 399 บาทค่ะ 🖐️",
    "สปาเท้าเท่าไหร่": "สปาเท้าเริ่มต้น 399 บาทค่ะ 🦶",
    "มีต่อเล็บเจลไหม": "มีค่ะ ต่อเล็บเจลราคาเริ่มต้น 899 บาท 💅",
    "มีต่อเล็บอะคริลิคไหม": "มีค่ะ ต่อเล็บอะคริลิกเริ่มต้นที่ 999 บาท 💅",
    "ต่อเล็บใช้เวลานานไหม": "ประมาณ 1 ชั่วโมงครึ่งค่ะ 💅",
    "ทำเล็บใช้เวลานานไหม": "ประมาณ 45 นาทีถึง 1 ชั่วโมงค่ะ ⏰",
    "ต่อขนตาใช้เวลานานไหม": "ประมาณ 1 ชั่วโมงค่ะ 👁️",
    "ทำเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ สบายมาก 💕",
    "ต่อขนตาเจ็บไหม": "ไม่เจ็บเลยค่ะ หลับได้สบาย 😴",
    "ทำขนตาแล้วอาบน้ำได้ไหม": "ได้ค่ะ แต่แนะนำรอ 24 ชั่วโมงก่อนนะคะ 🚿",
    "ทำเล็บก่อนแต่งงานได้ไหม": "ได้เลยค่ะ มีแพ็กเกจเจ้าสาวพิเศษ 💍",
    "รับคิวด่วนไหม": "รับค่ะ ถ้าช่างว่างสามารถทำได้เลย 💅",
    "วันนี้มีคิวว่างไหม": "รบกวนแจ้งเวลาที่ต้องการค่ะ จะเช็คให้เลย 💕",
    "คิวยาวไหม": "แล้วแต่ช่วงเวลาค่ะ แนะนำจองล่วงหน้าจะได้ไม่ต้องรอนะคะ ☺️",
    "มีทาสีธรรมดาไหม": "มีค่ะ ราคาเริ่มต้น 199 บาท 💅",
    "มีทาสีเจลไหม": "มีค่ะ ราคาเริ่มต้น 399 บาท 💅🏻",
    "มีเคลือบเล็บไหม": "มีค่ะ เคลือบใสหรือสีโปร่งใส 299 บาท ✨",
    "ทำเล็บสีอะไรสวย": "สีพาสเทลกับโทนชมพูนู้ดกำลังฮิตเลยค่ะ 💖",
    "แนะนำสีเล็บหน่อย": "สีชมพูนู้ด, มิลค์ที, หรือครีมเบจสวยมากเลยค่ะ 💅",
    "ต่อเล็บสั้นได้ไหม": "ได้ค่ะ ปรับความยาวได้ตามต้องการเลย 💕",
    "ต่อเล็บยาวได้ไหม": "ได้ค่ะ สูงสุดประมาณ 1 นิ้วเลย 💅",
    "ต่อขนตาฟูไหม": "เลือกได้เลยค่ะ จะฟูหรือธรรมชาติก็ได้ 😍",
    "ขนตาหลุดเร็วทำไง": "มาฟรีทัชอัพได้ใน 7 วันค่ะ 💖",
    "แก้ขนตาได้ไหม": "ได้ค่ะ ภายใน 7 วันแก้ฟรีค่ะ 💕",
    "ล้างเล็บเจลไหม": "มีค่ะ 100 บาทค่ะ 💅",
    "รับโอนเงินไหม": "รับค่ะ ทุกธนาคารหรือพร้อมเพย์ก็ได้ 💸",
    "รับเงินสดไหม": "แน่นอนค่ะ 💵",
    "รับบัตรเครดิตไหม": "รับค่ะ 💳",
    "มีส่วนลดไหม": "มีค่ะ ลูกค้าเก่าลด 10% ❤️",
    "มีโปรไหม": "ตอนนี้มีโปรต่อขนตา 599 บาท จาก 799 บาท 🎉",
    "มีบริการอะไรบ้าง": "ต่อขนตา ทำเล็บ สปามือเท้า เคลือบเล็บ ต่อเล็บ 💅",
    "ทำเล็บพร้อมขนตาได้ไหม": "ได้เลยค่ะ ทำคู่กันประหยัดเวลา 💕",
    "รับแต่งเล็บลายพิเศษไหม": "รับค่ะ มีลายแฟชั่นมากกว่า 200 แบบ 🎨",
    "มีลายเล็บเจ้าสาวไหม": "มีค่ะ ลายพิเศษเฉพาะเจ้าสาว 💍",
    "รับทำเล็บคู่เพื่อนได้ไหม": "ได้เลยค่ะ นั่งคู่กันได้เลย 💕",
    "รับ walk in ไหม": "รับค่ะ แต่แนะนำจองก่อนนะคะ 😊",
    "ร้านปิดวันไหน": "ร้านเปิดทุกวันค่ะ ไม่มีวันหยุด 🕗",
    "ร้านอยู่ชั้นไหน": "อยู่ชั้น 2 ของแฟชั่นไอส์แลนด์ค่ะ 💅",
    "เดินทางยังไง": "อยู่ติดบันไดเลื่อนฝั่ง Cafe Amazon ค่ะ 🚶‍♀️",
    "จอดรถได้ที่ไหน": "ที่จอดรถชั้นล่างของศูนย์การค้าเลยค่ะ 🚗",
    "มีที่นั่งรอไหม": "มีค่ะ โซฟานุ่มสบายเลย 🛋️",
    "ร้านมีห้องน้ำไหม": "มีค่ะ อยู่ใกล้ร้านเลย 🚻",
    "มีอาหารไหม": "ไม่มีค่ะ แต่ใกล้ร้านมีคาเฟ่หลายร้าน 🍹",
    "วันนี้ร้านเปิดไหม": "เปิดค่ะ เปิดทุกวัน 10:00 - 20:00 น. 💕",
    "วันนี้มีโปรไหม": "ตอนนี้มีโปรต่อขนตา 599 บาท จาก 799 บาทค่ะ 🎉",
    "วันนี้มีคิวว่างไหม": "มีค่ะ แจ้งเวลาที่สะดวกมาได้เลย เดี๋ยวเช็คให้ 💖",
    "ร้านเปิดกี่โมงวันนี้": "เปิด 10 โมงเช้าค่ะ 💅",
    "ร้านปิดกี่โมงวันนี้": "ปิด 2 ทุ่มค่ะ 🕗",
    "ถ้ามาสายทำได้ไหม": "ได้ค่ะ แต่แจ้งล่วงหน้าหน่อยนะคะ 💕",
    "มาช้าได้ไหม": "ได้ค่ะ แต่หากเกิน 15 นาทีอาจต้องรอคิวใหม่ค่ะ ⏰",
    "อยากยกเลิกคิว": "แจ้งชื่อและเวลาที่จองไว้ได้เลยค่ะ เดี๋ยวบันทึกให้ 💖",
    "จองคิวใหม่ได้ไหม": "ได้เลยค่ะ แจ้งวันและเวลาที่ต้องการได้เลย 💅",
    "แก้เล็บได้ไหม": "ได้ค่ะ ถ้าใน 7 วันแรกแก้ฟรีเลย 💕",
    "เล็บหลุดทำไงดี": "นำมาที่ร้านได้เลยค่ะ แก้ให้ฟรีภายใน 7 วัน 💅",
    "เล็บพังทำไงดี": "ไม่ต้องกังวลนะคะ มาซ่อมได้เลย 💕",
    "ต่อเล็บพังได้ไหม": "ได้ค่ะ เราซ่อมให้ได้ทุกแบบ 💪",
    "ทาเล็บเองแล้วพังแก้ได้ไหม": "ได้ค่ะ เดี๋ยวช่างดูให้ว่าต้องล้างหรือซ่อม 💅",
    "ต่อเล็บธรรมชาติมีไหม": "มีค่ะ เรียบหรู ดูเป็นธรรมชาติ 💖",
    "ต่อเล็บสั้นแบบน่ารักมีไหม": "มีค่ะ ลายมินิมอลน่ารักสุด ๆ 💅🏻",
    "ต่อเล็บใสได้ไหม": "ได้ค่ะ ใสสะอาดดูแพง ✨",
    "ต่อเล็บทำสีได้ไหม": "ได้เลยค่ะ จะทาเจลหรือตกแต่งเพิ่มก็ได้ 🎨",
    "ต่อขนตาแบบธรรมชาติไหม": "มีค่ะ สไตล์ฟูเบาเป็นธรรมชาติ 👁️",
    "ต่อขนตาแบบหนาได้ไหม": "ได้ค่ะ เลือกได้ทั้งหนาและวอลลุ่ม 💖",
    "ต่อขนตาแบบเกาหลีได้ไหม": "ได้ค่ะ ตอนนี้กำลังฮิตเลย 🩷",
    "ต่อขนตาแบบญี่ปุ่นมีไหม": "มีค่ะ ใช้เส้นไหมคุณภาพดีจากญี่ปุ่นเลย 👁️",
    "ขนตาแบบไหนดี": "แนะนำแบบฟูวิ้งดูหวาน หรือวอลลุ่มดูชัดค่ะ 😍",
    "อยากได้ลุคธรรมชาติ": "แนะนำต่อแบบ classic ค่ะ สวยกำลังดี 💕",
    "อยากได้ลุคเซ็กซี่": "ลองต่อแบบ doll หรือ cat eye ดูค่ะ 👁️‍🗨️",
    "อยากได้ขนตาฟู": "แนะนำแบบวอลลุ่มเลยค่ะ ฟูสวยสะพรึง 😍",
    "อยากได้ขนตาเบาๆ": "แบบ classic เหมาะสุดเลยค่ะ 💕",
    "ต่อขนตาแล้วล้างหน้าได้ไหม": "ได้ค่ะ แต่หลีกเลี่ยงน้ำ 24 ชม.แรกนะคะ 💧",
    "ต่อขนตาแล้วว่ายน้ำได้ไหม": "ได้ค่ะ หลังจาก 24 ชม. ไปแล้ว 🏊‍♀️",
    "ขนตาอยู่ได้นานไหม": "อยู่ได้ประมาณ 3-4 สัปดาห์ค่ะ 👁️",
    "ต่อขนตาต้องดูแลยังไง": "อย่าขยี้ตา หลีกเลี่ยงน้ำมัน และแปรงขนตาเบา ๆ ค่ะ 💕",
    "ต่อขนตาแล้วแต่งหน้าได้ไหม": "ได้ค่ะ แต่ควรใช้เครื่องสำอางสูตรน้ำ 💄",
    "ต่อขนตาแล้วล้างออกเองได้ไหม": "ไม่แนะนำค่ะ ควรให้ช่างล้างให้ 💅",
    "ทำเล็บแล้วอาบน้ำได้ไหม": "ได้ค่ะ แต่ระวังตอนใหม่ ๆ นิดนึงนะคะ 💧",
    "ทำเล็บแล้วอยู่ได้นานไหม": "อยู่ได้ประมาณ 3-4 สัปดาห์ค่ะ 💅",
    "ทาเจลติดนานไหม": "ประมาณ 3 สัปดาห์ขึ้นไปค่ะ ✨",
    "ล้างเจลที่บ้านได้ไหม": "ไม่แนะนำค่ะ เดี๋ยวหน้าเล็บพัง 😢",
    "ควรล้างเล็บบ่อยไหม": "ทุก 3-4 สัปดาห์กำลังดีค่ะ 💅",
    "ล้างเล็บที่ร้านใช้เวลานานไหม": "ประมาณ 15 นาทีค่ะ ⏱️",
    "ร้านสะอาดไหม": "สะอาดมากค่ะ ฆ่าเชื้อทุกครั้ง 🧼",
    "ช่างเป็นมืออาชีพไหม": "ทุกคนผ่านการอบรมค่ะ 💪",
    "ช่างใจดีไหม": "ใจดีทุกคนเลยค่ะ 🥰",
    "มีช่างผู้หญิงไหม": "มีค่ะ ทั้งหมดเป็นช่างผู้หญิง 💅",
    "ร้านมี Wi-Fi ไหม": "มีค่ะ ฟรีสำหรับลูกค้าเลย 📶",
    "ร้านรับบัตรกำนัลไหม": "ถ้าเป็นของห้างสามารถใช้ได้ค่ะ 🎁",
    "รับคูปองส่วนลดไหม": "รับค่ะ ถ้าเป็นของร้านเรา 💕",
    "ต่อเล็บกี่วันเสร็จ": "วันเดียวจบเลยค่ะ 💅",
    "ต่อขนตากี่วันเสร็จ": "ทำเสร็จภายใน 1 ชั่วโมงค่ะ 👁️",
    "ต่อเล็บใช้กาวไหม": "ใช่ค่ะ ใช้กาวเจลเฉพาะทาง ปลอดภัยแน่นอน 💅",
    "ขนตาใช้กาวแบบไหน": "กาวต่อขนตาเกรดพรีเมียม ไม่ระคายเคืองค่ะ 👁️",
    "ใช้ผลิตภัณฑ์แบรนด์อะไร": "ใช้แบรนด์ญี่ปุ่นและเกาหลีทั้งหมดค่ะ 🇯🇵🇰🇷",
    "อุปกรณ์ปลอดภัยไหม": "ฆ่าเชื้อทุกชิ้นก่อนใช้งานค่ะ 🧼",
    "เด็กทำเล็บได้ไหม": "ได้ค่ะ สีปลอดภัย ไม่มีสารเคมีแรง 💕",
    "ผู้ชายทำได้ไหม": "ได้เลยค่ะ ยินดีต้อนรับทุกเพศ 💅",
    "ทำเล็บคู่แฟนได้ไหม": "ได้เลยค่ะ คู่รักมาบ่อยเลย 💞",
    "รับทำเล็บกลิตเตอร์ไหม": "มีค่ะ กลิตเตอร์เพียบเลย ✨",
    "รับทำเล็บลายการ์ตูนไหม": "มีค่ะ ลายน่ารักสุด ๆ 🎨",
    "ต่อเล็บปลายขาวได้ไหม": "ได้ค่ะ เรียกว่า French Nail 💅🏻",
    "ต่อเล็บปลายใสได้ไหม": "ได้เลยค่ะ ใสหรูดูแพง 💖",
    "รับแต่งเล็บลายพิเศษไหม": "มีค่ะ ทั้งเพนต์และติดเพชร 💎",
    "ติดเพชรบนเล็บได้ไหม": "ได้เลยค่ะ มีหลายขนาดให้เลือก 💍",
    "มีเล็บแม่เหล็กไหม": "มีค่ะ สีแม่เหล็กสวยมาก 🧲",
    "มีเล็บมุกไหม": "มีค่ะ สีมุกเงาๆ กำลังฮิต 💅",
    "มีเล็บเรืองแสงไหม": "มีค่ะ เหมาะสำหรับสายปาร์ตี้ 🌈",
    "ล้างขนตาใช้เวลานานไหม": "ประมาณ 15 นาทีค่ะ 👁️",
    "ต่อขนตาใหม่ใช้เวลานานไหม": "ประมาณ 1 ชั่วโมงค่ะ ⏰",
    "เติมขนตาใช้เวลานานไหม": "ประมาณ 45 นาทีค่ะ 💕",
    "เติมขนตาได้บ่อยไหม": "ทุก 2-3 สัปดาห์ค่ะ 💖",
    "เติมขนตาเท่าไหร่": "เริ่มต้น 399 บาทค่ะ 👁️",
    "เติมเล็บได้ไหม": "ได้ค่ะ เติมปลายหรือทำใหม่ได้เลย 💅",
    "ทำเล็บเท้าราคาเท่าไหร่": "เริ่มต้น 350 บาทค่ะ 👣",
    "ทำเล็บพร้อมสปาได้ไหม": "ได้เลยค่ะ ทำพร้อมกันได้ 💕",
    "มีเก้าอี้สปาไหม": "มีค่ะ นวดสบายมาก 🛁",
    "มีนวดมือไหม": "มีค่ะ บริการนวดสปามือด้วย 💆‍♀️",
    "มีนวดเท้าไหม": "มีค่ะ ระหว่างทำเล็บเท้าเลย 🦶",
    "ต่อเล็บแบบฝังเพชรไหม": "มีค่ะ วิบวับสุด ๆ 💎",
    "เล็บพังจากที่อื่นซ่อมได้ไหม": "ได้ค่ะ เดี๋ยวช่างดูให้ 💕",
    "ทำขนตาที่อื่นมาเติมได้ไหม": "ได้ค่ะ เดี๋ยวช่างดูรูปแบบให้ก่อน 👁️",
    "ขนตาแพ้กาวทำไง": "ไม่ต้องห่วงค่ะ เรามีกาวสูตรอ่อนโยนสำหรับผิวแพ้ง่าย 💕",
    "ขนตาหลุดข้างเดียวแก้ได้ไหม": "ได้ค่ะ ฟรีภายใน 7 วัน 💖",
    "ต่อขนตาได้กี่แบบ": "มี Classic, Volume, Wispy, Kim K และอีกเพียบ 😍",
    "ต่อเล็บแบบไหนดี": "ขึ้นอยู่กับความยาวและลุคที่ต้องการเลยค่ะ 💅",
    "ต่อเล็บสีพื้นได้ไหม": "ได้ค่ะ สวยเรียบหรูมาก 💕",
    "เล็บสั้นต่อได้ไหม": "ได้ค่ะ ทำให้ดูยาวธรรมชาติเลย 💅",
    "เล็บยาวมากตัดได้ไหม": "ได้ค่ะ ปรับทรงให้ฟรีเลย ✂️",
    "เล็บหักทำยังไง": "มาซ่อมได้เลยค่ะ ไม่คิดเพิ่มใน 7 วัน 💅",
    "ทำเล็บลายคริสต์มาสได้ไหม": "ได้ค่ะ ลายน่ารักมาก 🎄",
    "ทำเล็บลายวาเลนไทน์ได้ไหม": "ได้ค่ะ หัวใจฟรุ้งฟริ้งเลย 💕",
    "ทำเล็บลายปีใหม่ได้ไหม": "ได้เลยค่ะ มีเพชรและกลิตเตอร์จัดเต็ม ✨",
    "ทำเล็บลายฮาโลวีนไหม": "มีค่ะ ลายผีเก๋ ๆ ก็มา 👻",
    "ทำเล็บลายดอกไม้ได้ไหม": "มีค่ะ ลายดอกไม้น่ารักมาก 🌸",
    "ทำเล็บเจลคืออะไร": "ทำเล็บเจลคือการทาสีด้วยเจลที่อบด้วยแสงยูวี ทำให้เงาและติดทนนาน 💅",
    "ทำเล็บเจลดียังไง": "สีติดทนนาน ไม่หลุดง่าย เงาสวยและไม่ต้องรอแห้งค่ะ ✨",
    "เล็บเจลอยู่ได้นานแค่ไหน": "อยู่ได้ประมาณ 3-4 สัปดาห์ค่ะ 💅🏻",
    "ทำเล็บเจลต้องอบไหม": "ใช่ค่ะ ต้องอบด้วยเครื่อง UV หรือ LED 💡",
    "เล็บเจลต้องพักเล็บไหม": "แนะนำให้พักบ้างทุก 2-3 เดือนค่ะ เพื่อสุขภาพเล็บ 💖",
    "ล้างเล็บเจลยังไง": "ใช้รีมูฟเวอร์เฉพาะและห่อด้วยฟอยล์ประมาณ 10 นาทีค่ะ 🧴",
    "ล้างเล็บเจลใช้เวลานานไหม": "ประมาณ 15 นาทีค่ะ ⏱️",
    "ทำเล็บเจลราคาเท่าไหร่": "เริ่มต้น 399 บาทค่ะ 💅",
    "ต่อเล็บเจลราคาเท่าไหร่": "เริ่มต้น 899 บาทค่ะ 💕",
    "ต่อเล็บอะคริลิคราคาเท่าไหร่": "เริ่มต้น 999 บาทค่ะ 💅",
    "สปาเล็บราคาเท่าไหร่": "เริ่มต้น 399 บาทค่ะ 🛁",
    "ทำเล็บธรรมดาเท่าไหร่": "ทาสีธรรมดาเริ่มต้น 199 บาทค่ะ 🎨",
    "ล้างเล็บธรรมดาเท่าไหร่": "ล้างเล็บธรรมดา 100 บาทค่ะ 💅",
    "ต่อเล็บใช้เวลานานไหม": "ประมาณ 1-1.5 ชั่วโมงค่ะ 💖",
    "ทำเล็บเจลใช้เวลานานไหม": "ประมาณ 45 นาที - 1 ชั่วโมงค่ะ 💅",
    "ทำเล็บเท้าใช้เวลานานไหม": "ประมาณ 1 ชั่วโมงค่ะ 👣",
    "ทำเล็บมือ+เท้าพร้อมกันได้ไหม": "ได้เลยค่ะ ทำพร้อมกันได้ 💕",
    "ทำเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ นุ่มนวลทุกขั้นตอน 💅",
    "ต่อเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ ช่างมือเบามาก 💕",
    "เล็บบางทำเล็บเจลได้ไหม": "ได้ค่ะ ใช้เบสสูตรอ่อนโยน ปลอดภัยแน่นอน 💅🏻",
    "เล็บหักทำเล็บได้ไหม": "ได้ค่ะ ซ่อมให้ก่อนต่อ 💪",
    "เล็บสั้นต่อได้ไหม": "ได้ค่ะ ทำให้ดูเรียวยาวธรรมชาติเลย 💅",
    "เล็บยาวมากตัดได้ไหม": "ได้ค่ะ ปรับทรงให้ฟรีเลย ✂️",
    "เล็บพังจากที่อื่นมาซ่อมได้ไหม": "ได้ค่ะ เดี๋ยวช่างดูให้ก่อน 💖",
    "อยากได้ลายเล็บน่ารักๆ": "มีเยอะเลยค่ะ ทั้งมินิมอล พาสเทล การ์ตูน 💕",
    "อยากได้เล็บเรียบหรู": "แนะนำโทนขาวครีม นู้ดทอง ดูแพงมาก 💅",
    "อยากได้เล็บสายฝอ": "แนะนำเล็บยาวเจลใสเพชรแน่น ๆ ค่ะ 💎",
    "อยากได้เล็บแบบเจ้าสาว": "มีแพ็กเกจเจ้าสาวพิเศษเริ่มต้น 1,299 บาทค่ะ 💍",
    "อยากได้เล็บสีใส": "มีค่ะ สีเจลใสธรรมชาติสุด ๆ 💅",
    "อยากได้เล็บสีขาว": "มีค่ะ สีขาวมุกหรือขาวนมก็สวยมาก ✨",
    "อยากได้เล็บสีชมพู": "มีหลายเฉดเลยค่ะ ทั้งพีช พาสเทล หวานสุด ๆ 💖",
    "อยากได้เล็บโทนเข้ม": "มีค่ะ เช่น น้ำตาล ดำ แดงเบอร์กันดี สวยมาก 💅",
    "อยากทำเล็บลายเกาหลี": "มีค่ะ ลายมินิมอลแบบเกาหลีเพียบเลย 💕",
    "อยากทำเล็บลายญี่ปุ่น": "มีค่ะ ลายคิ้วท์น่ารักสุด ๆ 🎀",
    "อยากทำเล็บลายมินิมอล": "ได้เลยค่ะ เรียบง่ายแต่ดูดี 💅",
    "อยากทำเล็บลายหินอ่อน": "มีค่ะ ลายหินอ่อนสุดหรู ✨",
    "อยากทำเล็บลายกลิตเตอร์": "มีค่ะ วิบวับสุด ๆ 💎",
    "อยากทำเล็บลายเพชร": "มีค่ะ ติดเพชร Swarovski สวยหรูเลย 💍",
    "อยากทำเล็บลายคริสต์มาส": "มีค่ะ ลายหิมะ กวาง ดาวทอง 🎄",
    "อยากทำเล็บลายปีใหม่": "มีค่ะ วิบวับรับปีใหม่เลย ✨",
    "อยากทำเล็บลายวาเลนไทน์": "มีค่ะ หัวใจชมพูฟรุ้งฟริ้ง 💕",
    "อยากทำเล็บลายฮาโลวีน": "มีค่ะ ลายฟักทอง ผีเก๋ ๆ 👻",
    "อยากทำเล็บลายการ์ตูน": "มีค่ะ ลายซานริโอ มิกกี้ และอีกเพียบ 🎨",
    "อยากทำเล็บลายมุก": "มีค่ะ สีมุกเงาๆ กำลังฮิต 💅",
    "อยากทำเล็บลายวาวๆ": "มีค่ะ สีแม่เหล็กวิ้งมาก 🧲",
    "เล็บพังจากเจลทำไงดี": "พักเล็บ 1-2 สัปดาห์แล้วบำรุงด้วยออยล์ค่ะ 💖",
    "บำรุงเล็บยังไงดี": "ใช้ cuticle oil และครีมบำรุงทุกวันค่ะ 💅",
    "ทำเล็บบ่อย ๆ จะบางไหม": "ถ้าทำถูกวิธีไม่บางค่ะ 💕",
    "ควรพักเล็บนานเท่าไหร่": "ทุก 2-3 เดือนควรพักสัก 1 สัปดาห์ค่ะ 💅🏻",
    "ใช้ครีมบำรุงเล็บอะไรดี": "ใช้ครีมน้ำมันหรือเซรั่มบำรุงจมูกเล็บได้เลยค่ะ 💧",
    "หลังทำเล็บควรดูแลยังไง": "หลีกเลี่ยงน้ำแรง ๆ และใช้ออยล์บำรุงทุกวันค่ะ 💅",
    "ทำเล็บก่อนออกงานได้ไหม": "ได้เลยค่ะ สีติดแน่นไม่หลุดแน่นอน 💖",
    "ทำเล็บก่อนแต่งงานได้ไหม": "มีแพ็กเกจเจ้าสาวพิเศษเลยค่ะ 💍",
    "ทำเล็บก่อนถ่ายรูปได้ไหม": "แน่นอนค่ะ ช่างช่วยเลือกสีให้เหมาะกับธีมได้เลย 💕",
    "ทำเล็บก่อนต่างประเทศได้ไหม": "ได้ค่ะ อยู่ได้ยาว 3-4 สัปดาห์ ✈️",
    "ทำเล็บก่อนเที่ยวทะเลได้ไหม": "ได้เลยค่ะ ใช้เจลกันน้ำไม่หลุดแน่นอน 🏖️",
    "ทำเล็บก่อนปีใหม่ได้ไหม": "ได้เลยค่ะ สีมงคลรับโชค 🎉",
    "ทำเล็บก่อนวันเกิดได้ไหม": "ได้เลยค่ะ แนะนำสีชมพูทองรับทรัพย์ 💅",
    "ทำเล็บก่อนวันวาเลนไทน์ดีไหม": "ดีเลยค่ะ ลายหัวใจสุดหวาน 💖",
    "ทำเล็บก่อนเปิดเทอมได้ไหม": "ได้ค่ะ สีสุภาพเหมาะกับนักเรียน 💕",
    "ทำเล็บก่อนสัมภาษณ์งานดีไหม": "ดีเลยค่ะ โทนนู้ดเรียบร้อย ✨",
    "ทำเล็บก่อนออกงานได้ไหม": "เหมาะมากเลยค่ะ 💅",
    "เล็บลอกทำยังไงดี": "อย่าดึงเองค่ะ มาที่ร้านล้างให้ 💖",
    "เล็บเหลืองทำไงดี": "ใช้เบสป้องกันและแช่น้ำมะนาวช่วยได้ค่ะ 🍋",
    "เล็บหักซ่อมได้ไหม": "ได้ค่ะ ซ่อมให้ฟรีใน 7 วัน 💅",
    "เล็บฉีกทำไงดี": "ใช้เทปเล็บปิดหรือให้ช่างซ่อมให้ค่ะ 💕",
    "เล็บมีเชื้อราแก้ยังไง": "ควรพักเล็บและรักษาก่อนค่ะ 💊",
    "เล็บเป็นคลื่นทำไงดี": "พักเล็บและบำรุงด้วยออยล์ค่ะ 💅",
    "เล็บเปราะง่ายทำไงดี": "บำรุงด้วยวิตามิน E และทาออยล์ทุกวัน 💕",
    "เล็บไม่เงาทำไงดี": "ใช้ top coat เพิ่มความเงาได้ค่ะ ✨",
    "ทำเล็บแล้วขึ้นฟองทำไม": "อาจเกิดจากอากาศหรือชั้นเจลหนาเกินไปค่ะ 💅",
    "ทำเล็บแล้วสีไม่ติดทำไม": "อาจเพราะหน้าเล็บมัน ต้องขัดเบา ๆ ก่อนค่ะ 💖",
    "ทำเล็บแล้วเป็นคลื่นทำไม": "เพราะชั้นเจลหนาเกินไปค่ะ เดี๋ยวช่างแก้ให้ 💅",
    "ทำเล็บแล้วหลุดเร็วทำไม": "อาจเพราะโดนน้ำหรือเคมีบ่อยค่ะ 💧",
    "ทำเล็บเจลกับทาสีธรรมดาต่างกันยังไง": "เจลติดทนกว่าและเงาสวยกว่าค่ะ 💅🏻",
    "เล็บสั้นทำแบบไหนดี": "แนะนำทาสีเจลหรือสปามือค่ะ 💕",
    "เล็บยาวทำแบบไหนดี": "ต่อปลายและเคลือบเจลเลยค่ะ สวยเรียว 💅",
    "เล็บกว้างทำแบบไหนดี": "ทรงอัลมอนด์หรือวงรีจะช่วยให้ดูเรียวค่ะ 💅🏻",
    "เล็บแคบทำแบบไหนดี": "ทรงสquoval หรือทรงตรงจะเหมาะค่ะ 💕",
    "เล็บรูปอะไรสวยสุด": "ทรงอัลมอนด์กำลังฮิตเลยค่ะ ✨",
    "อยากทำเล็บแต่ไม่รู้เลือกแบบไหน": "ส่งรูปตัวอย่างได้เลยค่ะ ช่างช่วยแนะนำ 💅",
    "อยากได้เล็บโทนสุภาพ": "โทนนู้ด ชมพูพีช เหมาะมากค่ะ 💕",
    "อยากได้เล็บโทนหวาน": "ชมพูอ่อน พาสเทล น่ารักสุด ๆ 💖",
    "อยากได้เล็บโทนเข้ม": "แดงเข้ม น้ำตาล ดำ สวยแพงมาก 💅",
    "อยากได้เล็บโทนสายมู": "แนะนำทอง เขียว ม่วง เสริมโชค ✨",
    "อยากได้เล็บโทนทำงาน": "โทนนู้ดสุภาพ เรียบหรู 💼",
    "อยากได้เล็บโทนเที่ยว": "สีสดใส ลายเพนต์หรือกลิตเตอร์ 🎉",
    "อยากได้เล็บโทนเจ้าสาว": "ขาว มุก ชมพูอ่อน สวยละมุน 💍",
    "อยากได้เล็บโทนแฟชั่น": "โทนแดง ดำ น้ำเงิน ดูเด่นมาก 💅",
    "อยากได้เล็บโทนหรู": "ทอง เงิน มุก หรือกลิตเตอร์ ✨",
    "เลือกสีเล็บยังไงให้เหมาะกับผิว": "ผิวขาวเหมาะกับโทนชมพู พาสเทล ผิวสองสีเหมาะกับนู้ดหรือแดงเข้ม ผิวคล้ำเหมาะกับทองหรือส้มค่ะ 💅",
    "สีเล็บมงคลมีอะไรบ้าง": "สีชมพูเสริมความรัก สีทองเสริมโชคลาภ สีแดงเสริมพลัง สีเขียวเสริมการเงินค่ะ ✨",
    "สีเล็บเสริมดวงเดือนนี้": "แนะนำโทนสีพาสเทลหรือชมพูทอง เสริมเสน่ห์มากค่ะ 💖",
    "อยากได้เล็บเสริมโชค": "สีทอง เขียว น้ำเงิน หรือม่วงดีมากค่ะ 💰",
    "สีเล็บเรียกทรัพย์": "สีทอง เขียว และชมพูอ่อนค่ะ 💵",
    "สีเล็บเรียกความรัก": "ชมพู พีช ม่วงพาสเทลค่ะ 💕",
    "สีเล็บเรียกงาน": "โทนนู้ด น้ำตาลอ่อน สุภาพดูดีค่ะ 💼",
    "สีเล็บเรียกความปัง": "แดงสดหรือกลิตเตอร์ทองเลยค่ะ ✨",
    "สีเล็บถูกโฉลกวันจันทร์": "สีครีม เหลืองทองค่ะ 🌕",
    "สีเล็บถูกโฉลกวันอังคาร": "สีส้ม แดงค่ะ 🔥",
    "สีเล็บถูกโฉลกวันพุธ": "สีเขียวค่ะ 🌿",
    "สีเล็บถูกโฉลกวันพฤหัส": "สีชมพูค่ะ 💖",
    "สีเล็บถูกโฉลกวันศุกร์": "สีฟ้า น้ำเงินค่ะ 💙",
    "สีเล็บถูกโฉลกวันเสาร์": "สีม่วงค่ะ 💜",
    "สีเล็บถูกโฉลกวันอาทิตย์": "สีทองหรือเหลืองค่ะ ☀️",
    "ทาเล็บแล้วเป็นฟองทำยังไง": "ทาบาง ๆ และปล่อยให้แต่ละชั้นแห้งก่อนค่ะ 💅",
    "ทำไมเล็บเจลถึงหลุดง่าย": "อาจเพราะหน้าเล็บมัน หรือไม่ได้ขัดเบา ๆ ก่อนทาค่ะ 💖",
    "ทาเล็บแล้วขึ้นคลื่นแก้ยังไง": "ให้ขัดหน้าเล็บให้เรียบก่อนทาค่ะ 💅",
    "เจลไม่เงาทำยังไงดี": "ใช้ top coat แล้วอบซ้ำอีกครั้งค่ะ ✨",
    "สีเล็บหมองทำยังไงดี": "ทาทับด้วย top coat จะกลับมาเงาเหมือนใหม่ค่ะ 💅",
    "เล็บเจลหลุดก่อนกำหนดทำไม": "เพราะโดนน้ำหรือเคมีบ่อยเกินไปค่ะ 💧",
    "ล้างจานแล้วเล็บพังทำไงดี": "ใส่ถุงมือป้องกันและบำรุงหลังทำงานบ้านค่ะ 🧤",
    "ใช้ครีมบำรุงเล็บอะไรดี": "แนะนำ cuticle oil หรือ jojoba oil ค่ะ 💅",
    "ใช้ท็อปโค้ทยี่ห้อไหนดี": "ใช้ของร้านได้เลยค่ะ คุณภาพดีและเงามาก 💖",
    "เจลที่ร้านใช้ยี่ห้ออะไร": "ใช้แบรนด์นำเข้าคุณภาพดี ปลอดภัยไม่ทำลายหน้าเล็บค่ะ 💅",
    "อบเล็บนานไหม": "ประมาณ 30-60 วินาทีต่อรอบค่ะ 💡",
    "เครื่องอบเล็บแบบไหนดี": "แบบ LED จะเร็วกว่าและไม่ร้อนมือค่ะ ✨",
    "ต้องขัดเล็บก่อนทาเจลไหม": "ต้องขัดเบา ๆ เพื่อให้เจลติดแน่นค่ะ 💅",
    "ต้องทาเบสก่อนเจลไหม": "ต้องค่ะ เพื่อปกป้องหน้าเล็บ 💕",
    "ต้องทาท็อปไหม": "ต้องค่ะ เพื่อความเงาและติดทนนาน 💅",
    "เล็บบางทำยังไงดี": "ใช้เบสป้องกันเล็บบางหรือพักเล็บสัก 1 สัปดาห์ค่ะ 💖",
    "เล็บแตกปลายทำไงดี": "ตัดแต่งและเคลือบเจลบาง ๆ ป้องกันแตกเพิ่มค่ะ 💅",
    "เล็บเปราะง่ายแก้ยังไง": "บำรุงด้วยน้ำมันมะพร้าวและวิตามิน E ค่ะ 🌿",
    "เล็บเหลืองจากยาทาเล็บแก้ยังไง": "พักเล็บและแช่น้ำมะนาวอุ่น ๆ 10 นาทีค่ะ 🍋",
    "ต้องพักเล็บบ่อยแค่ไหน": "ทุก 2-3 เดือนพักเล็บ 1-2 สัปดาห์ค่ะ 💅",
    "ทำเล็บบ่อยเกินไปอันตรายไหม": "ไม่ค่ะ ถ้าทำถูกวิธีและมีการพักเล็บเป็นระยะ 💖",
    "เล็บขึ้นช้าแก้ยังไง": "บำรุงด้วยน้ำมันและนวดเล็บทุกวันค่ะ 💅",
    "อยากต่อเล็บแต่กลัวพัง": "ไม่ต้องห่วงค่ะ ใช้วัสดุคุณภาพดีไม่ทำลายหน้าเล็บ 💕",
    "เล็บติดเพชรจะหลุดไหม": "ไม่หลุดง่ายค่ะ ติดแน่นมาก 💎",
    "ล้างมือบ่อยเล็บจะพังไหม": "ไม่ค่ะ ถ้าใช้ออยล์บำรุงหลังล้างมือ 💧",
    "อยากเปลี่ยนสีเล็บทำไงดี": "ล้างสีเก่าแล้วทาใหม่ได้เลยค่ะ 💅",
    "อยากได้เล็บเข้ากับชุด": "ส่งรูปชุดมาช่างช่วยแมทช์สีให้ได้เลยค่ะ 👗",
    "อยากทำเล็บธีมงานแต่ง": "มีแพ็กเกจพิเศษสำหรับเจ้าสาวค่ะ 💍",
    "อยากทำเล็บธีมคริสต์มาส": "มีลายกวางหิมะ ดาว และกลิตเตอร์ค่ะ 🎄",
    "อยากทำเล็บธีมปีใหม่": "สีทอง กลิตเตอร์ และเลข 2025 กำลังฮิตค่ะ ✨",
    "อยากทำเล็บธีมวาเลนไทน์": "มีลายหัวใจ หวานสุด ๆ 💖",
    "อยากทำเล็บธีมวันเกิด": "แนะนำกลิตเตอร์หรือเพชรเพิ่มความปังค่ะ 🎉",
    "อยากทำเล็บธีมฮาโลวีน": "มีลายผี ฟักทอง ควันม่วงเก๋ ๆ 👻",
    "อยากทำเล็บธีมซากุระ": "มีลายดอกไม้ชมพูพาสเทลค่ะ 🌸",
    "อยากทำเล็บธีมดอกไม้": "มีทั้งลายเพนต์และสติ๊กเกอร์ดอกไม้ค่ะ 🌼",
    "อยากทำเล็บธีมมินิมอล": "โทนนู้ด เรียบหรู ดูแพง 💅",
    "อยากทำเล็บธีมเกาหลี": "ลายใส ๆ เงาแบบ glass nail ค่ะ 💖",
    "อยากทำเล็บธีมญี่ปุ่น": "ลายคิ้วท์หวาน ๆ เพชรเล็ก ๆ 💕",
    "อยากทำเล็บธีมแฟชั่น": "แนวเมทัลลิก กลิตเตอร์หรือเพชรแน่น ✨",
    "อยากทำเล็บธีมธรรมชาติ": "โทนเขียว น้ำตาล เรียบหรูมาก 🌿",
    "อยากทำเล็บธีมงานบริษัท": "โทนนู้ดหรือน้ำตาลอ่อนดูเรียบร้อยค่ะ 💼",
    "อยากทำเล็บธีมเที่ยวทะเล": "ลายเปลือกหอย คลื่น ฟ้า ขาว 🌊",
    "อยากทำเล็บธีมเรียน": "สีอ่อน ๆ สุภาพ เช่น พีช นู้ด 💅",
    "อยากทำเล็บธีมพาสเทล": "ชมพู ฟ้า ม่วงอ่อน หวานละมุน 💖",
    "อยากทำเล็บธีมวิบวับ": "กลิตเตอร์หรือผงแม่เหล็กค่ะ ✨",
    "อยากทำเล็บธีมสวยหรู": "โทนมุกทอง เพชร Swarovski 💎",
    "อยากทำเล็บธีมสายมู": "สีทอง เขียว ม่วง เสริมโชคมาก 💰",
    "อยากทำเล็บธีมเจ้าหญิง": "สีชมพูอ่อน เพชรเล็ก ๆ ฟรุ้งฟริ้ง 💕",
    "อยากทำเล็บธีมโฮโลแกรม": "มีค่ะ แสงเล่นสีสุดล้ำ ✨",
    "อยากทำเล็บธีมแม่เหล็ก": "มีค่ะ แม่เหล็กวิ้งๆ สวยมาก 💅",
    "อยากทำเล็บธีมมุก": "มีค่ะ เคลือบมุกเงาสุดหรู 💎",
    "อยากทำเล็บธีมใส": "มีค่ะ ใสธรรมชาติแต่ดูแพง 💅",
    "อยากทำเล็บธีมมินิมอลใส": "ได้เลยค่ะ ลายเรียบ ๆ วิ้งเบา ๆ ✨",
    "อยากได้เล็บแบบ Glass Nail": "มีค่ะ เงาวาวเหมือนกระจก 💅",
    "อยากได้เล็บแบบ Chrome": "มีค่ะ สีเมทัลลิกเงาโดดเด่น 💖",
    "อยากได้เล็บแบบ Aurora": "มีค่ะ สีรุ้งวาว ๆ สวยมาก 🌈",
    "อยากได้เล็บแบบ Ombre": "มีค่ะ ไล่สีเรียบหรูมาก 💅",
    "อยากได้เล็บแบบ French": "มีค่ะ ขอบขาวเรียบหรูดูแพง 💕",
    "อยากได้เล็บแบบ Cat Eye": "มีค่ะ แม่เหล็กวิ้งสวยสุด ✨",
    "อยากได้เล็บแบบ Gradient": "มีค่ะ ไล่สีพาสเทลน่ารัก 💅",
    "อยากได้เล็บแบบใสเพชร": "มีค่ะ สวยวิ้งสุด 💎",
    "อยากได้เล็บแบบเคลือบมุก": "มีค่ะ เงาละมุนมาก 💖",
    "ขอจองคิวทำเล็บ": "สามารถแจ้งวันและเวลาที่ต้องการได้เลยค่ะ",
    "ขอจองคิววันเสาร์": "ได้ค่ะ กรุณาแจ้งเวลาที่ต้องการ",
    "ขอจองคิววันอาทิตย์": "ได้ค่ะ กรุณาแจ้งเวลาที่ต้องการ",
    "ขอจองคิววันหยุด": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิววันธรรมดา": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวล่วงหน้า": "จองล่วงหน้าได้สูงสุด 30 วันค่ะ",
    "ขอจองคิวด่วน": "ถ้าช่างว่างสามารถรับคิวด่วนได้ค่ะ",
    "ขอจองคิวกลุ่ม": "สามารถจองคิวเป็นกลุ่มได้ค่ะ แจ้งจำนวนคนและเวลาที่ต้องการ",
    "ขอจองคิวเจ้าสาว": "ได้ค่ะ กรุณาแจ้งวันแต่งงานและเวลาที่ต้องการ",
    "ขอจองคิวเจ้าบ่าว": "ได้ค่ะ กรุณาแจ้งวันแต่งงานและเวลาที่ต้องการ",
    "ขอจองคิวเด็ก": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวผู้ชาย": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวผู้สูงอายุ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวสปาเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวต่อเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวเพ้นท์เล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวถอดเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวซ่อมเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวทาสีเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวเจล": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวอะคริลิก": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิว PVC": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวบำรุงเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวตัดหนัง": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวขัดเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวล้างเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวตกแต่งเล็บ": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวพาราฟิน": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายแฟนซี": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายเรียบง่าย": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายหรูหรา": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายเกาหลี": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายญี่ปุ่น": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายฝรั่งเศส": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายมินิมอล": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายดอกไม้": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายการ์ตูน": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายคริสต์มาส": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายวาเลนไทน์": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายปีใหม่": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายสงกรานต์": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายฮาโลวีน": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายตรุษจีน": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายวันเกิด": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายรับปริญญา": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายแต่งงาน": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายเจ้าสาว": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ขอจองคิวลายเจ้าบ่าว": "ได้ค่ะ กรุณาแจ้งวันและเวลาที่ต้องการ",
    "ช่างทำเล็บไม่ตรงเวลา": "ขออภัยค่ะ ทางร้านจะปรับปรุงเรื่องการตรงต่อเวลา",
    "ช่างทำเล็บไม่ตั้งใจ": "ขออภัยค่ะ ทางร้านจะเน้นการดูแลลูกค้าให้มากขึ้น",
    "ช่างทำเล็บไม่ใส่ใจ": "ขออภัยค่ะ ทางร้านจะเน้นความใส่ใจในการบริการ",
    "ช่างทำเล็บไม่รับฟัง": "ขออภัยค่ะ ทางร้านจะเน้นการรับฟังลูกค้า",
    "ช่างทำเล็บไม่อธิบาย": "ขออภัยค่ะ ทางร้านจะปรับปรุงการสื่อสาร",
    "ช่างทำเล็บไม่ให้คำแนะนำ": "ขออภัยค่ะ ทางร้านจะเน้นการให้คำแนะนำ",
    "ช่างทำเล็บไม่สุภาพ": "ขออภัยค่ะ ทางร้านจะตักเตือนและปรับปรุงพฤติกรรม",
    "ช่างทำเล็บไม่ยิ้มแย้ม": "ขออภัยค่ะ ทางร้านจะเน้นความเป็นกันเอง",
    "ช่างทำเล็บไม่ทักทาย": "ขออภัยค่ะ ทางร้านจะเน้นการทักทายลูกค้า",
    "ช่างทำเล็บไม่สะอาด": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนถุงมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่ล้างมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนอุปกรณ์": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาดอุปกรณ์",
    "ช่างทำเล็บไม่ใส่หน้ากาก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่ใส่ผ้ากันเปื้อน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้ากันเปื้อน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปูโต๊ะ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าขนหนู": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าคลุม": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดปาก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดจมูก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหน้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดตา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหู": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดคอ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดแขน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดขา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดเท้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดนิ้ว": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหน้าเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหลังเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดข้างเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดใต้เล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดบนเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบนิ้ว": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบแขน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบขา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบเท้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบคอ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "วันนี้อากาศเป็นยังไง": "วันนี้อากาศดีค่ะ เหมาะกับการทำเล็บ",
    "ร้านเปิดกี่โมง": "ร้านเปิด 10.00 น. ถึง 20.00 น. ทุกวันค่ะ",
    "ร้านปิดกี่โมง": "ร้านปิด 20.00 น. ค่ะ",
    "ร้านอยู่ที่ไหน": "ร้านอยู่ใกล้ BTS สถานีแฟชั่น",
    "มีที่จอดรถไหม": "มีที่จอดรถหน้าร้านค่ะ",
    "ร้านรับบัตรเครดิตไหม": "รับค่ะ ทุกธนาคาร",
    "ร้านรับโอนเงินไหม": "รับค่ะ ทุกธนาคาร",
    "ร้านรับพร้อมเพย์ไหม": "รับค่ะ",
    "ร้านรับเงินสดไหม": "รับค่ะ",
    "ร้านมีบริการอะไรบ้าง": "มีบริการทำเล็บมือ เล็บเท้า ต่อเล็บ เพ้นท์เล็บ สปาเล็บ",
    "ร้านมีโปรโมชั่นอะไรบ้าง": "สอบถามโปรโมชั่นได้เลยค่ะ",
    "ร้านมีบริการนวดมือไหม": "มีค่ะ",
    "ร้านมีบริการนวดเท้าไหม": "มีค่ะ",
    "ร้านมีบริการสปาไหม": "มีค่ะ",
    "ร้านมีบริการต่อเล็บไหม": "มีค่ะ",
    "ร้านมีบริการเพ้นท์เล็บไหม": "มีค่ะ",
    "ร้านมีบริการถอดเล็บไหม": "มีค่ะ",
    "ร้านมีบริการซ่อมเล็บไหม": "มีค่ะ",
    "ร้านมีบริการทาสีเล็บไหม": "มีค่ะ",
    "ร้านมีบริการเจลไหม": "มีค่ะ",
    "ร้านมีบริการอะคริลิกไหม": "มีค่ะ",
    "ร้านมีบริการ PVC ไหม": "มีค่ะ",
    "ร้านมีบริการบำรุงเล็บไหม": "มีค่ะ",
    "ร้านมีบริการตัดหนังไหม": "มีค่ะ",
    "ร้านมีบริการขัดเล็บไหม": "มีค่ะ",
    "ร้านมีบริการล้างเล็บไหม": "มีค่ะ",
    "ร้านมีบริการตกแต่งเล็บไหม": "มีค่ะ",
    "ร้านมีบริการพาราฟินไหม": "มีค่ะ",
    "ร้านมีบริการลายแฟนซีไหม": "มีค่ะ",
    "ร้านมีบริการลายเรียบง่ายไหม": "มีค่ะ",
    "ร้านมีบริการลายหรูหราไหม": "มีค่ะ",
    "ร้านมีบริการลายเกาหลีไหม": "มีค่ะ",
    "ร้านมีบริการลายญี่ปุ่นไหม": "มีค่ะ",
    "ร้านมีบริการลายฝรั่งเศสไหม": "มีค่ะ",
    "ร้านมีบริการลายมินิมอลไหม": "มีค่ะ",
    "ร้านมีบริการลายดอกไม้ไหม": "มีค่ะ",
    "ร้านมีบริการลายการ์ตูนไหม": "มีค่ะ",
    "ร้านมีบริการลายคริสต์มาสไหม": "มีค่ะ",
    "ร้านมีบริการลายวาเลนไทน์ไหม": "มีค่ะ",
    "ร้านมีบริการลายปีใหม่ไหม": "มีค่ะ",
    "ร้านมีบริการลายสงกรานต์ไหม": "มีค่ะ",
    "ร้านมีบริการลายฮาโลวีนไหม": "มีค่ะ",
    "ร้านมีบริการลายตรุษจีนไหม": "มีค่ะ",
    "ร้านมีบริการลายวันเกิดไหม": "มีค่ะ",
    "ร้านมีบริการลายรับปริญญาไหม": "มีค่ะ",
    "ร้านมีบริการลายแต่งงานไหม": "มีค่ะ",
    "ร้านมีบริการลายเจ้าสาวไหม": "มีค่ะ",
    "ร้านมีบริการลายเจ้าบ่าวไหม": "มีค่ะ",
    "ร้านมีบริการลายเด็กไหม": "มีค่ะ",
    "ร้านมีบริการลายผู้ชายไหม": "มีค่ะ",
    "ร้านมีบริการลายผู้สูงอายุไหม": "มีค่ะ",
    "ช่างพูดไม่สุภาพ": "ขออภัยในความไม่สะดวกค่ะ ทางร้านจะตักเตือนและปรับปรุงพฤติกรรมช่าง",
    "ช่างบริการไม่ดี": "ขออภัยค่ะ ทางร้านจะปรับปรุงการบริการของช่าง",
    "ช่างทำเล็บไม่ตรงแบบ": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "ช่างทำเล็บช้า": "ขออภัยค่ะ ทางร้านจะปรับปรุงเรื่องความรวดเร็ว",
    "ช่างทำเล็บไม่ใส่ใจ": "ขออภัยค่ะ ทางร้านจะเน้นการดูแลลูกค้าให้มากขึ้น",
    "ช่างทำเล็บไม่รับฟัง": "ขออภัยค่ะ ทางร้านจะเน้นการรับฟังลูกค้า",
    "ช่างทำเล็บไม่อธิบายขั้นตอน": "ขออภัยค่ะ ทางร้านจะปรับปรุงการสื่อสาร",
    "ช่างทำเล็บไม่ให้คำแนะนำ": "ขออภัยค่ะ ทางร้านจะเน้นการให้คำแนะนำ",
    "ช่างทำเล็บไม่สุภาพ": "ขออภัยค่ะ ทางร้านจะตักเตือนและปรับปรุงพฤติกรรม",
    "ช่างทำเล็บไม่ยิ้มแย้ม": "ขออภัยค่ะ ทางร้านจะเน้นความเป็นกันเอง",
    "ช่างทำเล็บไม่ทักทาย": "ขออภัยค่ะ ทางร้านจะเน้นการทักทายลูกค้า",
    "ช่างทำเล็บไม่ใส่ใจรายละเอียด": "ขออภัยค่ะ ทางร้านจะเน้นความละเอียดในการทำงาน",
    "ช่างทำเล็บไม่สะอาด": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนถุงมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่ล้างมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนอุปกรณ์": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาดอุปกรณ์",
    "ช่างทำเล็บไม่ใส่หน้ากาก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่ใส่ผ้ากันเปื้อน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้ากันเปื้อน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปูโต๊ะ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าขนหนู": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าคลุม": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องความสะอาด",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดปาก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดจมูก": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหน้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดตา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหู": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดคอ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดแขน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดขา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดเท้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดนิ้ว": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหน้าเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดหลังเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดข้างเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดใต้เล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดบนเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบเล็บ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบนิ้ว": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบมือ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบแขน": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบขา": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบเท้า": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "ช่างทำเล็บไม่เปลี่ยนผ้าปิดรอบคอ": "ขออภัยค่ะ ทางร้านจะเน้นเรื่องสุขอนามัย",
    "เล็บหลุดหลังทำ": "ขออภัยค่ะ สามารถเข้ามาซ่อมเล็บฟรีภายใน 7 วัน",
    "เล็บแตกหลังทำ": "ขออภัยค่ะ ทางร้านยินดีซ่อมให้ฟรีภายใน 7 วัน",
    "เล็บลอกหลังทำ": "ขออภัยค่ะ สามารถเข้ามาซ่อมฟรีภายใน 7 วัน",
    "เล็บเจ็บหลังทำ": "ขออภัยค่ะ หากเจ็บมากกรุณาติดต่อร้านทันที",
    "เล็บอักเสบหลังทำ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บบวมหลังทำ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บแดงหลังทำ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บมีรอยหลังทำ": "ขออภัยค่ะ สามารถเข้ามาซ่อมฟรีภายใน 7 วัน",
    "เล็บสีหลุดเร็ว": "ขออภัยค่ะ สามารถเข้ามาเติมสีฟรีภายใน 7 วัน",
    "เล็บสีไม่ติด": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บสีไม่สวย": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "เล็บสีไม่ตรงแบบ": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "เล็บลายไม่ตรงแบบ": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บลายไม่สวย": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "เล็บลายหลุด": "ขออภัยค่ะ สามารถเข้ามาซ่อมฟรีภายใน 7 วัน",
    "เล็บลายลอก": "ขออภัยค่ะ สามารถเข้ามาซ่อมฟรีภายใน 7 วัน",
    "เล็บลายแตก": "ขออภัยค่ะ ทางร้านยินดีซ่อมให้ฟรี",
    "เล็บลายบวม": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายแดง": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายอักเสบ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายเจ็บ": "ขออภัยค่ะ หากเจ็บมากกรุณาติดต่อร้านทันที",
    "เล็บลายไม่ติด": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บลายสีไม่ตรง": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บลายสีไม่สวย": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "เล็บลายสีหลุด": "ขออภัยค่ะ สามารถเข้ามาเติมสีฟรีภายใน 7 วัน",
    "เล็บลายสีลอก": "ขออภัยค่ะ สามารถเข้ามาเติมสีฟรีภายใน 7 วัน",
    "เล็บลายสีแตก": "ขออภัยค่ะ ทางร้านยินดีซ่อมให้ฟรี",
    "เล็บลายสีบวม": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายสีแดง": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายสีอักเสบ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บลายสีเจ็บ": "ขออภัยค่ะ หากเจ็บมากกรุณาติดต่อร้านทันที",
    "เล็บต่อหลุด": "ขออภัยค่ะ สามารถเข้ามาซ่อมฟรีภายใน 7 วัน",
    "เล็บต่อแตก": "ขออภัยค่ะ ทางร้านยินดีซ่อมให้ฟรี",
    "เล็บต่อบวม": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่อแดง": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่ออักเสบ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่อเจ็บ": "ขออภัยค่ะ หากเจ็บมากกรุณาติดต่อร้านทันที",
    "เล็บต่อไม่ติด": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บต่อสีไม่ตรง": "ขออภัยค่ะ ทางร้านยินดีแก้ไขให้ฟรี",
    "เล็บต่อสีไม่สวย": "ขออภัยค่ะ สามารถแจ้งร้านเพื่อแก้ไขได้",
    "เล็บต่อสีหลุด": "ขออภัยค่ะ สามารถเข้ามาเติมสีฟรีภายใน 7 วัน",
    "เล็บต่อสีลอก": "ขออภัยค่ะ สามารถเข้ามาเติมสีฟรีภายใน 7 วัน",
    "เล็บต่อสีแตก": "ขออภัยค่ะ ทางร้านยินดีซ่อมให้ฟรี",
    "เล็บต่อสีบวม": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่อสีแดง": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่อสีอักเสบ": "ขออภัยค่ะ กรุณาติดต่อร้านเพื่อรับคำแนะนำ",
    "เล็บต่อสีเจ็บ": "ขออภัยค่ะ หากเจ็บมากกรุณาติดต่อร้านทันที",
    "ขอแสดงความคิดเห็นเกี่ยวกับร้าน": "ขอบคุณสำหรับความคิดเห็นค่ะ ทางร้านยินดีรับฟังทุกข้อเสนอแนะ",
    "ขอชมเชยช่างทำเล็บ": "ขอบคุณมากค่ะ ทางร้านจะส่งต่อคำชมให้ช่าง",
    "ขอติเรื่องบริการ": "ขออภัยในความไม่สะดวกค่ะ ทางร้านจะปรับปรุงบริการ",
    "ขอแนะนำเพิ่มเติม": "ขอบคุณสำหรับคำแนะนำค่ะ ทางร้านจะนำไปพิจารณา",
    "ขอร้องเรียน": "ขออภัยในความไม่สะดวกค่ะ สามารถแจ้งรายละเอียดเพิ่มเติมได้เลย",
    "ขอขอบคุณร้าน": "ขอบคุณมากค่ะ ยินดีให้บริการเสมอ",
    "ร้านมีช่องทางให้ติชมไหม": "สามารถติชมผ่าน LINE นี้ได้เลยค่ะ",
    "ขอให้ปรับปรุงเรื่องเวลา": "ขออภัยค่ะ ทางร้านจะปรับปรุงเรื่องเวลาให้ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องความสะอาด": "ขอบคุณสำหรับคำแนะนำค่ะ ทางร้านจะเน้นเรื่องความสะอาดมากขึ้น",
    "ขอให้ปรับปรุงเรื่องราคาค่าบริการ": "ขอบคุณสำหรับข้อเสนอแนะค่ะ ทางร้านจะพิจารณาเรื่องราคา",
    "ขอให้ปรับปรุงเรื่องการจองคิว": "ขออภัยค่ะ ทางร้านจะปรับปรุงระบบจองคิว",
    "ขอให้ปรับปรุงเรื่องการตอบกลับ": "ขออภัยค่ะ ทางร้านจะตอบกลับให้รวดเร็วขึ้น",
    "ขอให้ปรับปรุงเรื่องการบริการ": "ขออภัยค่ะ ทางร้านจะปรับปรุงบริการให้ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องการแต่งเล็บ": "ขอบคุณค่ะ ทางร้านจะพัฒนาฝีมือช่างต่อไป",
    "ขอให้ปรับปรุงเรื่องอุปกรณ์": "ขอบคุณค่ะ ทางร้านจะตรวจสอบและปรับปรุงอุปกรณ์",
    "ขอให้ปรับปรุงเรื่องสถานที่": "ขอบคุณค่ะ ทางร้านจะปรับปรุงสถานที่ให้ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องความปลอดภัย": "ขอบคุณค่ะ ทางร้านจะเน้นความปลอดภัยมากขึ้น",
    "ขอให้ปรับปรุงเรื่องความเป็นกันเอง": "ขอบคุณค่ะ ทางร้านจะเน้นความเป็นกันเอง",
    "ขอให้ปรับปรุงเรื่องความรวดเร็ว": "ขอบคุณค่ะ ทางร้านจะปรับปรุงความรวดเร็ว",
    "ขอให้ปรับปรุงเรื่องการสื่อสาร": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการสื่อสาร",
    "ขอให้ปรับปรุงเรื่องการจ่ายเงิน": "ขอบคุณค่ะ ทางร้านจะปรับปรุงระบบการจ่ายเงิน",
    "ขอให้ปรับปรุงเรื่องการแจ้งโปรโมชั่น": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งโปรโมชั่น",
    "ขอให้ปรับปรุงเรื่องการแจ้งข่าวสาร": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งข่าวสาร",
    "ขอให้ปรับปรุงเรื่องการนัดหมาย": "ขอบคุณค่ะ ทางร้านจะปรับปรุงระบบนัดหมาย",
    "ขอให้ปรับปรุงเรื่องการรอคิว": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการจัดการคิว",
    "ขอให้ปรับปรุงเรื่องการดูแลลูกค้า": "ขอบคุณค่ะ ทางร้านจะเน้นการดูแลลูกค้า",
    "ขอให้ปรับปรุงเรื่องการให้คำแนะนำ": "ขอบคุณค่ะ ทางร้านจะให้คำแนะนำที่ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องการตอบคำถาม": "ขอบคุณค่ะ ทางร้านจะตอบคำถามให้ครบถ้วน",
    "ขอให้ปรับปรุงเรื่องการจัดการเวลา": "ขอบคุณค่ะ ทางร้านจะจัดการเวลาให้ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องการจัดการคิว": "ขอบคุณค่ะ ทางร้านจะจัดการคิวให้ดีขึ้น",
    "ขอให้ปรับปรุงเรื่องการแจ้งเตือน": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งเตือน",
    "ขอให้ปรับปรุงเรื่องการแจ้งคิว": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งคิว",
    "ขอให้ปรับปรุงเรื่องการแจ้งเวลา": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งเวลา",
    "ขอให้ปรับปรุงเรื่องการแจ้งราคา": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งราคา",
    "ขอให้ปรับปรุงเรื่องการแจ้งบริการ": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งบริการ",
    "ขอให้ปรับปรุงเรื่องการแจ้งข้อมูล": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งข้อมูล",
    "ขอให้ปรับปรุงเรื่องการแจ้งช่าง": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งช่าง",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันหยุด": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันหยุด",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันเปิด": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันเปิด",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันปิด": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันปิด",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันจอง": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันจอง",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันบริการ": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันบริการ",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันโปรโมชั่น": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันโปรโมชั่น",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันนัดหมาย": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันนัดหมาย",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันรอคิว": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันรอคิว",
    "ขอให้ปรับปรุงเรื่องการแจ้งวันดูแลลูกค้า": "ขอบคุณค่ะ ทางร้านจะปรับปรุงการแจ้งวันดูแลลูกค้า",
    "ช่างทำเล็บชื่ออะไร": "ช่างของเราชื่อ คุณมิน และทีมงานค่ะ",
    "ช่างทำเล็บมีประสบการณ์กี่ปี": "ช่างมีประสบการณ์มากกว่า 5 ปีค่ะ",
    "ช่างทำเล็บจบจากที่ไหน": "จบหลักสูตรจากสถาบันทำเล็บชื่อดังค่ะ",
    "ช่างทำเล็บมีใบรับรองไหม": "มีใบรับรองจากสถาบันค่ะ",
    "ช่างทำเล็บพูดภาษาอังกฤษได้ไหม": "สามารถสื่อสารภาษาอังกฤษได้ค่ะ",
    "ช่างทำเล็บใจดีไหม": "ช่างทุกคนใจดีและเป็นกันเองค่ะ",
    "ช่างทำเล็บสุภาพไหม": "ช่างทุกคนสุภาพค่ะ",
    "ช่างทำเล็บมีความชำนาญอะไร": "ช่างชำนาญทั้งเจล อะคริลิก และ PVC ค่ะ",
    "ช่างทำเล็บมีเทคนิคพิเศษไหม": "มีค่ะ เช่น เทคนิคต่อเล็บและเพ้นท์ลาย",
    "ช่างทำเล็บมีผลงานตัวอย่างไหม": "มีค่ะ สามารถดูได้ที่เพจร้าน",
    "ช่างทำเล็บรับงานนอกสถานที่ไหม": "ขออภัยค่ะ รับเฉพาะที่ร้าน",
    "ช่างทำเล็บรับงานแต่งงานไหม": "รับค่ะ สามารถจองล่วงหน้าได้",
    "ช่างทำเล็บรับงานกลุ่มไหม": "รับค่ะ สามารถจองเป็นกลุ่มได้",
    "ช่างทำเล็บรับงานด่วนไหม": "รับค่ะ ถ้ามีคิวว่าง",
    "ช่างทำเล็บรับงานเด็กไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานผู้ชายไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานผู้สูงอายุไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเจ้าสาวไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเจ้าบ่าวไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเพ้นท์ลายไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานต่อเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานถอดเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานซ่อมเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานทาสีเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเจลไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานอะคริลิกไหม": "รับค่ะ",
    "ช่างทำเล็บรับงาน PVC ไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานสปาเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานพาราฟินไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานตกแต่งเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานล้างเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานตัดหนังไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานขัดเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานบำรุงเล็บไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานต่อเล็บเจลไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานต่อเล็บอะคริลิกไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานต่อเล็บ PVC ไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเพ้นท์ลายเจลไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเพ้นท์ลายอะคริลิกไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานเพ้นท์ลาย PVC ไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายแฟนซีไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายเรียบง่ายไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายหรูหราไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายเกาหลีไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายญี่ปุ่นไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายฝรั่งเศสไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายมินิมอลไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายดอกไม้ไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายการ์ตูนไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายคริสต์มาสไหม": "รับค่ะ",
    "ช่างทำเล็บรับงานลายวาเลนไทน์ไหม": "รับค่ะ",
    "ชำระเงินได้ทางไหนบ้าง": "รับเงินสด โอนผ่านธนาคาร และบัตรเครดิตค่ะ",
    "รับบัตรเครดิตไหม": "รับค่ะ ทุกธนาคาร",
    "รับบัตรเดบิตไหม": "รับค่ะ",
    "รับพร้อมเพย์ไหม": "รับค่ะ พร้อมเพย์ชื่อร้าน Your Nails",
    "รับโอนเงินไหม": "รับค่ะ ทุกธนาคาร",
    "รับเงินสดไหม": "รับค่ะ",
    "รับ QR Code ไหม": "รับค่ะ มี QR พร้อมเพย์ให้สแกน",
    "รับชำระผ่านแอปธนาคารไหม": "รับค่ะ ทุกแอปธนาคาร",
    "รับชำระผ่านทรูมันนี่ไหม": "รับค่ะ",
    "รับชำระผ่าน ShopeePay ไหม": "รับค่ะ",
    "รับชำระผ่าน LinePay ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรกำนัลไหม": "รับค่ะ ถ้าเป็นของห้าง",
    "รับชำระผ่านคูปองไหม": "รับค่ะ ถ้าเป็นของร้าน",
    "รับชำระผ่านบัตรสมาชิกไหม": "ขณะนี้ยังไม่มีระบบสมาชิกค่ะ",
    "รับชำระผ่านบัตรสวัสดิการไหม": "ขออภัยค่ะ ยังไม่รับบัตรสวัสดิการแห่งรัฐ",
    "รับชำระผ่านบัตรของขวัญไหม": "รับค่ะ ถ้าเป็นของห้าง",
    "รับชำระผ่านบัตรเติมเงินไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิตออนไลน์ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิตต่างประเทศไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต UnionPay ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต JCB ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต Visa ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต MasterCard ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต American Express ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต Diners Club ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต Discover ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต UOB ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต KBank ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต SCB ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต BBL ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต TMB ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต Krungsri ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต CIMB ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารออมสินไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารกรุงไทยไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารกรุงเทพไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารกสิกรไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารไทยพาณิชย์ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารทหารไทยไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารกรุงศรีไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารซีไอเอ็มบีไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารยูโอบีไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารแลนด์แอนด์เฮ้าส์ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารธนชาตไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารอาคารสงเคราะห์ไหม": "รับค่ะ",
    "รับชำระผ่านบัตรเครดิต ธนาคารอิสลามไหม": "รับค่ะ",
    "จองคิวทำเล็บยังไง": "สามารถจองคิวผ่าน LINE นี้ได้เลยค่ะ หรือโทรที่ร้านโดยตรง",
    "จองคิวล่วงหน้าได้กี่วัน": "จองล่วงหน้าได้สูงสุด 30 วันค่ะ",
    "จองคิวต้องมัดจำไหม": "บางบริการอาจต้องมัดจำค่ะ สอบถามรายละเอียดได้เลย",
    "จองคิวต้องแจ้งอะไรบ้าง": "แจ้งชื่อ วันที่ และเวลาที่ต้องการค่ะ",
    "จองคิวต้องรอนานไหม": "แล้วแต่ช่วงเวลาค่ะ ถ้าเป็นวันหยุดควรจองล่วงหน้า",
    "จองคิววันเสาร์ได้ไหม": "ได้ค่ะ เปิดบริการทุกวัน",
    "จองคิววันอาทิตย์ได้ไหม": "ได้ค่ะ เปิดบริการทุกวัน",
    "จองคิววันหยุดนักขัตฤกษ์ได้ไหม": "ได้ค่ะ เปิดบริการทุกวัน",
    "จองคิววันธรรมดาได้ไหม": "ได้ค่ะ",
    "จองคิววันไหนเร็วสุด": "ถ้าช่างว่างสามารถรับคิวได้ทันที",
    "จองคิวต้องแจ้งล่วงหน้ากี่วัน": "แนะนำจองล่วงหน้า 1-3 วันค่ะ",
    "จองคิวด่วนได้ไหม": "ได้ค่ะ ถ้าช่างว่าง",
    "จองคิวแล้วเปลี่ยนเวลาได้ไหม": "แจ้งเปลี่ยนเวลาได้ล่วงหน้าค่ะ",
    "จองคิวแล้วยกเลิกได้ไหม": "แจ้งยกเลิกได้ล่วงหน้าค่ะ",
    "จองคิวแล้วต้องรอกี่นาที": "โดยปกติไม่เกิน 10-15 นาทีค่ะ",
    "จองคิวแล้วต้องแจ้งชื่อไหม": "ต้องแจ้งชื่อเพื่อจองคิวค่ะ",
    "จองคิวแล้วต้องแจ้งเบอร์ไหม": "แจ้งเบอร์เพื่อความสะดวกในการติดต่อกลับค่ะ",
    "จองคิวแล้วต้องแจ้งบริการไหม": "แจ้งบริการที่ต้องการ เช่น ทำเล็บ ต่อขนตา",
    "จองคิวแล้วต้องแจ้งสีไหม": "แจ้งสีที่ต้องการได้เลยค่ะ",
    "จองคิวแล้วต้องแจ้งลายไหม": "แจ้งลายที่ต้องการได้เลยค่ะ",
    "จองคิวแล้วต้องแจ้งช่างไหม": "แจ้งชื่อช่างที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาไหม": "แจ้งเวลาที่สะดวกได้เลยค่ะ",
    "จองคิวแล้วต้องแจ้งวันไหม": "แจ้งวันที่ต้องการค่ะ",
    "จองคิวแล้วต้องแจ้งจำนวนคนไหม": "แจ้งจำนวนคนที่มาด้วยค่ะ",
    "จองคิวแล้วต้องแจ้งบริการเสริมไหม": "แจ้งบริการเสริมที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งโปรโมชั่นไหม": "แจ้งโปรที่ต้องการใช้ได้ค่ะ",
    "จองคิวแล้วต้องแจ้งความต้องการพิเศษไหม": "แจ้งความต้องการพิเศษได้เลยค่ะ",
    "จองคิวแล้วต้องแจ้งโรคประจำตัวไหม": "แจ้งเพื่อความปลอดภัยค่ะ",
    "จองคิวแล้วต้องแจ้งอาการแพ้ไหม": "แจ้งอาการแพ้เพื่อเลือกผลิตภัณฑ์ที่เหมาะสม",
    "จองคิวแล้วต้องแจ้งงบประมาณไหม": "แจ้งงบประมาณที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งวิธีชำระเงินไหม": "แจ้งวิธีที่สะดวกได้เลยค่ะ",
    "จองคิวแล้วต้องแจ้งช่องทางติดต่อไหม": "แจ้งช่องทางที่สะดวก เช่น LINE หรือโทรศัพท์",
    "จองคิวแล้วต้องแจ้งรูปแบบเล็บไหม": "แจ้งรูปแบบที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งความยาวเล็บไหม": "แจ้งความยาวที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งทรงเล็บไหม": "แจ้งทรงที่ต้องการได้ค่ะ",
    "จองคิวแล้วต้องแจ้งสีผิวไหม": "แจ้งเพื่อเลือกสีที่เหมาะสมได้ค่ะ",
    "จองคิวแล้วต้องแจ้งอายุไหม": "แจ้งอายุเพื่อเลือกบริการที่เหมาะสมได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเพศไหม": "แจ้งเพศเพื่อเลือกบริการที่เหมาะสมได้ค่ะ",
    "จองคิวแล้วต้องแจ้งสาขาไหม": "แจ้งสาขาที่ต้องการจองได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการเสร็จไหม": "แจ้งเวลาที่ต้องการเสร็จได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการเริ่มไหม": "แจ้งเวลาที่ต้องการเริ่มได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการพักไหม": "แจ้งเวลาที่ต้องการพักได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการกลับไหม": "แจ้งเวลาที่ต้องการกลับได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการเลิกไหม": "แจ้งเวลาที่ต้องการเลิกได้ค่ะ",
    "จองคิวแล้วต้องแจ้งเวลาที่ต้องการนัดหมายไหม": "แจ้งเวลานัดหมายที่ต้องการได้ค่ะ",
    "ทรงเล็บยอดนิยมปีนี้": "ทรงอัลมอนด์และทรงวงรีกำลังฮิตมากค่ะ",
    "ทรงเล็บอัลมอนด์คืออะไร": "ทรงอัลมอนด์คือทรงปลายมนคล้ายเมล็ดอัลมอนด์ สวยเรียวค่ะ",
    "ทรงเล็บวงรีคืออะไร": "ทรงวงรีคือทรงปลายมนโค้งมน ดูสุภาพและเรียบหรู",
    "ทรงเล็บสี่เหลี่ยมคืออะไร": "ทรงสี่เหลี่ยมคือทรงปลายตรง เหมาะกับคนชอบลุคเท่ ๆ",
    "ทรงเล็บสี่เหลี่ยมมนคืออะไร": "ทรงสี่เหลี่ยมมนคือปลายตรงแต่ขอบมน ดูน่ารัก",
    "ทรงเล็บทรงตรงคืออะไร": "ทรงตรงคือปลายเล็บตรงทั้งสองข้าง ดูเรียบง่าย",
    "ทรงเล็บทรงแหลมคืออะไร": "ทรงแหลมคือปลายเล็บแหลม ดูโดดเด่นและแฟชั่น",
    "ทรงเล็บทรงบัลเลต์คืออะไร": "ทรงบัลเลต์คือปลายตรงและขอบมนคล้ายรองเท้าบัลเลต์",
    "ทรงเล็บทรงสควอวอลคืออะไร": "ทรงสควอวอลคือทรงสี่เหลี่ยมมน ดูเรียบหรู",
    "ทรงเล็บทรงสติลเลโต้คืออะไร": "ทรงสติลเลโต้คือปลายแหลมมาก ดูแฟชั่นสุด ๆ",
    "ทรงเล็บทรงคอฟฟินคืออะไร": "ทรงคอฟฟินคือปลายตรงและขอบมนคล้ายโลงศพ ดูเท่",
    "ทรงเล็บทรงราวด์คืออะไร": "ทรงราวด์คือปลายมนโค้ง ดูสุภาพ",
    "ทรงเล็บทรงพอยต์คืออะไร": "ทรงพอยต์คือปลายแหลม ดูโดดเด่น",
    "ทรงเล็บทรงฟลาร์คืออะไร": "ทรงฟลาร์คือปลายกว้าง ดูแปลกใหม่",
    "ทรงเล็บทรงลิปสติกคืออะไร": "ทรงลิปสติกคือปลายเฉียงคล้ายลิปสติก",
    "ทรงเล็บทรงเมาน์เทนพีคคืออะไร": "ทรงเมาน์เทนพีคคือปลายแหลมคล้ายยอดเขา",
    "ทรงเล็บทรงเอจคืออะไร": "ทรงเอจคือปลายแหลมและขอบเฉียง ดูแฟชั่น",
    "ทรงเล็บทรงพีคคืออะไร": "ทรงพีคคือปลายแหลมสูง ดูโดดเด่น",
    "ทรงเล็บทรงฟลิปคืออะไร": "ทรงฟลิปคือปลายโค้งขึ้น ดูแปลกใหม่",
    "ทรงเล็บทรงฟลูทคืออะไร": "ทรงฟลูทคือปลายโค้งลง ดูน่ารัก",
    "ทรงเล็บทรงสแควร์คืออะไร": "ทรงสแควร์คือปลายตรง ดูเรียบง่าย",
    "ทรงเล็บทรงโอวอลคืออะไร": "ทรงโอวอลคือปลายมนโค้ง ดูสุภาพ",
    "ทรงเล็บทรงสควอวอลเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคเรียบหรู",
    "ทรงเล็บทรงอัลมอนด์เหมาะกับใคร": "เหมาะกับคนที่อยากให้มือดูเรียวยาว",
    "ทรงเล็บทรงวงรีเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคสุภาพ",
    "ทรงเล็บทรงสี่เหลี่ยมเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคเท่ ๆ",
    "ทรงเล็บทรงแหลมเหมาะกับใคร": "เหมาะกับคนที่ชอบแฟชั่นโดดเด่น",
    "ทรงเล็บทรงบัลเลต์เหมาะกับใคร": "เหมาะกับคนที่ชอบลุคหวาน",
    "ทรงเล็บทรงคอฟฟินเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคเท่และแปลกใหม่",
    "ทรงเล็บทรงราวด์เหมาะกับใคร": "เหมาะกับคนที่ชอบลุคสุภาพ",
    "ทรงเล็บทรงพอยต์เหมาะกับใคร": "เหมาะกับคนที่ชอบลุคโดดเด่น",
    "ทรงเล็บทรงฟลาร์เหมาะกับใคร": "เหมาะกับคนที่ชอบลุคแปลกใหม่",
    "ทรงเล็บทรงลิปสติกเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคแฟชั่น",
    "ทรงเล็บทรงเมาน์เทนพีคเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคโดดเด่น",
    "ทรงเล็บทรงเอจเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคแฟชั่น",
    "ทรงเล็บทรงพีคเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคโดดเด่น",
    "ทรงเล็บทรงฟลิปเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคแปลกใหม่",
    "ทรงเล็บทรงฟลูทเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคน่ารัก",
    "ทรงเล็บทรงสแควร์เหมาะกับใคร": "เหมาะกับคนที่ชอบลุคเรียบง่าย",
    "ทรงเล็บทรงโอวอลเหมาะกับใคร": "เหมาะกับคนที่ชอบลุคสุภาพ",
    "ทรงเล็บทรงไหนเหมาะกับมือเล็ก": "ทรงอัลมอนด์และวงรีจะช่วยให้มือดูเรียวยาว",
    "ทรงเล็บทรงไหนเหมาะกับมือใหญ่": "ทรงสี่เหลี่ยมหรือคอฟฟินจะช่วยให้มือดูเล็กลง",
    "ทรงเล็บทรงไหนเหมาะกับนิ้วยาว": "ทรงสแควร์และอัลมอนด์จะดูสวย",
    "ทรงเล็บทรงไหนเหมาะกับนิ้วสั้น": "ทรงวงรีและราวด์จะช่วยให้ดูเรียวยาว",
    "ทรงเล็บทรงไหนเหมาะกับคนทำงาน": "ทรงตรงและสแควร์ดูสุภาพ",
    "ทรงเล็บทรงไหนเหมาะกับไปงาน": "ทรงอัลมอนด์และคอฟฟินดูหรู",
    "ทรงเล็บทรงไหนเหมาะกับไปเที่ยว": "ทรงแหลมและลิปสติกดูแฟชั่น",
    "ทรงเล็บทรงไหนเหมาะกับไปงานแต่ง": "ทรงวงรีและอัลมอนด์ดูสุภาพ",
    "ทรงเล็บทรงไหนเหมาะกับไปสัมภาษณ์งาน": "ทรงตรงและสแควร์ดูสุภาพ",
    "ต่อเล็บเจลคืออะไร": "ต่อเล็บเจลคือการใช้เจลพิเศษปั้นขึ้นรูปบนเล็บจริงแล้วอบด้วยแสง UV หรือ LED ค่ะ",
    "ต่อเล็บเจลทนไหม": "ทนค่ะ อยู่ได้ประมาณ 3-4 สัปดาห์",
    "ต่อเล็บเจลราคาเท่าไหร่": "เริ่มต้น 899 บาทค่ะ",
    "ต่อเล็บเจลเจ็บไหม": "ไม่เจ็บเลยค่ะ ช่างมือเบามาก",
    "ต่อเล็บเจลอยู่ได้นานแค่ไหน": "ประมาณ 3-4 สัปดาห์ค่ะ",
    "ต่อเล็บเจลเหมาะกับใคร": "เหมาะกับคนที่ต้องการเล็บเงาสวยและติดทนนาน",
    "ต่อเล็บเจลมีสีอะไรบ้าง": "มีให้เลือกมากกว่า 200 สีค่ะ",
    "ต่อเล็บเจลมีลายอะไรบ้าง": "มีลายแฟชั่น มินิมอล และลายการ์ตูนค่ะ",
    "ต่อเล็บเจลต้องดูแลยังไง": "ควรบำรุงด้วยออยล์และหลีกเลี่ยงน้ำแรง ๆ",
    "ต่อเล็บเจลถอดเองได้ไหม": "แนะนำให้มาถอดที่ร้านเพื่อความปลอดภัยค่ะ",
    "ต่อเล็บเจลแตกซ่อมได้ไหม": "ซ่อมได้ค่ะ ช่างจะปั้นใหม่ให้",
    "ต่อเล็บเจลทำสีเจลได้ไหม": "ได้ค่ะ สามารถทาสีเจลบนเล็บเจลได้เลย",
    "ต่อเล็บเจลทำลายพิเศษได้ไหม": "ได้ค่ะ มีบริการเพนต์ลายและติดเพชร",
    "ต่อเล็บเจลทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บเจลทำลายคริสต์มาสได้ไหม": "ได้ค่ะ มีลายคริสต์มาสน่ารัก ๆ",
    "ต่อเล็บเจลทำลายวาเลนไทน์ได้ไหม": "ได้ค่ะ มีลายหัวใจและชมพูฟรุ้งฟริ้ง",
    "ต่อเล็บเจลทำลายปีใหม่ได้ไหม": "ได้ค่ะ มีลายกลิตเตอร์และสีทอง",
    "ต่อเล็บเจลทำลายฮาโลวีนได้ไหม": "ได้ค่ะ มีลายฟักทองและผีเก๋ ๆ",
    "ต่อเล็บเจลทำลายการ์ตูนได้ไหม": "ได้ค่ะ มีลายซานริโอ มิกกี้ ฯลฯ",
    "ต่อเล็บเจลทำลายมุกได้ไหม": "ได้ค่ะ มีสีมุกและลายมุก",
    "ต่อเล็บเจลทำลายวาวได้ไหม": "ได้ค่ะ มีสีแม่เหล็กและกลิตเตอร์",
    "ต่อเล็บเจลทำลายแฟชั่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นมากมาย",
    "ต่อเล็บเจลทำลายธรรมชาติได้ไหม": "ได้ค่ะ มีสีเขียว น้ำตาล และลายใบไม้",
    "ต่อเล็บเจลทำลายสปาได้ไหม": "ได้ค่ะ มีลายสปามือและเท้า",
    "ต่อเล็บเจลทำลายนวดได้ไหม": "ได้ค่ะ มีลายผ่อนคลาย",
    "ต่อเล็บเจลทำลายเล็บได้ไหม": "ได้ค่ะ มีลายเล็บหลากหลาย",
    "ต่อเล็บเจลทำลายขนตาได้ไหม": "ได้ค่ะ มีลายขนตาแฟชั่น",
    "ต่อเล็บเจลทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บเจลทำลายเจ้าบ่าวได้ไหม": "ได้ค่ะ มีลายสุภาพสำหรับผู้ชาย",
    "ต่อเล็บเจลทำลายเด็กได้ไหม": "ได้ค่ะ มีลายการ์ตูนและสีสดใส",
    "ต่อเล็บเจลทำลายผู้ใหญ่ได้ไหม": "ได้ค่ะ มีลายสุภาพและสีพาสเทล",
    "ต่อเล็บเจลทำลายวัยรุ่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นและสีสดใส",
    "ต่อเล็บเจลทำลายผู้สูงอายุได้ไหม": "ได้ค่ะ มีลายสุภาพและสีโทนนู้ด",
    "ต่อเล็บเจลทำลายเพื่อน": "ได้ค่ะ มีลายคู่เพื่อนและลายสนุก ๆ",
    "ต่อเล็บเจลทำลายครอบครัว": "ได้ค่ะ มีลายสำหรับทุกวัย",
    "ต่อเล็บเจลทำลายคู่รัก": "ได้ค่ะ มีลายหัวใจและลายคู่",
    "ต่อเล็บเจลถอดออกยากไหม": "ไม่ยากค่ะ ช่างจะถอดให้แบบปลอดภัย",
    "ต่อเล็บเจลทำให้เล็บจริงเสียไหม": "ไม่เสียค่ะ ถ้าดูแลและถอดถูกวิธี",
    "ต่อเล็บเจลต้องพักเล็บไหม": "ควรพักเล็บบ้างทุก 2-3 เดือน",
    "ต่อเล็บเจลทำเล็บเท้าได้ไหม": "ได้ค่ะ มีบริการต่อเจลที่เล็บเท้า",
    "ต่อเล็บเจลทำเล็บมือได้ไหม": "ได้ค่ะ มีบริการต่อเจลที่เล็บมือ",
    "ต่อเล็บเจลทำเล็บพร้อมกันได้ไหม": "ได้ค่ะ สามารถทำมือและเท้าพร้อมกัน",
    "ต่อเล็บเจลมีแบบสั้นไหม": "มีค่ะ เลือกความยาวได้ตามต้องการ",
    "ต่อเล็บเจลมีแบบยาวไหม": "มีค่ะ ต่อได้ยาวตามต้องการ",
    "ต่อเล็บเจลมีแบบใสไหม": "มีค่ะ เจลใสดูธรรมชาติ",
    "ต่อเล็บเจลมีแบบสีพื้นไหม": "มีค่ะ สีพื้นหลากหลาย",
    "ต่อเล็บเจลมีแบบกลิตเตอร์ไหม": "มีค่ะ สีวิบวับและกลิตเตอร์",
    "ต่อเล็บเจลมีแบบเพชรไหม": "มีค่ะ ติดเพชรได้ทุกแบบ",
    "ต่อเล็บเจลมีแบบลายการ์ตูนไหม": "มีค่ะ ลายการ์ตูนมากมาย",
    "ต่อเล็บเจลมีแบบลายแฟชั่นไหม": "มีค่ะ ลายแฟชั่นหลากหลาย",
    "ต่อเล็บเจลมีแบบลายธรรมชาติไหม": "มีค่ะ ลายใบไม้ ดอกไม้ และสีเขียว",
    "ต่อเล็บอะคริลิคคืออะไร": "ต่อเล็บอะคริลิคคือการใช้ผงอะคริลิคผสมกับน้ำยาแล้วปั้นขึ้นรูปบนเล็บจริงค่ะ",
    "ต่อเล็บอะคริลิคทนไหม": "ทนมากค่ะ อยู่ได้ 3-4 สัปดาห์",
    "ต่อเล็บอะคริลิคราคาเท่าไหร่": "เริ่มต้น 999 บาทค่ะ",
    "ต่อเล็บอะคริลิคเจ็บไหม": "ไม่เจ็บเลยค่ะ ช่างมือเบามาก",
    "ต่อเล็บอะคริลิคอยู่ได้นานแค่ไหน": "ประมาณ 3-4 สัปดาห์ค่ะ",
    "ต่อเล็บอะคริลิคเหมาะกับใคร": "เหมาะกับคนที่ต้องการเล็บแข็งแรงและต่อยาว",
    "ต่อเล็บอะคริลิคมีสีอะไรบ้าง": "มีให้เลือกมากกว่า 100 สีค่ะ",
    "ต่อเล็บอะคริลิคมีลายอะไรบ้าง": "มีลายแฟชั่น มินิมอล และลายการ์ตูนค่ะ",
    "ต่อเล็บอะคริลิคต้องดูแลยังไง": "ควรบำรุงด้วยออยล์และหลีกเลี่ยงน้ำแรง ๆ",
    "ต่อเล็บอะคริลิคถอดเองได้ไหม": "แนะนำให้มาถอดที่ร้านเพื่อความปลอดภัยค่ะ",
    "ต่อเล็บอะคริลิคแตกซ่อมได้ไหม": "ซ่อมได้ค่ะ ช่างจะปั้นใหม่ให้",
    "ต่อเล็บอะคริลิคทำสีเจลได้ไหม": "ได้ค่ะ สามารถทาสีเจลบนอะคริลิคได้เลย",
    "ต่อเล็บอะคริลิคทำลายพิเศษได้ไหม": "ได้ค่ะ มีบริการเพนต์ลายและติดเพชร",
    "ต่อเล็บอะคริลิคทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บอะคริลิคทำลายคริสต์มาสได้ไหม": "ได้ค่ะ มีลายคริสต์มาสน่ารัก ๆ",
    "ต่อเล็บอะคริลิคทำลายวาเลนไทน์ได้ไหม": "ได้ค่ะ มีลายหัวใจและชมพูฟรุ้งฟริ้ง",
    "ต่อเล็บอะคริลิคทำลายปีใหม่ได้ไหม": "ได้ค่ะ มีลายกลิตเตอร์และสีทอง",
    "ต่อเล็บอะคริลิคทำลายฮาโลวีนได้ไหม": "ได้ค่ะ มีลายฟักทองและผีเก๋ ๆ",
    "ต่อเล็บอะคริลิคทำลายการ์ตูนได้ไหม": "ได้ค่ะ มีลายซานริโอ มิกกี้ ฯลฯ",
    "ต่อเล็บอะคริลิคทำลายมุกได้ไหม": "ได้ค่ะ มีสีมุกและลายมุก",
    "ต่อเล็บอะคริลิคทำลายวาวได้ไหม": "ได้ค่ะ มีสีแม่เหล็กและกลิตเตอร์",
    "ต่อเล็บอะคริลิคทำลายแฟชั่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นมากมาย",
    "ต่อเล็บอะคริลิคทำลายธรรมชาติได้ไหม": "ได้ค่ะ มีสีเขียว น้ำตาล และลายใบไม้",
    "ต่อเล็บอะคริลิคทำลายสปาได้ไหม": "ได้ค่ะ มีลายสปามือและเท้า",
    "ต่อเล็บอะคริลิคทำลายนวดได้ไหม": "ได้ค่ะ มีลายผ่อนคลาย",
    "ต่อเล็บอะคริลิคทำลายเล็บได้ไหม": "ได้ค่ะ มีลายเล็บหลากหลาย",
    "ต่อเล็บอะคริลิคทำลายขนตาได้ไหม": "ได้ค่ะ มีลายขนตาแฟชั่น",
    "ต่อเล็บอะคริลิคทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บอะคริลิคทำลายเจ้าบ่าวได้ไหม": "ได้ค่ะ มีลายสุภาพสำหรับผู้ชาย",
    "ต่อเล็บอะคริลิคทำลายเด็กได้ไหม": "ได้ค่ะ มีลายการ์ตูนและสีสดใส",
    "ต่อเล็บอะคริลิคทำลายผู้ใหญ่ได้ไหม": "ได้ค่ะ มีลายสุภาพและสีพาสเทล",
    "ต่อเล็บอะคริลิคทำลายวัยรุ่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นและสีสดใส",
    "ต่อเล็บอะคริลิคทำลายผู้สูงอายุได้ไหม": "ได้ค่ะ มีลายสุภาพและสีโทนนู้ด",
    "ต่อเล็บอะคริลิคทำลายเพื่อน": "ได้ค่ะ มีลายคู่เพื่อนและลายสนุก ๆ",
    "ต่อเล็บอะคริลิคทำลายครอบครัว": "ได้ค่ะ มีลายสำหรับทุกวัย",
    "ต่อเล็บอะคริลิคทำลายคู่รัก": "ได้ค่ะ มีลายหัวใจและลายคู่",
    "ต่อเล็บอะคริลิคถอดออกยากไหม": "ไม่ยากค่ะ ช่างจะถอดให้แบบปลอดภัย",
    "ต่อเล็บอะคริลิคทำให้เล็บจริงเสียไหม": "ไม่เสียค่ะ ถ้าดูแลและถอดถูกวิธี",
    "ต่อเล็บอะคริลิคต้องพักเล็บไหม": "ควรพักเล็บบ้างทุก 2-3 เดือน",
    "ต่อเล็บอะคริลิคทำเล็บเท้าได้ไหม": "ได้ค่ะ มีบริการต่ออะคริลิคที่เล็บเท้า",
    "ต่อเล็บอะคริลิคทำเล็บมือได้ไหม": "ได้ค่ะ มีบริการต่ออะคริลิคที่เล็บมือ",
    "ต่อเล็บอะคริลิคทำเล็บพร้อมกันได้ไหม": "ได้ค่ะ สามารถทำมือและเท้าพร้อมกัน",
    "ต่อเล็บอะคริลิคมีแบบสั้นไหม": "มีค่ะ เลือกความยาวได้ตามต้องการ",
    "ต่อเล็บอะคริลิคมีแบบยาวไหม": "มีค่ะ ต่อได้ยาวตามต้องการ",
    "ต่อเล็บอะคริลิคมีแบบใสไหม": "มีค่ะ อะคริลิคใสดูธรรมชาติ",
    "ต่อเล็บอะคริลิคมีแบบสีพื้นไหม": "มีค่ะ สีพื้นหลากหลาย",
    "ต่อเล็บอะคริลิคมีแบบกลิตเตอร์ไหม": "มีค่ะ สีวิบวับและกลิตเตอร์",
    "ต่อเล็บอะคริลิคมีแบบเพชรไหม": "มีค่ะ ติดเพชรได้ทุกแบบ",
    "ต่อเล็บอะคริลิคมีแบบลายการ์ตูนไหม": "มีค่ะ ลายการ์ตูนมากมาย",
    "ต่อเล็บอะคริลิคมีแบบลายแฟชั่นไหม": "มีค่ะ ลายแฟชั่นหลากหลาย",
    "ต่อเล็บอะคริลิคมีแบบลายธรรมชาติไหม": "มีค่ะ ลายใบไม้ ดอกไม้ และสีเขียว",
    "ต่อเล็บ pvc คืออะไร": "ต่อเล็บ PVC คือการติดเล็บปลอมแบบ PVC ลงบนเล็บจริงค่ะ",
    "ต่อเล็บ pvc ทนไหม": "ทนค่ะ ถ้าดูแลดีอยู่ได้ 2-3 สัปดาห์",
    "ต่อเล็บ pvc ราคาเท่าไหร่": "เริ่มต้น 399 บาทค่ะ",
    "ต่อเล็บ pvc เจ็บไหม": "ไม่เจ็บเลยค่ะ ช่างมือเบามาก",
    "ต่อเล็บ pvc อยู่ได้นานแค่ไหน": "ประมาณ 2-3 สัปดาห์ค่ะ",
    "ต่อเล็บ pvc เหมาะกับใคร": "เหมาะกับคนที่อยากเปลี่ยนลุคเล็บชั่วคราว",
    "ต่อเล็บ pvc มีสีอะไรบ้าง": "มีให้เลือกมากกว่า 100 สีค่ะ",
    "ต่อเล็บ pvc มีลายอะไรบ้าง": "มีลายแฟชั่น มินิมอล และลายการ์ตูนค่ะ",
    "ต่อเล็บ pvc ต้องดูแลยังไง": "ควรหลีกเลี่ยงน้ำแรง ๆ และบำรุงด้วยออยล์ค่ะ",
    "ต่อเล็บ pvc ถอดเองได้ไหม": "แนะนำให้มาถอดที่ร้านเพื่อความปลอดภัยค่ะ",
    "ต่อเล็บ pvc แตกซ่อมได้ไหม": "ซ่อมได้ค่ะ ช่างจะเปลี่ยนแผ่นใหม่ให้",
    "ต่อเล็บ pvc ทำสีเจลได้ไหม": "ได้ค่ะ สามารถทาสีเจลบน PVC ได้เลย",
    "ต่อเล็บ pvc ทำลายพิเศษได้ไหม": "ได้ค่ะ มีบริการเพนต์ลายและติดเพชร",
    "ต่อเล็บ pvc ทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บ pvc ทำลายคริสต์มาสได้ไหม": "ได้ค่ะ มีลายคริสต์มาสน่ารัก ๆ",
    "ต่อเล็บ pvc ทำลายวาเลนไทน์ได้ไหม": "ได้ค่ะ มีลายหัวใจและชมพูฟรุ้งฟริ้ง",
    "ต่อเล็บ pvc ทำลายปีใหม่ได้ไหม": "ได้ค่ะ มีลายกลิตเตอร์และสีทอง",
    "ต่อเล็บ pvc ทำลายฮาโลวีนได้ไหม": "ได้ค่ะ มีลายฟักทองและผีเก๋ ๆ",
    "ต่อเล็บ pvc ทำลายการ์ตูนได้ไหม": "ได้ค่ะ มีลายซานริโอ มิกกี้ ฯลฯ",
    "ต่อเล็บ pvc ทำลายมุกได้ไหม": "ได้ค่ะ มีสีมุกและลายมุก",
    "ต่อเล็บ pvc ทำลายวาวได้ไหม": "ได้ค่ะ มีสีแม่เหล็กและกลิตเตอร์",
    "ต่อเล็บ pvc ทำลายแฟชั่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นมากมาย",
    "ต่อเล็บ pvc ทำลายธรรมชาติได้ไหม": "ได้ค่ะ มีสีเขียว น้ำตาล และลายใบไม้",
    "ต่อเล็บ pvc ทำลายสปาได้ไหม": "ได้ค่ะ มีลายสปามือและเท้า",
    "ต่อเล็บ pvc ทำลายนวดได้ไหม": "ได้ค่ะ มีลายผ่อนคลาย",
    "ต่อเล็บ pvc ทำลายเล็บได้ไหม": "ได้ค่ะ มีลายเล็บหลากหลาย",
    "ต่อเล็บ pvc ทำลายขนตาได้ไหม": "ได้ค่ะ มีลายขนตาแฟชั่น",
    "ต่อเล็บ pvc ทำลายเจ้าสาวได้ไหม": "ได้ค่ะ มีลายเจ้าสาวให้เลือก",
    "ต่อเล็บ pvc ทำลายเจ้าบ่าวได้ไหม": "ได้ค่ะ มีลายสุภาพสำหรับผู้ชาย",
    "ต่อเล็บ pvc ทำลายเด็กได้ไหม": "ได้ค่ะ มีลายการ์ตูนและสีสดใส",
    "ต่อเล็บ pvc ทำลายผู้ใหญ่ได้ไหม": "ได้ค่ะ มีลายสุภาพและสีพาสเทล",
    "ต่อเล็บ pvc ทำลายวัยรุ่นได้ไหม": "ได้ค่ะ มีลายแฟชั่นและสีสดใส",
    "ต่อเล็บ pvc ทำลายผู้สูงอายุได้ไหม": "ได้ค่ะ มีลายสุภาพและสีโทนนู้ด",
    "ต่อเล็บ pvc ทำลายเพื่อน": "ได้ค่ะ มีลายคู่เพื่อนและลายสนุก ๆ",
    "ต่อเล็บ pvc ทำลายครอบครัว": "ได้ค่ะ มีลายสำหรับทุกวัย",
    "ต่อเล็บ pvc ทำลายคู่รัก": "ได้ค่ะ มีลายหัวใจและลายคู่",
    "ต่อเล็บ pvc ถอดออกยากไหม": "ไม่ยากค่ะ ช่างจะถอดให้แบบปลอดภัย",
    "ต่อเล็บ pvc ทำให้เล็บจริงเสียไหม": "ไม่เสียค่ะ ถ้าดูแลและถอดถูกวิธี",
    "ต่อเล็บ pvc ต้องพักเล็บไหม": "ควรพักเล็บบ้างทุก 2-3 เดือน",
    "ต่อเล็บ pvc ทำเล็บเท้าได้ไหม": "ได้ค่ะ มีบริการต่อ PVC ที่เล็บเท้า",
    "ต่อเล็บ pvc ทำเล็บมือได้ไหม": "ได้ค่ะ มีบริการต่อ PVC ที่เล็บมือ",
    "ต่อเล็บ pvc ทำเล็บพร้อมกันได้ไหม": "ได้ค่ะ สามารถทำมือและเท้าพร้อมกัน",
    "ต่อเล็บ pvc มีแบบสั้นไหม": "มีค่ะ เลือกความยาวได้ตามต้องการ",
    "ต่อเล็บ pvc มีแบบยาวไหม": "มีค่ะ ต่อได้ยาวตามต้องการ",
    "ต่อเล็บ pvc มีแบบใสไหม": "มีค่ะ PVC ใสดูธรรมชาติ",
    "ต่อเล็บ pvc มีแบบสีพื้นไหม": "มีค่ะ สีพื้นหลากหลาย",
    "ต่อเล็บ pvc มีแบบกลิตเตอร์ไหม": "มีค่ะ สีวิบวับและกลิตเตอร์",
    "ต่อเล็บ pvc มีแบบเพชรไหม": "มีค่ะ ติดเพชรได้ทุกแบบ",
    "ต่อเล็บ pvc มีแบบลายการ์ตูนไหม": "มีค่ะ ลายการ์ตูนมากมาย",
    "ต่อเล็บ pvc มีแบบลายแฟชั่นไหม": "มีค่ะ ลายแฟชั่นหลากหลาย",
    "ต่อเล็บ pvc มีแบบลายธรรมชาติไหม": "มีค่ะ ลายใบไม้ ดอกไม้ และสีเขียว",
    "ต่อเล็บแบบธรรมชาติราคาเท่าไหร่": "เริ่มต้น 899 บาทค่ะ 💅",
    "ต่อเล็บอะคริลิคดีไหม": "ดีค่ะ แข็งแรงและต่อยาวได้มาก",
    "ต่อเล็บเจลดีไหม": "ดีค่ะ เงาสวยและติดทนนาน",
    "ต่อเล็บแบบไหนทนสุด": "อะคริลิคจะทนสุดค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับมือเล็ก": "แนะนำทรงอัลมอนด์หรือวงรีค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับมือใหญ่": "ทรงสี่เหลี่ยมหรือทรงตรงจะเหมาะค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับเจ้าสาว": "ทรงอัลมอนด์หรือวงรี สีขาวมุกสวยมากค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับวัยรุ่น": "ทรงสั้นมินิมอลหรือสีพาสเทลกำลังฮิตค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับผู้ใหญ่": "ทรงวงรีหรือทรงตรง สีสุภาพดูดีค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับคนทำงาน": "ทรงตรงหรือทรงสี่เหลี่ยม สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงาน": "ทรงอัลมอนด์หรือทรงยาว สีมุกหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปเที่ยว": "ทรงสั้น สีสดใส ลายแฟชั่นค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปทะเล": "ทรงวงรี สีฟ้า ขาว หรือเปลือกหอยค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานแต่ง": "ทรงอัลมอนด์ สีขาวมุกหรือชมพูอ่อนค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปสัมภาษณ์งาน": "ทรงตรง สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปเรียน": "ทรงสั้น สีสุภาพ เช่น พีช นู้ดค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปปาร์ตี้": "ทรงยาว สีสดใส กลิตเตอร์หรือเพชรค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปออกงาน": "ทรงอัลมอนด์ สีมุกหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปถ่ายรูป": "ทรงยาว สีสดใสหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปต่างประเทศ": "ทรงยาว สีโทนสุภาพหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานบริษัท": "ทรงตรง สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเลี้ยง": "ทรงอัลมอนด์ สีมุกหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานรับปริญญา": "ทรงตรง สีขาวมุกหรือชมพูอ่อนค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานวันเกิด": "ทรงยาว สีสดใส กลิตเตอร์หรือเพชรค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานปีใหม่": "ทรงอัลมอนด์ สีทองหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานคริสต์มาส": "ทรงวงรี สีแดง เขียว หรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานวาเลนไทน์": "ทรงอัลมอนด์ สีชมพูหรือกลิตเตอร์หัวใจค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานฮาโลวีน": "ทรงยาว สีดำ ส้ม หรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานการ์ตูน": "ทรงสั้น สีสดใส ลายการ์ตูนค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานมุก": "ทรงวงรี สีมุกหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานวาว": "ทรงยาว สีแม่เหล็กหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานแฟชั่น": "ทรงยาว สีสดใส ลายแฟชั่นค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานธรรมชาติ": "ทรงสั้น สีเขียว น้ำตาล หรือโทนธรรมชาติค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานบริษัท": "ทรงตรง สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานสปา": "ทรงวงรี สีสุภาพหรือสีพาสเทลค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานนวด": "ทรงสั้น สีสุภาพหรือสีพาสเทลค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเล็บ": "ทรงอัลมอนด์ สีสดใสหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานขนตา": "ทรงยาว สีสุภาพหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเจ้าสาว": "ทรงอัลมอนด์ สีขาวมุกหรือชมพูอ่อนค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเจ้าบ่าว": "ทรงตรง สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเด็ก": "ทรงสั้น สีสดใส ลายการ์ตูนค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานผู้ใหญ่": "ทรงวงรี สีสุภาพหรือสีพาสเทลค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานวัยรุ่น": "ทรงสั้น สีสดใส ลายแฟชั่นค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานผู้สูงอายุ": "ทรงตรง สีโทนนู้ดสุภาพค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานเพื่อน": "ทรงอัลมอนด์ สีสดใสหรือกลิตเตอร์ค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานครอบครัว": "ทรงวงรี สีสุภาพหรือสีพาสเทลค่ะ",
    "ต่อเล็บแบบไหนเหมาะกับไปงานคู่รัก": "ทรงสั้น สีชมพูหรือกลิตเตอร์หัวใจค่ะ",
    "ต่อเล็บแบบไหนดี": "ขึ้นอยู่กับความยาวและลุคที่ต้องการเลยค่ะ 💅",
    "สีเล็บยอดนิยมปีนี้": "สีพาสเทลและโทนชมพูยังคงฮิตมากค่ะ 💅",
    "ทำเล็บเจลกับอะคริลิคต่างกันยังไง": "เจลจะเงาและติดทนนานกว่า ส่วนอะคริลิคแข็งแรงและต่อยาวได้มากค่ะ",
    "เล็บเจลอยู่ได้นานแค่ไหน": "ประมาณ 3-4 สัปดาห์ค่ะ 💅",
    "ล้างเล็บเจลใช้เวลานานไหม": "ประมาณ 15 นาทีค่ะ",
    "ต่อเล็บใช้เวลานานไหม": "ประมาณ 1-1.5 ชั่วโมงค่ะ 💅",
    "ทำเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ ช่างมือเบามาก 💕",
    "ต่อเล็บเจ็บไหม": "ไม่เจ็บเลยค่ะ นุ่มนวลทุกขั้นตอน 💅",
    "เล็บบางทำเล็บเจลได้ไหม": "ได้ค่ะ ใช้เบสสูตรอ่อนโยน ปลอดภัยแน่นอน 💅",
    "เล็บหักทำเล็บได้ไหม": "ได้ค่ะ ซ่อมให้ก่อนต่อ 💪",
    "เล็บสั้นต่อได้ไหม": "ได้ค่ะ ทำให้ดูเรียวยาวธรรมชาติเลย 💅",
    "เล็บยาวมากตัดได้ไหม": "ได้ค่ะ ปรับทรงให้ฟรีเลย ✂️",
    "เล็บพังจากที่อื่นมาซ่อมได้ไหม": "ได้ค่ะ เดี๋ยวช่างดูให้ก่อน 💖",
    "อยากได้ลายเล็บน่ารักๆ": "มีเยอะเลยค่ะ ทั้งมินิมอล พาสเทล การ์ตูน 💕",
    "อยากได้เล็บเรียบหรู": "แนะนำโทนขาวครีม นู้ดทอง ดูแพงมาก 💅",
    "อยากได้เล็บสายฝอ": "แนะนำเล็บยาวเจลใสเพชรแน่น ๆ ค่ะ 💎",
    "อยากได้เล็บแบบเจ้าสาว": "มีแพ็กเกจเจ้าสาวพิเศษเริ่มต้น 1,299 บาทค่ะ 💍",
    "อยากได้เล็บสีใส": "มีค่ะ สีเจลใสธรรมชาติสุด ๆ 💅",
    "อยากได้เล็บสีขาว": "มีค่ะ สีขาวมุกหรือขาวนมก็สวยมาก ✨",
    "อยากได้เล็บสีชมพู": "มีหลายเฉดเลยค่ะ ทั้งพีช พาสเทล หวานสุด ๆ 💖",
    "อยากได้เล็บโทนเข้ม": "มีค่ะ เช่น น้ำตาล ดำ แดงเบอร์กันดี สวยมาก 💅",
    "อยากทำเล็บลายเกาหลี": "มีค่ะ ลายมินิมอลแบบเกาหลีเพียบเลย 💕",
    "อยากทำเล็บลายญี่ปุ่น": "มีค่ะ ลายคิ้วท์น่ารักสุด ๆ 🎀",
    "อยากทำเล็บลายมินิมอล": "ได้เลยค่ะ เรียบง่ายแต่ดูดี 💅",
    "อยากทำเล็บลายหินอ่อน": "มีค่ะ ลายหินอ่อนสุดหรู ✨",
    "อยากทำเล็บลายกลิตเตอร์": "มีค่ะ วิบวับสุด ๆ 💎",
    "อยากทำเล็บลายเพชร": "มีค่ะ ติดเพชร Swarovski สวยหรูเลย 💍",
    "อยากทำเล็บลายคริสต์มาส": "มีค่ะ ลายน่ารักมาก 🎄",
    "อยากทำเล็บลายปีใหม่": "มีค่ะ วิบวับรับปีใหม่เลย ✨",
    "อยากทำเล็บลายวาเลนไทน์": "มีค่ะ หัวใจชมพูฟรุ้งฟริ้ง 💕",
    "อยากทำเล็บลายฮาโลวีน": "มีค่ะ ลายฟักทอง ผีเก๋ ๆ 👻",
    "อยากทำเล็บลายการ์ตูน": "มีค่ะ ลายซานริโอ มิกกี้ และอีกเพียบ 🎨",
    "อยากทำเล็บลายมุก": "มีค่ะ สีมุกเงาๆ กำลังฮิต 💅",
    "อยากทำเล็บลายวาวๆ": "มีค่ะ สีแม่เหล็กวิ้งมาก 🧲",
    "เล็บพังจากเจลทำไงดี": "พักเล็บ 1-2 สัปดาห์แล้วบำรุงด้วยออยล์ค่ะ 💖",
    "บำรุงเล็บยังไงดี": "ใช้ cuticle oil และครีมบำรุงทุกวันค่ะ 💅",
    "ทำเล็บบ่อย ๆ จะบางไหม": "ถ้าทำถูกวิธีไม่บางค่ะ 💕",
    "ควรพักเล็บนานเท่าไหร่": "ทุก 2-3 เดือนควรพักสัก 1 สัปดาห์ค่ะ 💅🏻",
    "ใช้ครีมบำรุงเล็บอะไรดี": "ใช้ครีมน้ำมันหรือเซรั่มบำรุงจมูกเล็บได้เลยค่ะ 💧",
    "หลังทำเล็บควรดูแลยังไง": "หลีกเลี่ยงน้ำแรง ๆ และใช้ออยล์บำรุงทุกวันค่ะ 💅",
    "ทำเล็บก่อนออกงานได้ไหม": "ได้เลยค่ะ สีติดแน่นไม่หลุดแน่นอน 💖",
    "ทำเล็บก่อนแต่งงานได้ไหม": "มีแพ็กเกจเจ้าสาวพิเศษเลยค่ะ 💍",
    "ทำเล็บก่อนถ่ายรูปได้ไหม": "แน่นอนค่ะ ช่างช่วยเลือกสีให้เหมาะกับธีมได้เลย 💕",
    "ทำเล็บก่อนต่างประเทศได้ไหม": "ได้ค่ะ อยู่ได้ยาว 3-4 สัปดาห์ ✈️",
    "ทำเล็บก่อนเที่ยวทะเลได้ไหม": "ได้เลยค่ะ ใช้เจลกันน้ำไม่หลุดแน่นอน 🏖️",
    "ทำเล็บก่อนปีใหม่ได้ไหม": "ได้เลยค่ะ สีมงคลรับโชค 🎉",
    "ทำเล็บก่อนวันเกิดได้ไหม": "ได้เลยค่ะ แนะนำสีชมพูทองรับทรัพย์ 💅",
    "ทำเล็บก่อนวันวาเลนไทน์ดีไหม": "ดีเลยค่ะ ลายหัวใจสุดหวาน 💖",
    "ทำเล็บก่อนเปิดเทอมได้ไหม": "ได้ค่ะ สีสุภาพเหมาะกับนักเรียน 💕",
    "ทำเล็บก่อนสัมภาษณ์งานดีไหม": "ดีเลยค่ะ โทนนู้ดเรียบร้อย ✨",
    "ทำเล็บก่อนออกงานได้ไหม": "เหมาะมากเลยค่ะ 💅",
    "เฟร้นปลายเล็บคืออะไร": "เฟร้นปลายเล็บคือการทาสีปลายเล็บให้ดูสวยคลาสสิกค่ะ",
    "เฟร้นปลายเล็บไหม": "มีค่ะ เหมาะกับทุกวัยและทุกโอกาสค่ะ",
    "เฟร้นปลายเล็บเหมาะกับใคร": "เหมาะกับทุกวัยและทุกโอกาสค่ะ",
    "เฟร้นปลายเล็บสีขาวมีไหม": "มีค่ะ สีขาวดูเรียบหรูและคลาสสิก",
    "เฟร้นปลายเล็บสีชมพูมีไหม": "มีค่ะ สีชมพูดูหวานและน่ารัก",
    "เฟร้นปลายเล็บสีดำมีไหม": "มีค่ะ สีดำดูเท่และทันสมัย",
    "เฟร้นปลายเล็บสีทองมีไหม": "มีค่ะ สีทองดูหรูหราและโดดเด่น",
    "เฟร้นปลายเล็บสีเงินมีไหม": "มีค่ะ สีเงินดูทันสมัยและมีประกาย",
    "เฟร้นปลายเล็บสีฟ้ามีไหม": "มีค่ะ สีฟ้าดูสดใสและทันสมัย",
    "เฟร้นปลายเล็บสีแดงมีไหม": "มีค่ะ สีแดงดูสดใสและมั่นใจ",
    "เฟร้นปลายเล็บสีพาสเทลมีไหม": "มีค่ะ สีพาสเทลดูน่ารักและสดใส",
    "เฟร้นปลายเล็บลายดอกไม้มีไหม": "มีค่ะ ลายดอกไม้ดูหวานและสดใส",
    "เฟร้นปลายเล็บลายการ์ตูนมีไหม": "มีค่ะ ลายการ์ตูนดูน่ารักและสนุกสนาน",
    "เฟร้นปลายเล็บลายแฟนซีมีไหม": "มีค่ะ ลายแฟนซีดูโดดเด่นและทันสมัย",
    "เฟร้นปลายเล็บลายมินิมอลมีไหม": "มีค่ะ ลายมินิมอลดูเรียบง่ายและเก๋",
    "เฟร้นปลายเล็บลายเกาหลีมีไหม": "มีค่ะ ลายเกาหลีดูทันสมัยและน่ารัก",
    "เฟร้นปลายเล็บลายญี่ปุ่นมีไหม": "มีค่ะ ลายญี่ปุ่นดูสดใสและน่ารัก",
    "เฟร้นปลายเล็บลายฝรั่งเศสมีไหม": "มีค่ะ ลายฝรั่งเศสดูคลาสสิกและหรูหรา",
    "เฟร้นปลายเล็บลายคริสต์มาสมีไหม": "มีค่ะ ลายคริสต์มาสดูสดใสและน่ารัก",
    "เฟร้นปลายเล็บลายวาเลนไทน์มีไหม": "มีค่ะ ลายวาเลนไทน์ดูหวานและโรแมนติก",
    "เฟร้นปลายเล็บลายปีใหม่มีไหม": "มีค่ะ ลายปีใหม่ดูสดใสและสนุกสนาน",
    "เฟร้นปลายเล็บลายสงกรานต์มีไหม": "มีค่ะ ลายสงกรานต์ดูสดใสและสนุกสนาน",
    "เฟร้นปลายเล็บลายตรุษจีนมีไหม": "มีค่ะ ลายตรุษจีนดูสดใสและโชคดี",
    "เฟร้นปลายเล็บลายวันเกิดมีไหม": "มีค่ะ ลายวันเกิดดูสดใสและน่ารัก",
    "เฟร้นปลายเล็บลายรับปริญญามีไหม": "มีค่ะ ลายรับปริญญาดูหรูหราและน่ารัก",
    "เฟร้นปลายเล็บลายแต่งงานมีไหม": "มีค่ะ ลายแต่งงานดูหรูหราและโรแมนติก",
    "เฟร้นปลายเล็บลายเจ้าสาวมีไหม": "มีค่ะ ลายเจ้าสาวดูหวานและหรูหรา",
    "เฟร้นปลายเล็บลายเจ้าบ่าวมีไหม": "มีค่ะ ลายเจ้าบ่าวดูเรียบง่ายและเท่",
    "เฟร้นปลายเล็บลายเด็กมีไหม": "มีค่ะ ลายเด็กดูน่ารักและสดใส",
    "เฟร้นปลายเล็บลายผู้ชายมีไหม": "มีค่ะ ลายผู้ชายดูเท่และทันสมัย",
    "เฟร้นปลายเล็บลายผู้สูงอายุมีไหม": "มีค่ะ ลายผู้สูงอายุดูสุภาพและเรียบง่าย",
    "เฟร้นปลายเล็บทรงอัลมอนด์มีไหม": "มีค่ะ ทรงอัลมอนด์ดูเรียวสวยและทันสมัย",
    "เฟร้นปลายเล็บทรงเหลี่ยมมีไหม": "มีค่ะ ทรงเหลี่ยมดูเท่และทันสมัย",
    "เฟร้นปลายเล็บทรงรีมีไหม": "มีค่ะ ทรงรีดูเรียบง่ายและสุภาพ",
    "เฟร้นปลายเล็บทรงกลมมีไหม": "มีค่ะ ทรงกลมดูน่ารักและอ่อนโยน",
    "เฟร้นปลายเล็บทรงปลายแหลมมีไหม": "มีค่ะ ทรงปลายแหลมดูโดดเด่นและทันสมัย",
    "เฟร้นปลายเล็บทรงปลายมนมีไหม": "มีค่ะ ทรงปลายมนดูนุ่มนวลและสุภาพ",
    "เฟร้นปลายเล็บทรงปลายตรงมีไหม": "มีค่ะ ทรงปลายตรงดูเรียบง่ายและทันสมัย",
    "เฟร้นปลายเล็บทรงปลายโค้งมีไหม": "มีค่ะ ทรงปลายโค้งดูสวยและทันสมัย",
    "เฟร้นปลายเล็บทรงปลายตัดมีไหม": "มีค่ะ ทรงปลายตัดดูเท่และทันสมัย",
    "เฟร้นปลายเล็บทรงปลายหยักมีไหม": "มีค่ะ ทรงปลายหยักดูเก๋และทันสมัย",
    "เฟร้นปลายเล็บทรงปลายหยดน้ำมีไหม": "มีค่ะ ทรงปลายหยดน้ำดูน่ารักและทันสมัย",
    "เฟร้นปลายเล็บทรงปลายเปลวไฟมีไหม": "มีค่ะ ทรงปลายเปลวไฟดูโดดเด่นและทันสมัย",
    "เฟร้นปลายเล็บทรงปลายหัวใจมีไหม": "มีค่ะ ทรงปลายหัวใจดูหวานและน่ารัก",
    "เฟร้นปลายเล็บทรงปลายใบไม้มีไหม": "มีค่ะ ทรงปลายใบไม้ดูสดใสและธรรมชาติ",
    "มีสีโรสโกลด์ไหม": "มีค่ะ สีโรสโกลด์ดูหรูหราและทันสมัยมากค่ะ",
    "มีสีแชมเปญไหม": "มีค่ะ สีแชมเปญดูสุภาพและหรูหราค่ะ",
    "มีสีคอรัลไหม": "มีค่ะ สีคอรัลดูสดใสและน่ารักค่ะ",
    "มีสีลาเวนเดอร์ไหม": "มีค่ะ สีลาเวนเดอร์ดูหวานและสงบค่ะ",
    "มีสีบลูเบอร์รี่ไหม": "มีค่ะ สีบลูเบอร์รี่ดูสดใสและโดดเด่นค่ะ",
    "มีสีมะม่วงไหม": "มีค่ะ สีมะม่วงดูสดใสและแปลกใหม่ค่ะ",
    "มีสีส้มพีชไหม": "มีค่ะ สีส้มพีชดูนุ่มนวลและน่ารักค่ะ",
    "มีสีเขียวมิ้นต์ไหม": "มีค่ะ สีเขียวมิ้นต์ดูสดชื่นและทันสมัยค่ะ",
    "มีสีฟ้าเทอร์ควอยซ์ไหม": "มีค่ะ สีฟ้าเทอร์ควอยซ์ดูสดใสและโดดเด่นค่ะ",
    "มีสีแดงเบอร์กันดีไหม": "มีค่ะ สีแดงเบอร์กันดีดูหรูหราและคลาสสิกค่ะ",
    "มีสีชมพูบานเย็นไหม": "มีค่ะ สีชมพูบานเย็นดูสดใสและน่ารักค่ะ",
    "มีสีม่วงพลัมไหม": "มีค่ะ สีม่วงพลัมดูหรูหราและมีเสน่ห์ค่ะ",
    "มีสีเขียวมะกอกไหม": "มีค่ะ สีเขียวมะกอกดูสุภาพและธรรมชาติค่ะ",
    "มีสีฟ้าไอซ์ไหม": "มีค่ะ สีฟ้าไอซ์ดูเย็นสบายและทันสมัยค่ะ",
    "มีสีเหลืองมัสตาร์ดไหม": "มีค่ะ สีเหลืองมัสตาร์ดดูสดใสและโดดเด่นค่ะ",
    "มีสีส้มแครอทไหม": "มีค่ะ สีส้มแครอทดูสดใสและน่ารักค่ะ",
    "มีสีแดงเชอร์รี่ไหม": "มีค่ะ สีแดงเชอร์รี่ดูสดใสและหวานค่ะ",
    "มีสีชมพูซากุระไหม": "มีค่ะ สีชมพูซากุระดูหวานและอ่อนโยนค่ะ",
    "มีสีม่วงอเมทิสต์ไหม": "มีค่ะ สีม่วงอเมทิสต์ดูหรูหราและน่ารักค่ะ",
    "มีสีเขียวใบเตยไหม": "มีค่ะ สีเขียวใบเตยดูสดชื่นและธรรมชาติค่ะ",
    "มีสีฟ้าสกายไหม": "มีค่ะ สีฟ้าสกายดูสดใสและสบายตาค่ะ",
    "มีสีเหลืองกล้วยไหม": "มีค่ะ สีเหลืองกล้วยดูสดใสและน่ารักค่ะ",
    "มีสีส้มแมนดารินไหม": "มีค่ะ สีส้มแมนดารินดูสดใสและโดดเด่นค่ะ",
    "มีสีแดงกุหลาบไหม": "มีค่ะ สีแดงกุหลาบดูหรูหราและคลาสสิกค่ะ",
    "มีสีชมพูพีโอนีไหม": "มีค่ะ สีชมพูพีโอนีดูหวานและน่ารักค่ะ",
    "มีสีม่วงไลแลคไหม": "มีค่ะ สีม่วงไลแลคดูนุ่มนวลและหรูหราค่ะ",
    "มีสีเขียวแอปเปิ้ลไหม": "มีค่ะ สีเขียวแอปเปิ้ลดูสดใสและธรรมชาติค่ะ",
    "มีสีฟ้าโอเชี่ยนไหม": "มีค่ะ สีฟ้าโอเชี่ยนดูสดใสและทันสมัยค่ะ",
    "มีสีเหลืองขมิ้นไหม": "มีค่ะ สีเหลืองขมิ้นดูสดใสและโดดเด่นค่ะ",
    "มีสีส้มซันเซ็ทไหม": "มีค่ะ สีส้มซันเซ็ทดูสดใสและน่ารักค่ะ",
    "มีสีแดงทับทิมไหม": "มีค่ะ สีแดงทับทิมดูหรูหราและคลาสสิกค่ะ",
    "มีสีชมพูโรสไหม": "มีค่ะ สีชมพูโรสดูหวานและอ่อนโยนค่ะ",
    "มีสีม่วงไวโอเล็ตไหม": "มีค่ะ สีม่วงไวโอเล็ตดูหรูหราและน่ารักค่ะ",
    "มีสีเขียวหยกไหม": "มีค่ะ สีเขียวหยกดูสดชื่นและธรรมชาติค่ะ",
    "มีสีฟ้าเมฆไหม": "มีค่ะ สีฟ้าเมฆดูสดใสและสบายตาค่ะ",
    "มีสีเหลืองอำพันไหม": "มีค่ะ สีเหลืองอำพันดูสดใสและโดดเด่นค่ะ",
    "มีสีส้มคาราเมลไหม": "มีค่ะ สีส้มคาราเมลดูนุ่มนวลและน่ารักค่ะ",
    "มีสีแดงสตรอว์เบอร์รี่ไหม": "มีค่ะ สีแดงสตรอว์เบอร์รี่ดูสดใสและหวานค่ะ",
    "มีสีชมพูแมกโนเลียไหม": "มีค่ะ สีชมพูแมกโนเลียดูหวานและน่ารักค่ะ",
    "มีสีม่วงลาเวนเดอร์ไหม": "มีค่ะ สีม่วงลาเวนเดอร์ดูนุ่มนวลและหรูหราค่ะ",
    "มีสีเขียวมะนาวไหม": "มีค่ะ สีเขียวมะนาวดูสดใสและธรรมชาติค่ะ",
    "มีสีฟ้าทะเลไหม": "มีค่ะ สีฟ้าทะเลดูสดใสและทันสมัยค่ะ",
    "มีสีเหลืองข้าวโพดไหม": "มีค่ะ สีเหลืองข้าวโพดดูสดใสและน่ารักค่ะ",
    "มีสีส้มส้มโอไหม": "มีค่ะ สีส้มส้มโอดูสดใสและโดดเด่นค่ะ",
    "มีสีแดงแอปเปิ้ลไหม": "มีค่ะ สีแดงแอปเปิ้ลดูสดใสและหวานค่ะ",
    "มีสีชมพูคามิเลียไหม": "มีค่ะ สีชมพูคามิเลียดูหวานและอ่อนโยนค่ะ",
    "มีสีม่วงกล้วยไม้ไหม": "มีค่ะ สีม่วงกล้วยไม้ดูหรูหราและน่ารักค่ะ",
    "มีสีเขียวใบไม้ไหม": "มีค่ะ สีเขียวใบไม้ดูสดชื่นและธรรมชาติค่ะ",
    "มีสีแดงไหม": "มีค่ะ สีแดงสดใสเหมาะกับลุคมั่นใจค่ะ",
    "มีสีฟ้าไหม": "มีค่ะ สีฟ้าดูสดชื่นและทันสมัยค่ะ",
    "มีสีเขียวไหม": "มีค่ะ สีเขียวให้ความรู้สึกสดชื่นธรรมชาติค่ะ",
    "มีสีเหลืองไหม": "มีค่ะ สีเหลืองสดใสเหมาะกับวันสดใสค่ะ",
    "มีสีชมพูไหม": "มีค่ะ สีชมพูดูอ่อนหวานกำลังดีเลยค่ะ",
    "มีสีม่วงไหม": "มีค่ะ สีม่วงดูหรูหราและมีเสน่ห์ค่ะ",
    "มีสีส้มไหม": "มีค่ะ สีส้มสดใสเหมาะกับลุคสนุกสนานค่ะ",
    "มีสีขาวไหม": "มีค่ะ สีขาวดูสะอาดและเรียบง่ายค่ะ",
    "มีสีดำไหม": "มีค่ะ สีดำดูเท่และคลาสสิกค่ะ",
    "มีสีทองไหม": "มีค่ะ สีทองดูหรูหราและโดดเด่นค่ะ",
    "มีสีเงินไหม": "มีค่ะ สีเงินดูทันสมัยและมีประกายค่ะ",
    "มีสีเทาไหม": "มีค่ะ สีเทาดูสุภาพและเรียบหรูค่ะ",
    "มีสีน้ำตาลไหม": "มีค่ะ สีน้ำตาลดูอบอุ่นและธรรมชาติค่ะ",
    "มีสีครีมไหม": "มีค่ะ สีครีมดูสุภาพและนุ่มนวลค่ะ",
    "มีสีพาสเทลไหม": "มีค่ะ สีพาสเทลดูน่ารักและสดใสค่ะ",
    "มีสีโอลด์โรสไหม": "มีค่ะ สีโอลด์โรสดูหวานและคลาสสิกค่ะ",
    "มีสีไวน์ไหม": "มีค่ะ สีไวน์ดูหรูหราและมีสไตล์ค่ะ",
    "มีสีบานเย็นไหม": "มีค่ะ สีบานเย็นดูสดใสและโดดเด่นค่ะ",
    "มีสีมินต์ไหม": "มีค่ะ สีมินต์ดูสดชื่นและน่ารักค่ะ",
    "มีสีมะนาวไหม": "มีค่ะ สีมะนาวดูสดใสและแปลกใหม่ค่ะ",
    "มีสีฟ้าอ่อนไหม": "มีค่ะ สีฟ้าอ่อนดูนุ่มนวลและสบายตาค่ะ",
    "มีสีฟ้าเข้มไหม": "มีค่ะ สีฟ้าเข้มดูเท่และทันสมัยค่ะ",
    "มีสีเขียวอ่อนไหม": "มีค่ะ สีเขียวอ่อนดูสดชื่นและธรรมชาติค่ะ",
    "มีสีเขียวเข้มไหม": "มีค่ะ สีเขียวเข้มดูสุขุมและมีเสน่ห์ค่ะ",
    "มีสีเหลืองอ่อนไหม": "มีค่ะ สีเหลืองอ่อนดูนุ่มนวลและสดใสค่ะ",
    "มีสีเหลืองเข้มไหม": "มีค่ะ สีเหลืองเข้มดูโดดเด่นและสดใสค่ะ",
    "มีสีชมพูอ่อนไหม": "มีค่ะ สีชมพูอ่อนดูหวานและน่ารักค่ะ",
    "มีสีชมพูเข้มไหม": "มีค่ะ สีชมพูเข้มดูสดใสและโดดเด่นค่ะ",
    "มีสีม่วงอ่อนไหม": "มีค่ะ สีม่วงอ่อนดูนุ่มนวลและหรูหราค่ะ",
    "มีสีม่วงเข้มไหม": "มีค่ะ สีม่วงเข้มดูมีเสน่ห์และโดดเด่นค่ะ",
    "มีสีส้มอ่อนไหม": "มีค่ะ สีส้มอ่อนดูนุ่มนวลและสดใสค่ะ",
    "มีสีส้มเข้มไหม": "มีค่ะ สีส้มเข้มดูสดใสและโดดเด่นค่ะ",
    "มีสีขาวมุกไหม": "มีค่ะ สีขาวมุกดูหรูหราและอ่อนโยนค่ะ",
    "มีสีดำด้านไหม": "มีค่ะ สีดำด้านดูเท่และทันสมัยค่ะ",
    "มีสีทองประกายไหม": "มีค่ะ สีทองประกายดูหรูหราและมีประกายค่ะ",
    "มีสีเงินประกายไหม": "มีค่ะ สีเงินประกายดูทันสมัยและโดดเด่นค่ะ",
    "มีสีเทาอ่อนไหม": "มีค่ะ สีเทาอ่อนดูสุภาพและเรียบง่ายค่ะ",
    "มีสีเทาเข้มไหม": "มีค่ะ สีเทาเข้มดูสุขุมและทันสมัยค่ะ",
    "มีสีน้ำตาลอ่อนไหม": "มีค่ะ สีน้ำตาลอ่อนดูอบอุ่นและนุ่มนวลค่ะ",
    "มีสีน้ำตาลเข้มไหม": "มีค่ะ สีน้ำตาลเข้มดูสุขุมและคลาสสิกค่ะ",
    "มีสีครีมอ่อนไหม": "มีค่ะ สีครีมอ่อนดูสุภาพและนุ่มนวลค่ะ",
    "มีสีครีมเข้มไหม": "มีค่ะ สีครีมเข้มดูโดดเด่นและสุภาพค่ะ",
    "มีสีพาสเทลฟ้าไหม": "มีค่ะ สีพาสเทลฟ้าดูน่ารักและสดใสค่ะ",
    "มีสีพาสเทลชมพูไหม": "มีค่ะ สีพาสเทลชมพูดูหวานและน่ารักค่ะ",
    "มีสีพาสเทลเขียวไหม": "มีค่ะ สีพาสเทลเขียวดูสดชื่นและธรรมชาติค่ะ",
    "มีสีพาสเทลเหลืองไหม": "มีค่ะ สีพาสเทลเหลืองดูสดใสและนุ่มนวลค่ะ",
    "มีสีพาสเทลม่วงไหม": "มีค่ะ สีพาสเทลม่วงดูหรูหราและน่ารักค่ะ",
    "มีสีพาสเทลส้มไหม": "มีค่ะ สีพาสเทลส้มดูสดใสและทันสมัยค่ะ",
    "ราคาทรงเล็บอัลมอนด์เท่าไหร่": "ราคาทรงเล็บอัลมอนด์เริ่มต้น 350 บาทค่ะ",
    "ราคาทรงเล็บเหลี่ยมเท่าไหร่": "ราคาทรงเล็บเหลี่ยมเริ่มต้น 300 บาทค่ะ",
    "ราคาทรงเล็บรีเท่าไหร่": "ราคาทรงเล็บรีเริ่มต้น 320 บาทค่ะ",
    "ราคาทรงเล็บกลมเท่าไหร่": "ราคาทรงเล็บกลมเริ่มต้น 280 บาทค่ะ",
    "ราคาทรงเล็บปลายแหลมเท่าไหร่": "ราคาทรงเล็บปลายแหลมเริ่มต้น 400 บาทค่ะ",
    "ราคาทรงเล็บปลายมนเท่าไหร่": "ราคาทรงเล็บปลายมนเริ่มต้น 300 บาทค่ะ",
    "ราคาทรงเล็บปลายตรงเท่าไหร่": "ราคาทรงเล็บปลายตรงเริ่มต้น 320 บาทค่ะ",
    "ราคาทรงเล็บปลายโค้งเท่าไหร่": "ราคาทรงเล็บปลายโค้งเริ่มต้น 350 บาทค่ะ",
    "ราคาทรงเล็บปลายตัดเท่าไหร่": "ราคาทรงเล็บปลายตัดเริ่มต้น 300 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเท่าไหร่": "ราคาทรงเล็บปลายหยักเริ่มต้น 380 บาทค่ะ",
    "ราคาทรงเล็บปลายหยดน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยดน้ำเริ่มต้น 400 บาทค่ะ",
    "ราคาทรงเล็บปลายเปลวไฟเท่าไหร่": "ราคาทรงเล็บปลายเปลวไฟเริ่มต้น 420 บาทค่ะ",
    "ราคาทรงเล็บปลายหัวใจเท่าไหร่": "ราคาทรงเล็บปลายหัวใจเริ่มต้น 450 บาทค่ะ",
    "ราคาทรงเล็บปลายใบไม้เท่าไหร่": "ราคาทรงเล็บปลายใบไม้เริ่มต้น 370 บาทค่ะ",
    "ราคาทรงเล็บปลายเพชรเท่าไหร่": "ราคาทรงเล็บปลายเพชรเริ่มต้น 400 บาทค่ะ",
    "ราคาทรงเล็บปลายกลีบดอกไม้เท่าไหร่": "ราคาทรงเล็บปลายกลีบดอกไม้เริ่มต้น 420 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักคลื่นเท่าไหร่": "ราคาทรงเล็บปลายหยักคลื่นเริ่มต้น 380 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟันปลาเท่าไหร่": "ราคาทรงเล็บปลายหยักฟันปลาเริ่มต้น 390 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักซิกแซกเท่าไหร่": "ราคาทรงเล็บปลายหยักซิกแซกเริ่มต้น 400 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟองน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักฟองน้ำเริ่มต้น 410 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหยดน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักหยดน้ำเริ่มต้น 420 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเปลวไฟเท่าไหร่": "ราคาทรงเล็บปลายหยักเปลวไฟเริ่มต้น 430 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหัวใจเท่าไหร่": "ราคาทรงเล็บปลายหยักหัวใจเริ่มต้น 440 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักใบไม้เท่าไหร่": "ราคาทรงเล็บปลายหยักใบไม้เริ่มต้น 450 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเพชรเท่าไหร่": "ราคาทรงเล็บปลายหยักเพชรเริ่มต้น 460 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักกลีบดอกไม้เท่าไหร่": "ราคาทรงเล็บปลายหยักกลีบดอกไม้เริ่มต้น 470 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักคลื่นเท่าไหร่": "ราคาทรงเล็บปลายหยักคลื่นเริ่มต้น 480 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟันปลาเท่าไหร่": "ราคาทรงเล็บปลายหยักฟันปลาเริ่มต้น 490 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักซิกแซกเท่าไหร่": "ราคาทรงเล็บปลายหยักซิกแซกเริ่มต้น 500 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟองน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักฟองน้ำเริ่มต้น 510 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหยดน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักหยดน้ำเริ่มต้น 520 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเปลวไฟเท่าไหร่": "ราคาทรงเล็บปลายหยักเปลวไฟเริ่มต้น 530 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหัวใจเท่าไหร่": "ราคาทรงเล็บปลายหยักหัวใจเริ่มต้น 540 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักใบไม้เท่าไหร่": "ราคาทรงเล็บปลายหยักใบไม้เริ่มต้น 550 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเพชรเท่าไหร่": "ราคาทรงเล็บปลายหยักเพชรเริ่มต้น 560 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักกลีบดอกไม้เท่าไหร่": "ราคาทรงเล็บปลายหยักกลีบดอกไม้เริ่มต้น 570 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักคลื่นเท่าไหร่": "ราคาทรงเล็บปลายหยักคลื่นเริ่มต้น 580 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟันปลาเท่าไหร่": "ราคาทรงเล็บปลายหยักฟันปลาเริ่มต้น 590 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักซิกแซกเท่าไหร่": "ราคาทรงเล็บปลายหยักซิกแซกเริ่มต้น 600 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักฟองน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักฟองน้ำเริ่มต้น 610 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหยดน้ำเท่าไหร่": "ราคาทรงเล็บปลายหยักหยดน้ำเริ่มต้น 620 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักเปลวไฟเท่าไหร่": "ราคาทรงเล็บปลายหยักเปลวไฟเริ่มต้น 630 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักหัวใจเท่าไหร่": "ราคาทรงเล็บปลายหยักหัวใจเริ่มต้น 640 บาทค่ะ",
    "ราคาทรงเล็บปลายหยักใบไม้เท่าไหร่": "ราคาทรงเล็บปลายหยักใบไม้เริ่มต้น 650 บาทค่ะ",
    "ราคาต่อเล็บมือเท่าไหร่": "ราคาต่อเล็บมือเริ่มต้น 700 บาทค่ะ",
    "ราคาต่อเล็บเท้าเท่าไหร่": "ราคาต่อเล็บเท้าเริ่มต้น 750 บาทค่ะ",
    "ราคาต่อเล็บเจลมือเท่าไหร่": "ราคาต่อเล็บเจลมือเริ่มต้น 800 บาทค่ะ",
    "ราคาต่อเล็บเจลเท้าเท่าไหร่": "ราคาต่อเล็บเจลเท้าเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บอะคริลิกมือเท่าไหร่": "ราคาต่อเล็บอะคริลิกมือเริ่มต้น 900 บาทค่ะ",
    "ราคาต่อเล็บอะคริลิกเท้าเท่าไหร่": "ราคาต่อเล็บอะคริลิกเท้าเริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บ PVC มือเท่าไหร่": "ราคาต่อเล็บ PVC มือเริ่มต้น 600 บาทค่ะ",
    "ราคาต่อเล็บ PVC เท้าเท่าไหร่": "ราคาต่อเล็บ PVC เท้าเริ่มต้น 650 บาทค่ะ",
    "ราคาต่อเล็บลายแฟนซีเท่าไหร่": "ราคาต่อเล็บลายแฟนซีเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายเรียบง่ายเท่าไหร่": "ราคาต่อเล็บลายเรียบง่ายเริ่มต้น 800 บาทค่ะ",
    "ราคาต่อเล็บลายหรูหราเท่าไหร่": "ราคาต่อเล็บลายหรูหราเริ่มต้น 1,200 บาทค่ะ",
    "ราคาต่อเล็บลายเกาหลีเท่าไหร่": "ราคาต่อเล็บลายเกาหลีเริ่มต้น 900 บาทค่ะ",
    "ราคาต่อเล็บลายญี่ปุ่นเท่าไหร่": "ราคาต่อเล็บลายญี่ปุ่นเริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บลายฝรั่งเศสเท่าไหร่": "ราคาต่อเล็บลายฝรั่งเศสเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายมินิมอลเท่าไหร่": "ราคาต่อเล็บลายมินิมอลเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บลายดอกไม้เท่าไหร่": "ราคาต่อเล็บลายดอกไม้เริ่มต้น 900 บาทค่ะ",
    "ราคาต่อเล็บลายการ์ตูนเท่าไหร่": "ราคาต่อเล็บลายการ์ตูนเริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บลายคริสต์มาสเท่าไหร่": "ราคาต่อเล็บลายคริสต์มาสเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายวาเลนไทน์เท่าไหร่": "ราคาต่อเล็บลายวาเลนไทน์เริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บลายปีใหม่เท่าไหร่": "ราคาต่อเล็บลายปีใหม่เริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายสงกรานต์เท่าไหร่": "ราคาต่อเล็บลายสงกรานต์เริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บลายตรุษจีนเท่าไหร่": "ราคาต่อเล็บลายตรุษจีนเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายวันเกิดเท่าไหร่": "ราคาต่อเล็บลายวันเกิดเริ่มต้น 950 บาทค่ะ",
    "ราคาต่อเล็บลายรับปริญญาเท่าไหร่": "ราคาต่อเล็บลายรับปริญญาเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายแต่งงานเท่าไหร่": "ราคาต่อเล็บลายแต่งงานเริ่มต้น 1,200 บาทค่ะ",
    "ราคาต่อเล็บลายเจ้าสาวเท่าไหร่": "ราคาต่อเล็บลายเจ้าสาวเริ่มต้น 1,200 บาทค่ะ",
    "ราคาต่อเล็บลายเจ้าบ่าวเท่าไหร่": "ราคาต่อเล็บลายเจ้าบ่าวเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บลายเด็กเท่าไหร่": "ราคาต่อเล็บลายเด็กเริ่มต้น 800 บาทค่ะ",
    "ราคาต่อเล็บลายผู้ชายเท่าไหร่": "ราคาต่อเล็บลายผู้ชายเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บลายผู้สูงอายุเท่าไหร่": "ราคาต่อเล็บลายผู้สูงอายุเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บบำรุงเล็บเท่าไหร่": "ราคาต่อเล็บบำรุงเล็บเริ่มต้น 700 บาทค่ะ",
    "ราคาต่อเล็บมือเจ้าสาวเท่าไหร่": "ราคาต่อเล็บมือเจ้าสาวเริ่มต้น 1,200 บาทค่ะ",
    "ราคาต่อเล็บมือเจ้าบ่าวเท่าไหร่": "ราคาต่อเล็บมือเจ้าบ่าวเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บมือเด็กเท่าไหร่": "ราคาต่อเล็บมือเด็กเริ่มต้น 800 บาทค่ะ",
    "ราคาต่อเล็บมือผู้ชายเท่าไหร่": "ราคาต่อเล็บมือผู้ชายเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บมือผู้สูงอายุเท่าไหร่": "ราคาต่อเล็บมือผู้สูงอายุเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บเท้าเจ้าสาวเท่าไหร่": "ราคาต่อเล็บเท้าเจ้าสาวเริ่มต้น 1,200 บาทค่ะ",
    "ราคาต่อเล็บเท้าเจ้าบ่าวเท่าไหร่": "ราคาต่อเล็บเท้าเจ้าบ่าวเริ่มต้น 1,000 บาทค่ะ",
    "ราคาต่อเล็บเท้าเด็กเท่าไหร่": "ราคาต่อเล็บเท้าเด็กเริ่มต้น 800 บาทค่ะ",
    "ราคาต่อเล็บเท้าผู้ชายเท่าไหร่": "ราคาต่อเล็บเท้าผู้ชายเริ่มต้น 850 บาทค่ะ",
    "ราคาต่อเล็บเท้าผู้สูงอายุเท่าไหร่": "ราคาต่อเล็บเท้าผู้สูงอายุเริ่มต้น 850 บาทค่ะ",
    "ราคาเล็บเจลเท่าไหร่": "ราคาเล็บเจลเริ่มต้น 500 บาทค่ะ",
    "ราคาเล็บอะคริลิกเท่าไหร่": "ราคาเล็บอะคริลิกเริ่มต้น 600 บาทค่ะ",
    "ราคาเล็บ PVC เท่าไหร่": "ราคาเล็บ PVC เริ่มต้น 400 บาทค่ะ",
    "ราคาต่อเล็บเท่าไหร่": "ราคาต่อเล็บเริ่มต้น 700 บาทค่ะ",
    "ราคาเพ้นท์เล็บเท่าไหร่": "ราคาเพ้นท์เล็บเริ่มต้น 300 บาทค่ะ",
    "ราคาทาสีเล็บเท่าไหร่": "ราคาทาสีเล็บเริ่มต้น 200 บาทค่ะ",
    "ราคาถอดเล็บเท่าไหร่": "ราคาถอดเล็บเริ่มต้น 150 บาทค่ะ",
    "ราคาซ่อมเล็บเท่าไหร่": "ราคาซ่อมเล็บเริ่มต้น 250 บาทค่ะ",
    "ราคาสปาเล็บเท่าไหร่": "ราคาสปาเล็บเริ่มต้น 350 บาทค่ะ",
    "ราคาตัดหนังเท่าไหร่": "ราคาตัดหนังเริ่มต้น 100 บาทค่ะ",
    "ราคาขัดเล็บเท่าไหร่": "ราคาขัดเล็บเริ่มต้น 120 บาทค่ะ",
    "ราคาล้างเล็บเท่าไหร่": "ราคาล้างเล็บเริ่มต้น 80 บาทค่ะ",
    "ราคาตกแต่งเล็บเท่าไหร่": "ราคาตกแต่งเล็บเริ่มต้น 180 บาทค่ะ",
    "ราคาพาราฟินเท่าไหร่": "ราคาพาราฟินเริ่มต้น 400 บาทค่ะ",
    "ราคานวดมือเท่าไหร่": "ราคานวดมือเริ่มต้น 200 บาทค่ะ",
    "ราคานวดเท้าเท่าไหร่": "ราคานวดเท้าเริ่มต้น 250 บาทค่ะ",
    "ราคาสปามือเท่าไหร่": "ราคาสปามือเริ่มต้น 350 บาทค่ะ",
    "ราคาสปาเท้าเท่าไหร่": "ราคาสปาเท้าเริ่มต้น 400 บาทค่ะ",
    "ราคาลายแฟนซีเท่าไหร่": "ราคาลายแฟนซีเริ่มต้น 350 บาทค่ะ",
    "ราคาลายเรียบง่ายเท่าไหร่": "ราคาลายเรียบง่ายเริ่มต้น 250 บาทค่ะ",
    "ราคาลายหรูหราเท่าไหร่": "ราคาลายหรูหราเริ่มต้น 400 บาทค่ะ",
    "ราคาลายเกาหลีเท่าไหร่": "ราคาลายเกาหลีเริ่มต้น 300 บาทค่ะ",
    "ราคาลายญี่ปุ่นเท่าไหร่": "ราคาลายญี่ปุ่นเริ่มต้น 320 บาทค่ะ",
    "ราคาลายฝรั่งเศสเท่าไหร่": "ราคาลายฝรั่งเศสเริ่มต้น 350 บาทค่ะ",
    "ราคาลายมินิมอลเท่าไหร่": "ราคาลายมินิมอลเริ่มต้น 200 บาทค่ะ",
    "ราคาลายดอกไม้เท่าไหร่": "ราคาลายดอกไม้เริ่มต้น 280 บาทค่ะ",
    "ราคาลายการ์ตูนเท่าไหร่": "ราคาลายการ์ตูนเริ่มต้น 300 บาทค่ะ",
    "ราคาลายคริสต์มาสเท่าไหร่": "ราคาลายคริสต์มาสเริ่มต้น 350 บาทค่ะ",
    "ราคาลายวาเลนไทน์เท่าไหร่": "ราคาลายวาเลนไทน์เริ่มต้น 320 บาทค่ะ",
    "ราคาลายปีใหม่เท่าไหร่": "ราคาลายปีใหม่เริ่มต้น 350 บาทค่ะ",
    "ราคาลายสงกรานต์เท่าไหร่": "ราคาลายสงกรานต์เริ่มต้น 300 บาทค่ะ",
    "ราคาลายตรุษจีนเท่าไหร่": "ราคาลายตรุษจีนเริ่มต้น 350 บาทค่ะ",
    "ราคาลายวันเกิดเท่าไหร่": "ราคาลายวันเกิดเริ่มต้น 320 บาทค่ะ",
    "ราคาลายรับปริญญาเท่าไหร่": "ราคาลายรับปริญญาเริ่มต้น 350 บาทค่ะ",
    "ราคาลายแต่งงานเท่าไหร่": "ราคาลายแต่งงานเริ่มต้น 400 บาทค่ะ",
    "ราคาลายเจ้าสาวเท่าไหร่": "ราคาลายเจ้าสาวเริ่มต้น 400 บาทค่ะ",
    "ราคาลายเจ้าบ่าวเท่าไหร่": "ราคาลายเจ้าบ่าวเริ่มต้น 350 บาทค่ะ",
    "ราคาลายเด็กเท่าไหร่": "ราคาลายเด็กเริ่มต้น 200 บาทค่ะ",
    "ราคาลายผู้ชายเท่าไหร่": "ราคาลายผู้ชายเริ่มต้น 250 บาทค่ะ",
    "ราคาลายผู้สูงอายุเท่าไหร่": "ราคาลายผู้สูงอายุเริ่มต้น 250 บาทค่ะ",
    "ราคาบำรุงเล็บเท่าไหร่": "ราคาบำรุงเล็บเริ่มต้น 150 บาทค่ะ",
    "ราคาทำเล็บมือเท่าไหร่": "ราคาทำเล็บมือเริ่มต้น 200 บาทค่ะ",
    "ราคาทำเล็บเท้าเท่าไหร่": "ราคาทำเล็บเท้าเริ่มต้น 250 บาทค่ะ",
    "ราคาทำเล็บเจ้าสาวเท่าไหร่": "ราคาทำเล็บเจ้าสาวเริ่มต้น 400 บาทค่ะ",
    "ราคาทำเล็บเจ้าบ่าวเท่าไหร่": "ราคาทำเล็บเจ้าบ่าวเริ่มต้น 350 บาทค่ะ",
    "ร้านทำเล็บมีรีวิวจากลูกค้าไหม": "มีรีวิวจากลูกค้าหลายท่านในเพจ Facebook และ Google ค่ะ",
    "ร้านทำเล็บมีช่างกี่คน": "ร้านมีช่างประจำ 5 คนค่ะ",
    "ร้านทำเล็บมีบริการรับจองคิวออนไลน์ไหม": "สามารถจองคิวผ่าน LINE หรือเว็บไซต์ได้ค่ะ",
    "ร้านทำเล็บมีบริการรับจองคิวหน้าร้านไหม": "สามารถจองคิวที่หน้าร้านได้ค่ะ",
    "ร้านทำเล็บมีบริการรับจองคิวโทรศัพท์ไหม": "สามารถจองคิวทางโทรศัพท์ได้ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งเตือนคิวไหม": "มีบริการแจ้งเตือนคิวผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งโปรโมชั่นไหม": "มีบริการแจ้งโปรโมชั่นผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งข่าวสารไหม": "มีบริการแจ้งข่าวสารผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันหยุดไหม": "มีบริการแจ้งวันหยุดผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันเปิดไหม": "มีบริการแจ้งวันเปิดผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันปิดไหม": "มีบริการแจ้งวันปิดผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันจองไหม": "มีบริการแจ้งวันจองผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันบริการไหม": "มีบริการแจ้งวันบริการผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันโปรโมชั่นไหม": "มีบริการแจ้งวันโปรโมชั่นผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันนัดหมายไหม": "มีบริการแจ้งวันนัดหมายผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันรอคิวไหม": "มีบริการแจ้งวันรอคิวผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันดูแลลูกค้าไหม": "มีบริการแจ้งวันดูแลลูกค้าผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันสำคัญไหม": "มีบริการแจ้งวันสำคัญผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันกิจกรรมไหม": "มีบริการแจ้งวันกิจกรรมผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันเทศกาลไหม": "มีบริการแจ้งวันเทศกาลผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันฤดูกาลไหม": "มีบริการแจ้งวันฤดูกาลผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันสุขภาพไหม": "มีบริการแจ้งวันสุขภาพผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันโปรโมชั่นพิเศษไหม": "มีบริการแจ้งวันโปรโมชั่นพิเศษผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันรับปริญญาไหม": "มีบริการแจ้งวันรับปริญญาผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันแต่งงานไหม": "มีบริการแจ้งวันแต่งงานผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันวันเกิดไหม": "มีบริการแจ้งวันวันเกิดผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันคริสต์มาสไหม": "มีบริการแจ้งวันคริสต์มาสผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันปีใหม่ไหม": "มีบริการแจ้งวันปีใหม่ผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันสงกรานต์ไหม": "มีบริการแจ้งวันสงกรานต์ผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการแจ้งวันตรุษจีนไหม": "มีบริการแจ้งวันตรุษจีนผ่าน LINE ค่ะ",
    "ร้านทำเล็บมีบริการรับฝากของไหม": "มีบริการรับฝากของสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการน้ำดื่มฟรีไหม": "มีน้ำดื่มฟรีสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการขนมไหม": "มีขนมบริการสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการอินเทอร์เน็ตฟรีไหม": "มี Wi-Fi ฟรีสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการชาร์จมือถือไหม": "มีจุดชาร์จมือถือให้บริการค่ะ",
    "ร้านทำเล็บมีบริการนวดมือไหม": "มีบริการนวดมือสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการนวดเท้าไหม": "มีบริการนวดเท้าสำหรับลูกค้าค่ะ",
    "ร้านทำเล็บมีบริการสปาเท้าไหม": "มีบริการสปาเท้าค่ะ",
    "ร้านทำเล็บมีบริการสปามือไหม": "มีบริการสปามือค่ะ",
    "ร้านทำเล็บมีบริการถ่ายรูปไหม": "มีมุมถ่ายรูปสวย ๆ ให้บริการค่ะ",
    "ร้านทำเล็บมีบริการดูแลเด็กไหม": "มีบริการดูแลเด็กสำหรับลูกค้าที่พาเด็กมาด้วยค่ะ",
    "ร้านทำเล็บมีบริการดูแลผู้สูงอายุไหม": "มีบริการดูแลผู้สูงอายุค่ะ",
    "ร้านทำเล็บมีบริการรับส่งไหม": "ขออภัยค่ะ ยังไม่มีบริการรับส่ง",
    "ร้านมีที่จอดรถกี่คัน": "ร้านมีที่จอดรถประมาณ 10 คันค่ะ",
    "ร้านมีบริการรับฝากของไหม": "มีบริการรับฝากของสำหรับลูกค้าค่ะ",
    "ร้านมีบริการน้ำดื่มฟรีไหม": "มีน้ำดื่มฟรีสำหรับลูกค้าค่ะ",
    "ร้านมีบริการขนมไหม": "มีขนมบริการสำหรับลูกค้าค่ะ",
    "ร้านมีบริการอินเทอร์เน็ตฟรีไหม": "มี Wi-Fi ฟรีสำหรับลูกค้าค่ะ",
    "ร้านมีบริการชาร์จมือถือไหม": "มีจุดชาร์จมือถือให้บริการค่ะ",
    "ร้านมีบริการนวดมือไหม": "มีบริการนวดมือสำหรับลูกค้าค่ะ",
    "ร้านมีบริการนวดเท้าไหม": "มีบริการนวดเท้าสำหรับลูกค้าค่ะ",
    "ร้านมีบริการสปาเท้าไหม": "มีบริการสปาเท้าค่ะ",
    "ร้านมีบริการสปามือไหม": "มีบริการสปามือค่ะ",
    "ร้านมีบริการถ่ายรูปไหม": "มีมุมถ่ายรูปสวย ๆ ให้บริการค่ะ",
    "ร้านมีบริการแต่งหน้าไหม": "ขออภัยค่ะ ยังไม่มีบริการแต่งหน้า",
    "ร้านมีบริการทำผมไหม": "ขออภัยค่ะ ยังไม่มีบริการทำผม",
    "ร้านมีบริการแต่งตัวไหม": "ขออภัยค่ะ ยังไม่มีบริการแต่งตัว",
    "ร้านมีบริการดูแลเด็กไหม": "มีบริการดูแลเด็กสำหรับลูกค้าที่พาเด็กมาด้วยค่ะ",
    "ร้านมีบริการดูแลผู้สูงอายุไหม": "มีบริการดูแลผู้สูงอายุค่ะ",
    "ร้านมีบริการรับส่งไหม": "ขออภัยค่ะ ยังไม่มีบริการรับส่ง",
    "ร้านมีบริการจองคิวออนไลน์ไหม": "สามารถจองคิวผ่าน LINE ได้เลยค่ะ",
    "ร้านมีบริการจองคิวโทรศัพท์ไหม": "สามารถจองคิวทางโทรศัพท์ได้ค่ะ",
    "ร้านมีบริการจองคิวหน้าร้านไหม": "สามารถจองคิวที่หน้าร้านได้ค่ะ",
    "ร้านมีบริการแจ้งเตือนคิวไหม": "มีบริการแจ้งเตือนคิวผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งเตือนโปรโมชั่นไหม": "มีบริการแจ้งโปรโมชั่นผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งข่าวสารไหม": "มีบริการแจ้งข่าวสารผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันหยุดไหม": "มีบริการแจ้งวันหยุดผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันเปิดไหม": "มีบริการแจ้งวันเปิดผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันปิดไหม": "มีบริการแจ้งวันปิดผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันจองไหม": "มีบริการแจ้งวันจองผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันบริการไหม": "มีบริการแจ้งวันบริการผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันโปรโมชั่นไหม": "มีบริการแจ้งวันโปรโมชั่นผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันนัดหมายไหม": "มีบริการแจ้งวันนัดหมายผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันรอคิวไหม": "มีบริการแจ้งวันรอคิวผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันดูแลลูกค้าไหม": "มีบริการแจ้งวันดูแลลูกค้าผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันสำคัญไหม": "มีบริการแจ้งวันสำคัญผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันกิจกรรมไหม": "มีบริการแจ้งวันกิจกรรมผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันเทศกาลไหม": "มีบริการแจ้งวันเทศกาลผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันฤดูกาลไหม": "มีบริการแจ้งวันฤดูกาลผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันสุขภาพไหม": "มีบริการแจ้งวันสุขภาพผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันโปรโมชั่นพิเศษไหม": "มีบริการแจ้งวันโปรโมชั่นพิเศษผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันรับปริญญาไหม": "มีบริการแจ้งวันรับปริญญาผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันแต่งงานไหม": "มีบริการแจ้งวันแต่งงานผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันวันเกิดไหม": "มีบริการแจ้งวันวันเกิดผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันคริสต์มาสไหม": "มีบริการแจ้งวันคริสต์มาสผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันปีใหม่ไหม": "มีบริการแจ้งวันปีใหม่ผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันสงกรานต์ไหม": "มีบริการแจ้งวันสงกรานต์ผ่าน LINE ค่ะ",
    "ร้านมีบริการแจ้งวันตรุษจีนไหม": "มีบริการแจ้งวันตรุษจีนผ่าน LINE ค่ะ",
    "วิธีป้องกันเล็บเหลือง": "ควรหลีกเลี่ยงการใช้ยาทาเล็บที่มีสารเคมีรุนแรงและบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บเปราะง่ายควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันบำรุงเล็บและหลีกเลี่ยงการกัดเล็บค่ะ",
    "เล็บฉีกบ่อยควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมบำรุงเล็บค่ะ",
    "เล็บไม่แข็งแรงควรดูแลอย่างไร": "ควรรับประทานอาหารที่มีแคลเซียมและบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีจุดขาวเกิดจากอะไร": "อาจเกิดจากการขาดแร่ธาตุหรือได้รับการกระแทกค่ะ",
    "เล็บมีรอยดำควรทำอย่างไร": "ควรปรึกษาแพทย์หากรอยดำไม่หายไปค่ะ",
    "เล็บมีเชื้อรารักษาอย่างไร": "ควรปรึกษาแพทย์และหลีกเลี่ยงความชื้นค่ะ",
    "เล็บขุ่นมัวควรดูแลยังไง": "ควรล้างเล็บให้สะอาดและบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บเป็นคลื่นเกิดจากอะไร": "อาจเกิดจากการขาดสารอาหารหรือโรคบางชนิดค่ะ",
    "เล็บมีรอยแตกควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมบำรุงเล็บค่ะ",
    "เล็บมีรอยบุ๋มควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์หากไม่ดีขึ้นค่ะ",
    "เล็บมีรอยขีดควรดูแลยังไง": "ควรหลีกเลี่ยงการกระแทกและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาวควรทำอย่างไร": "อาจเกิดจากการขาดแร่ธาตุ ควรรับประทานอาหารที่มีแร่ธาตุค่ะ",
    "เล็บมีรอยเหลืองควรแก้ไขยังไง": "ควรหลีกเลี่ยงการใช้ยาทาเล็บที่มีสารเคมีรุนแรงค่ะ",
    "เล็บมีรอยดำควรดูแลยังไง": "ควรปรึกษาแพทย์หากรอยดำไม่หายไปค่ะ",
    "เล็บมีรอยคล้ำควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยแดงควรดูแลยังไง": "ควรหลีกเลี่ยงการกระแทกและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยบวมควรทำอย่างไร": "ควรปรึกษาแพทย์หากบวมไม่หายไปค่ะ",
    "เล็บมีรอยอักเสบควรดูแลยังไง": "ควรปรึกษาแพทย์และหลีกเลี่ยงการสัมผัสสิ่งสกปรกค่ะ",
    "เล็บมีรอยเจ็บควรทำอย่างไร": "ควรพักการใช้เล็บและบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยลอกควรดูแลยังไง": "ควรบำรุงด้วยครีมเล็บและหลีกเลี่ยงการกัดเล็บค่ะ",
    "เล็บมีรอยแตกควรทำอย่างไร": "ควรตัดเล็บให้สั้นและบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขรุขระควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรบำรุงด้วยน้ำมันเล็บและหลีกเลี่ยงการกัดเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "เล็บมีรอยขาดควรแก้ไขยังไง": "ควรตัดเล็บให้สั้นและบำรุงด้วยครีมเล็บค่ะ",
    "เล็บมีรอยขาดควรทำอย่างไร": "ควรบำรุงด้วยน้ำมันเล็บและปรึกษาแพทย์ค่ะ",
    "เล็บมีรอยขาดควรดูแลยังไง": "ควรขัดเล็บเบา ๆ และบำรุงด้วยน้ำมันเล็บค่ะ",
    "ควรเลือกสีเล็บตามฤดูไหม": "แนะนำให้เลือกสีสดใสในฤดูร้อน สีเข้มในฤดูหนาวค่ะ",
    "ควรเลือกสีเล็บตามเทศกาลไหม": "แนะนำให้เลือกสีแดงในเทศกาลตรุษจีน สีเขียวแดงในคริสต์มาสค่ะ",
    "ควรเลือกสีเล็บตามงานที่ไปไหม": "แนะนำให้เลือกสีสุภาพสำหรับงานทางการ สีสดใสสำหรับงานปาร์ตี้ค่ะ",
    "ควรเลือกสีเล็บตามชุดที่ใส่ไหม": "แนะนำให้เลือกสีที่เข้ากับชุดค่ะ",
    "ควรเลือกสีเล็บตามบุคลิกไหม": "แนะนำให้เลือกสีที่เหมาะกับบุคลิกค่ะ",
    "ควรเลือกสีเล็บตามอายุไหม": "แนะนำให้เลือกสีที่เหมาะกับวัยค่ะ",
    "ควรเลือกสีเล็บตามอาชีพไหม": "แนะนำให้เลือกสีสุภาพสำหรับอาชีพที่ต้องการความเรียบร้อยค่ะ",
    "ควรเลือกสีเล็บตามความชอบไหม": "แนะนำให้เลือกสีที่ชอบและมั่นใจค่ะ",
    "ควรเลือกสีเล็บตามงบประมาณไหม": "แนะนำให้เลือกสีที่เหมาะกับงบประมาณค่ะ",
    "ควรเลือกสีเล็บตามความสะดวกไหม": "แนะนำให้เลือกสีที่ดูแลง่ายค่ะ",
    "ควรเลือกสีเล็บตามความทนทานไหม": "แนะนำให้เลือกสีที่ติดทนนานค่ะ",
    "ควรเลือกสีเล็บตามความปลอดภัยไหม": "แนะนำให้เลือกสีที่ปลอดภัยต่อสุขภาพค่ะ",
    "ควรเลือกสีเล็บตามความนิยมไหม": "แนะนำให้เลือกสีที่นิยมในช่วงนั้นค่ะ",
    "ควรเลือกสีเล็บตามความต้องการไหม": "แนะนำให้เลือกสีที่ตรงกับความต้องการค่ะ",
    "ควรเลือกสีเล็บตามความมั่นใจไหม": "แนะนำให้เลือกสีที่ทำให้มั่นใจค่ะ",
    "ควรเลือกสีเล็บตามความสะอาดไหม": "แนะนำให้เลือกสีที่ดูแลความสะอาดง่ายค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมไหม": "แนะนำให้เลือกสีที่เหมาะสมกับโอกาสค่ะ",
    "ควรเลือกสีเล็บตามความสวยงามไหม": "แนะนำให้เลือกสีที่สวยงามและเหมาะกับตัวเองค่ะ",
    "ควรเลือกสีเล็บตามความง่ายในการดูแลไหม": "แนะนำให้เลือกสีที่ดูแลง่ายค่ะ",
    "ควรเลือกสีเล็บตามความปลอดภัยของผลิตภัณฑ์ไหม": "แนะนำให้เลือกผลิตภัณฑ์ที่ปลอดภัยค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับมือไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปมือค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับเท้าไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปเท้าค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับนิ้วไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปนิ้วค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับเล็บไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปเล็บค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับใบหน้าไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปหน้าและบุคลิกค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับรูปร่างไหม": "แนะนำให้เลือกสีที่เหมาะกับรูปร่างค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับสไตล์ไหม": "แนะนำให้เลือกสีที่เหมาะกับสไตล์ของแต่ละคนค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับเทรนด์ไหม": "แนะนำให้เลือกสีที่เหมาะกับเทรนด์ปัจจุบันค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับฤดูกาลไหม": "แนะนำให้เลือกสีที่เหมาะกับฤดูกาลค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับเทศกาลไหม": "แนะนำให้เลือกสีที่เหมาะกับเทศกาลค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับวันสำคัญไหม": "แนะนำให้เลือกสีที่เหมาะกับวันสำคัญค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับงานสำคัญไหม": "แนะนำให้เลือกสีที่เหมาะกับงานสำคัญค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับกิจกรรมไหม": "แนะนำให้เลือกสีที่เหมาะกับกิจกรรมค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับสถานที่ไหม": "แนะนำให้เลือกสีที่เหมาะกับสถานที่ค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับเวลาไหม": "แนะนำให้เลือกสีที่เหมาะกับเวลาค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับฤดูไหม": "แนะนำให้เลือกสีที่เหมาะกับฤดูค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับสภาพอากาศไหม": "แนะนำให้เลือกสีที่เหมาะกับสภาพอากาศค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับสภาพผิวไหม": "แนะนำให้เลือกสีที่เหมาะกับสภาพผิวค่ะ",
    "ควรเลือกสีเล็บตามความเหมาะสมกับสุขภาพไหม": "แนะนำให้เลือกสีที่เหมาะกับสุขภาพค่ะ",
    "ควรเลือกทรงเล็บตามฤดูไหม": "แนะนำให้เลือกทรงอัลมอนด์ในฤดูร้อน ทรงเหลี่ยมในฤดูหนาวค่ะ",
    "ควรเลือกทรงเล็บตามเทศกาลไหม": "แนะนำให้เลือกทรงกลมในเทศกาลตรุษจีน ทรงรีในคริสต์มาสค่ะ",
    "ควรเลือกทรงเล็บตามงานที่ไปไหม": "แนะนำให้เลือกทรงสุภาพสำหรับงานทางการ ทรงแฟนซีสำหรับงานปาร์ตี้ค่ะ",
    "ควรเลือกทรงเล็บตามชุดที่ใส่ไหม": "แนะนำให้เลือกทรงที่เข้ากับชุดค่ะ",
    "ควรเลือกทรงเล็บตามบุคลิกไหม": "แนะนำให้เลือกทรงที่เหมาะกับบุคลิกค่ะ",
    "ควรเลือกทรงเล็บตามอายุไหม": "แนะนำให้เลือกทรงที่เหมาะกับวัยค่ะ",
    "ควรเลือกทรงเล็บตามอาชีพไหม": "แนะนำให้เลือกทรงสุภาพสำหรับอาชีพที่ต้องการความเรียบร้อยค่ะ",
    "ควรเลือกทรงเล็บตามความชอบไหม": "แนะนำให้เลือกทรงที่ชอบและมั่นใจค่ะ",
    "ควรเลือกทรงเล็บตามงบประมาณไหม": "แนะนำให้เลือกทรงที่เหมาะกับงบประมาณค่ะ",
    "ควรเลือกทรงเล็บตามความสะดวกไหม": "แนะนำให้เลือกทรงที่ดูแลง่ายค่ะ",
    "ควรดูแลเล็บอย่างไร": "ควรตัดเล็บให้สั้นอยู่เสมอและบำรุงด้วยน้ำมันบำรุงเล็บค่ะ",
    "ควรเลือกน้ำยาทาเล็บแบบไหน": "ควรเลือกน้ำยาทาเล็บที่ไม่มีสารเคมีรุนแรงและปลอดภัยค่ะ",
    "ควรเลือกสีเล็บตามโอกาสไหม": "แนะนำให้เลือกสีเล็บตามโอกาส เช่น งานแต่งงาน สีอ่อน งานปาร์ตี้ สีสดใสค่ะ",
    "ควรเลือกทรงเล็บตามรูปมือไหม": "แนะนำให้เลือกทรงเล็บที่เหมาะกับรูปมือเพื่อความสวยงามค่ะ",
    "ควรบำรุงเล็บบ่อยแค่ไหน": "ควรบำรุงเล็บทุกวันด้วยน้ำมันบำรุงเล็บค่ะ",
    "ควรหลีกเลี่ยงอะไรบ้างในการดูแลเล็บ": "ควรหลีกเลี่ยงการกัดเล็บและใช้เล็บเปิดสิ่งของค่ะ",
    "ควรใช้ผลิตภัณฑ์บำรุงเล็บอะไร": "แนะนำให้ใช้น้ำมันบำรุงเล็บและครีมบำรุงมือค่ะ",
    "ควรล้างเล็บบ่อยไหม": "ควรล้างเล็บเมื่อเปลี่ยนสีหรือมีคราบสกปรกค่ะ",
    "ควรตัดหนังรอบเล็บบ่อยไหม": "ไม่ควรตัดหนังรอบเล็บบ่อยเกินไปเพื่อป้องกันการอักเสบค่ะ",
    "ควรเลือกแบบเล็บตามฤดูกาลไหม": "แนะนำให้เลือกแบบเล็บตามฤดูกาล เช่น ฤดูร้อน สีสดใส ฤดูหนาว สีเข้มค่ะ",
    "ควรเลือกแบบเล็บตามแฟชั่นไหม": "แนะนำให้เลือกแบบเล็บที่กำลังเป็นเทรนด์ค่ะ",
    "ควรเลือกแบบเล็บตามบุคลิกไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับบุคลิกของแต่ละคนค่ะ",
    "ควรเลือกแบบเล็บตามชุดที่ใส่ไหม": "แนะนำให้เลือกแบบเล็บที่เข้ากับชุดค่ะ",
    "ควรเลือกแบบเล็บตามงานที่ไปไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับงานที่ไปค่ะ",
    "ควรเลือกแบบเล็บตามสีผิวไหม": "แนะนำให้เลือกสีเล็บที่เข้ากับสีผิวค่ะ",
    "ควรเลือกแบบเล็บตามอายุไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับวัยค่ะ",
    "ควรเลือกแบบเล็บตามอาชีพไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับอาชีพค่ะ",
    "ควรเลือกแบบเล็บตามความชอบไหม": "แนะนำให้เลือกแบบเล็บที่ชอบและมั่นใจค่ะ",
    "ควรเลือกแบบเล็บตามงบประมาณไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับงบประมาณค่ะ",
    "ควรเลือกแบบเล็บตามความสะดวกไหม": "แนะนำให้เลือกแบบเล็บที่สะดวกต่อการดูแลค่ะ",
    "ควรเลือกแบบเล็บตามความทนทานไหม": "แนะนำให้เลือกแบบเล็บที่ทนทานต่อการใช้งานค่ะ",
    "ควรเลือกแบบเล็บตามความปลอดภัยไหม": "แนะนำให้เลือกแบบเล็บที่ปลอดภัยต่อสุขภาพค่ะ",
    "ควรเลือกแบบเล็บตามความง่ายในการดูแลไหม": "แนะนำให้เลือกแบบเล็บที่ดูแลง่ายค่ะ",
    "ควรเลือกแบบเล็บตามความสวยงามไหม": "แนะนำให้เลือกแบบเล็บที่สวยงามและเหมาะกับตัวเองค่ะ",
    "ควรเลือกแบบเล็บตามความนิยมไหม": "แนะนำให้เลือกแบบเล็บที่นิยมในช่วงนั้นค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะสมกับโอกาสค่ะ",
    "ควรเลือกแบบเล็บตามความต้องการไหม": "แนะนำให้เลือกแบบเล็บที่ตรงกับความต้องการค่ะ",
    "ควรเลือกแบบเล็บตามความมั่นใจไหม": "แนะนำให้เลือกแบบเล็บที่ทำให้มั่นใจค่ะ",
    "ควรเลือกแบบเล็บตามความสะอาดไหม": "แนะนำให้เลือกแบบเล็บที่ดูแลความสะอาดง่ายค่ะ",
    "ควรเลือกแบบเล็บตามความปลอดภัยของผลิตภัณฑ์ไหม": "แนะนำให้เลือกผลิตภัณฑ์ที่ปลอดภัยค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับมือไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปมือค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับเท้าไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปเท้าค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับนิ้วไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปนิ้วค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับเล็บไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปเล็บค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับใบหน้าไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปหน้าและบุคลิกค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับรูปร่างไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับรูปร่างค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับสไตล์ไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับสไตล์ของแต่ละคนค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับเทรนด์ไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับเทรนด์ปัจจุบันค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับฤดูกาลไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับฤดูกาลค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับเทศกาลไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับเทศกาลค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับวันสำคัญไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับวันสำคัญค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับงานสำคัญไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับงานสำคัญค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับกิจกรรมไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับกิจกรรมค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับสถานที่ไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับสถานที่ค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับเวลาไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับเวลาค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับฤดูไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับฤดูค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับสภาพอากาศไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับสภาพอากาศค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับสภาพผิวไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับสภาพผิวค่ะ",
    "ควรเลือกแบบเล็บตามความเหมาะสมกับสุขภาพไหม": "แนะนำให้เลือกแบบเล็บที่เหมาะกับสุขภาพค่ะ",
    "มีสีเล็บแนะนำไหม": "แนะนำสีชมพู สีขาว สีพาสเทล และสีโทนธรรมชาติค่ะ",
    "มีทรงเล็บแนะนำไหม": "แนะนำทรงอัลมอนด์ ทรงเหลี่ยม ทรงรี และทรงกลมค่ะ",
    "มีลายเล็บแนะนำไหม": "แนะนำลายดอกไม้ ลายมินิมอล ลายเกาหลี และลายแฟนซีค่ะ",
    "มีแบบเล็บเจลแนะนำไหม": "แนะนำเจลใส เจลสีพาสเทล และเจลลายเกาหลีค่ะ",
    "มีแบบเล็บอะคริลิกแนะนำไหม": "แนะนำอะคริลิกสีธรรมชาติและลายเรียบง่ายค่ะ",
    "มีแบบเล็บ PVC แนะนำไหม": "แนะนำ PVC สีขาว สีชมพู และลายแฟนซีค่ะ",
    "มีแบบเล็บสั้นแนะนำไหม": "แนะนำทรงกลมและทรงรีสำหรับเล็บสั้นค่ะ",
    "มีแบบเล็บยาวแนะนำไหม": "แนะนำทรงอัลมอนด์และทรงเหลี่ยมสำหรับเล็บยาวค่ะ",
    "มีแบบเล็บเจ้าสาวแนะนำไหม": "แนะนำสีขาว สีชมพูอ่อน และลายดอกไม้ค่ะ",
    "มีแบบเล็บเจ้าบ่าวแนะนำไหม": "แนะนำสีธรรมชาติและทรงเรียบง่ายค่ะ",
    "มีแบบเล็บเด็กแนะนำไหม": "แนะนำลายการ์ตูนและสีสดใสค่ะ",
    "มีแบบเล็บผู้ชายแนะนำไหม": "แนะนำสีธรรมชาติและทรงเหลี่ยมค่ะ",
    "มีแบบเล็บผู้สูงอายุแนะนำไหม": "แนะนำสีธรรมชาติและทรงกลมค่ะ",
    "มีแบบเล็บรับปริญญาแนะนำไหม": "แนะนำสีขาว สีฟ้า และลายเรียบง่ายค่ะ",
    "มีแบบเล็บวันเกิดแนะนำไหม": "แนะนำลายเค้ก ลายลูกโป่ง และสีสดใสค่ะ",
    "มีแบบเล็บปีใหม่แนะนำไหม": "แนะนำสีแดง สีทอง และลายดาวค่ะ",
    "มีแบบเล็บคริสต์มาสแนะนำไหม": "แนะนำลายต้นคริสต์มาส ลายกวาง และสีเขียวแดงค่ะ",
    "มีแบบเล็บวาเลนไทน์แนะนำไหม": "แนะนำลายหัวใจ สีชมพู และลายดอกไม้ค่ะ",
    "มีแบบเล็บสงกรานต์แนะนำไหม": "แนะนำลายดอกไม้ สีฟ้า และลายสดใสค่ะ",
    "มีแบบเล็บตรุษจีนแนะนำไหม": "แนะนำสีแดง สีทอง และลายมังกรค่ะ",
    "มีแบบเล็บฮาโลวีนแนะนำไหม": "แนะนำลายฟักทอง ลายผี และสีดำส้มค่ะ",
    "มีแบบเล็บลายดอกไม้แนะนำไหม": "แนะนำลายดอกกุหลาบ ลายดอกทานตะวัน และลายดอกซากุระค่ะ",
    "มีแบบเล็บลายการ์ตูนแนะนำไหม": "แนะนำลายมิกกี้เมาส์ ลายคิตตี้ และลายโดราเอมอนค่ะ",
    "มีแบบเล็บลายมินิมอลแนะนำไหม": "แนะนำลายเส้น สีพื้น และลายจุดค่ะ",
    "มีแบบเล็บลายเกาหลีแนะนำไหม": "แนะนำลายเกาหลีโทนพาสเทลและลายเรียบง่ายค่ะ",
    "มีแบบเล็บลายญี่ปุ่นแนะนำไหม": "แนะนำลายญี่ปุ่นโทนสดใสและลายดอกไม้ค่ะ",
    "มีแบบเล็บลายฝรั่งเศสแนะนำไหม": "แนะนำลายปลายขาวและลายเรียบง่ายค่ะ",
    "มีแบบเล็บลายแฟนซีแนะนำไหม": "แนะนำลายกลิตเตอร์ ลายเพชร และลายสีสดใสค่ะ",
    "มีแบบเล็บลายเรียบง่ายแนะนำไหม": "แนะนำสีพื้นและลายเส้นบาง ๆ ค่ะ",
    "มีแบบเล็บลายหรูหราแนะนำไหม": "แนะนำลายทอง ลายเพชร และสีเมทัลลิคค่ะ",
    "มีแบบเล็บลายเจ้าสาวแนะนำไหม": "แนะนำลายดอกไม้ สีขาว และกลิตเตอร์ค่ะ",
    "มีแบบเล็บลายเจ้าบ่าวแนะนำไหม": "แนะนำลายเรียบง่ายและสีธรรมชาติค่ะ",
    "มีแบบเล็บลายเด็กแนะนำไหม": "แนะนำลายการ์ตูนและสีสดใสค่ะ",
    "มีแบบเล็บลายผู้ชายแนะนำไหม": "แนะนำลายเรียบง่ายและสีธรรมชาติค่ะ",
    "มีแบบเล็บลายผู้สูงอายุแนะนำไหม": "แนะนำลายดอกไม้และสีธรรมชาติค่ะ",
    "มีแบบเล็บลายรับปริญญาแนะนำไหม": "แนะนำลายหมวกรับปริญญาและสีฟ้าค่ะ",
    "มีแบบเล็บลายวันเกิดแนะนำไหม": "แนะนำลายเค้กและสีสดใสค่ะ",
    "มีแบบเล็บลายปีใหม่แนะนำไหม": "แนะนำลายดาวและสีทองค่ะ",
    "มีแบบเล็บลายคริสต์มาสแนะนำไหม": "แนะนำลายต้นคริสต์มาสและสีเขียวแดงค่ะ",
    "มีแบบเล็บลายวาเลนไทน์แนะนำไหม": "แนะนำลายหัวใจและสีชมพูค่ะ",
    "มีแบบเล็บลายสงกรานต์แนะนำไหม": "แนะนำลายดอกไม้และสีฟ้าค่ะ",
    "มีแบบเล็บลายตรุษจีนแนะนำไหม": "แนะนำลายมังกรและสีแดงทองค่ะ",
    "มีแบบเล็บลายฮาโลวีนแนะนำไหม": "แนะนำลายฟักทองและสีดำส้มค่ะ",
    "ควย": "พ่อมึงสิ อีสัส!!",
    "เย็ดแม่": "พ่อมึงตาย",
    "ไอ้": "มึงสิไอ้ควาย",
    "หี": "หีแม่มึงไง",
    "หน้าหี": "หีแม่มึงไง",
    "ไอ้สัส": "หมายถึงเพื่อนมึงที่อยู่ในป่าใช่ปะ",
    "ไอ้สัตว์": "หมายถึงเพื่อนมึงที่อยู่ในป่าใช่ปะ",
    "ไอ้โง่": "ยังดีไม่โง่เท่ามึง",
    "พูดไม่เพราะ": "จะพูดเพราะกับคนดีๆเท่านั้นค่ะ",
    "ส้นตีน": "ทำไม จะขัดส้นตีนหรอคะ",
    "ไอ้เวร": "มึงสิไอ้เวร",
    "ไอ้เหี้ย": "เทียบกับมึง เหี้ยยังดีกว่า",
    "ไอ้แม่เย็ด": "ส่วนมึงไอ้เย็ดแม่",
    "ไอ้เย็ดแม่": "ส่วนมึงไอ้แม่เย็ด",
    "ไอ้หน้าหมา": "หมามึงยังน่ารักกว่า",
    "ไอ้หน้าลิง": "ลิงยังฉลาดกว่ามึง",
    "ไอ้หน้าตัวเมีย": "ตัวเมียยังสวยกว่ามึง",
    "ไอ้หน้าตัวผู้": "ตัวผู้ยังหล่อกว่ามึง",
    "ไอ้หน้าหมา": "หมามึงยังน่ารักกว่า",
    "ไอ้หน้าลิง": "ลิงยังฉลาดกว่ามึง",
    "ไอ้หน้าตัวเมีย": "ตัวเมียยังสวยกว่ามึง",
    "ไอ้หน้าตัวผู้": "ตัวผู้ยังหล่อกว่ามึง",
    "ไอ้หน้าหมา": "หมามึงยังน่ารักกว่า",
    "ไอ้หน้าลิง": "ลิงยังฉลาดกว่ามึง",
    "ไอ้หน้าตัวเมีย": "ตัวเมียยังสวยกว่ามึง",
    "ไอ้หน้าตัวผู้": "ตัวผู้ยังหล่อกว่ามึง",
    "ไอ้ควาย": "ควายยังฉลาดกว่ามึง",
    "ไอ้หน้าด้าน": "หน้าด้านยังดีกว่าหน้ามึง",
    "ไอ้หน้าหมา": "หมามึงยังน่ารักกว่า",
    "ไอ้หน้าลิง": "ลิงยังฉลาดกว่ามึง"
    }

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
    else:
        closest = find_closest_question(user_message, FAQ)
        if closest:
            reply_text = FAQ[closest]
        else:
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
