import os
import asyncio
import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from fastapi import FastAPI

# 1. 설정
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = 7958659939  # 본인 텔레그램 숫자 ID

# 2. FastAPI 앱
app = FastAPI()

# 3. 텔레그램 앱 전역 변수
telegram_app = None

async def start_telegram_bot():
    """비동기로 텔레그램 봇 실행"""
    global telegram_app
    
    try:
        print("⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ 봇 초기화 중...")
        
        # 봇 애플리케이션 빌드
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        
        # 명령어 핸들러 등록
        telegram_app.add_handler(CommandHandler("start", start_command))
        telegram_app.add_handler(CommandHandler("현재시간", time_command))
        
        print("⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ 정상 실행 중 입니다.")
        
        # 비동기 폴링 실행 (Render 호환)
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ ERROR: {e}")

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 봇 실행"""
    print(" ⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ 서버 실행 완료 입니다.")
    asyncio.create_task(start_telegram_bot())

@app.get("/health")
def health():
    return {"status": "alive", "time": datetime.datetime.now(datetime.timezone.utc).isoformat()}

def format_world_time():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    tz_list = [
        ("KST", "대한민국", "Asia/Seoul", "🇰🇷", "UTC +09:00"),
        ("JST", "도쿄", "Asia/Tokyo", "🇯🇵", "UTC +09:00"),
        ("GST", "두바이", "Asia/Dubai", "🇦🇪", "UTC +04:00"),
        ("MSK", "모스크바", "Europe/Moscow", "🇷🇺", "UTC +03:00"),
        ("EST", "뉴욕", "America/New_York", "🇺🇸", "UTC -05:00"),
        ("GMT", "런던", "Europe/London", "🇬🇧", "UTC +00:00"),
        ("CET", "파리", "Europe/Paris", "🇫🇷", "UTC +01:00"),
        ("BRT", "브라질", "America/Sao_Paulo", "🇧🇷", "UTC -03:00"),
        ("SGT", "싱가포르", "Asia/Singapore", "🇸🇬", "UTC +08:00"),
        ("AEST", "호주", "Australia/Sydney", "🇦🇺", "UTC +10:00"),
        ("HKT", "홍콩", "Asia/Hong_Kong", "🇭🇰", "UTC +08:00"),
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
    """/start 명령어"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ 명령어 입니다.")
        return
    await update.message.reply_text("⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆.")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/현재시간 명령어"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⚫️ 𝗡Ø𝗫•Σ𝗩𝗤†∆ 명령어 입니다.")
        return
    
    msg = format_world_time()
    await update.message.reply_text(msg)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)