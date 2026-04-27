# bot.py
import os
import threading
import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from fastapi import FastAPI

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# 👇 [수정 지점 1] 여기에 @userinfobot 에서 확인한 본인 숫자 ID 입력
OWNER_ID = 7958659939  # <-- 예: 123456789 (반드시 숫자로만 입력)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "alive", "time": datetime.datetime.utcnow().isoformat()}

def format_world_time():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    tz_list = [
        ("KST", "대한민국", "Asia/Seoul", "🇰🇷", "UTC +09:00"),
        ("GMT", "런던", "Etc/GMT", "🇬🇧", "UTC +00:00"),
        ("EST", "뉴욕", "America/New_York", "🇺🇸", "UTC -05:00"),
        ("JST", "도쿄", "Asia/Tokyo", "🇯🇵", "UTC +09:00"),
        ("GST", "두바이", "Asia/Dubai", "🇦🇪", "UTC +04:00")
    ]
    
    lines = []
    for i, (code, city, tz_name, flag, offset) in enumerate(tz_list):
        tz = ZoneInfo(tz_name)
        dt = now_utc.astimezone(tz)
        
        date_str = f"{dt.year % 100}. {dt.month}. {dt.day}."
        weekdays = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
        weekday_kr = weekdays[dt.weekday()]
        
        h = dt.hour if dt.hour <= 12 else dt.hour - 12
        if h == 0: h = 12
        period = "오전" if dt.hour < 12 else "오후"
        m_s = dt.strftime("%M:%S")
        time_str = f"{period} {h}:{m_s}"
        
        if i == 0:
            lines.append(f"{flag} {city} 표준 시 [{code}] = {offset}")
            lines.append(f"  🗓 현 재 날 짜 : {date_str} [{weekday_kr}]")
            lines.append(f"  ⏰ 현 재 시 간 : {time_str}")
        else:
            lines.append("")
            lines.append("────────────")
            lines.append(f" {flag} {city} 표준 시 [{code}] = {offset}")
            lines.append(f"  🗓 현 재 날 짜 : {date_str} [{weekday_kr}]")
            lines.append(f"  ⏰ 현 재 시 간 : {time_str}")
            
    return "\n".join(lines)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 👇 [수정 지점 2] /start 명령어도 소유자만 사용 가능하게 제한
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⚠️ 이 봇은 관리자 전용입니다.")
        return
    await update.message.reply_text("안녕 하세요 !!", parse_mode="Markdown")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 👇 [수정 지점 3] /time 명령어에 소유자 확인 로직 적용
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⚠️ 이 봇은 관리자 전용입니다.")
        return
    
    msg = format_world_time()
    await update.message.reply_text(msg)

def run_telegram_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("time", time_command))
    print("🤖 텔레그램 봇 실행 중 입니다.")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)