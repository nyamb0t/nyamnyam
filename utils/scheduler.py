# utils/scheduler.py
# --- リマインダー機能の「時間管理」部分！
#     毎日・一度きりのメッセージを、指定時刻にちゃんと送れるようにする仕組み！

from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from utils.send_reminder import send_reminder_message

# スケジューラーの本体を作成（非同期対応）
scheduler = AsyncIOScheduler()

# --- 毎日リマインダーを登録する関数
def schedule_daily_reminder(bot, guild_id, time, message, channel_id, jobs, reminder_type):
    hour, minute = map(int, time.split(":"))  # 時刻（"09:00"）を数字に変換
    
    jst = timezone('Asia/Tokyo') # 日本時間にする
    trigger = CronTrigger(hour=hour, minute=minute, timezone=jst)  # 毎日同じ時間に起動するトリガー

    job_id = f"{reminder_type}_{guild_id}_{channel_id}_{time}"  # ユニークなIDで管理

    jobs[job_id] = scheduler.add_job(
        send_reminder_message,
        trigger,
        args=[bot, channel_id, message],
        id=job_id,
        replace_existing=True  # 同じIDのジョブがあれば上書き
    )

# --- 毎日リマインダーのキャンセル関数
def cancel_daily_reminder(guild_id, time, channel_id, jobs, reminder_type):
    job_id = f"{reminder_type}_{guild_id}_{channel_id}_{time}"
    if job_id in jobs:
        jobs[job_id].remove()  # ジョブをスケジューラーから削除
        del jobs[job_id]       # 登録済みリストからも削除

# --- 一度だけのリマインダーを登録する関数
def schedule_one_time_reminder(bot, reminder_data):
    from datetime import datetime
    run_date = datetime.fromisoformat(reminder_data["time"])
    job_id = reminder_data["id"]

    scheduler.add_job(
        send_reminder_message,
        trigger=DateTrigger(run_date=run_date),  # 一回だけのトリガー
        args=[bot, reminder_data["channel_id"], reminder_data["message"]],
        id=job_id,
        replace_existing=True
    )

# --- スケジューラーを起動（まだ動いてなければ）
def start_scheduler():
    if not scheduler.running:
        scheduler.start()