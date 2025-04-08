# utils/send_reminder.py
# --- チャンネルにリマインダーのメッセージを送る処理だけを、共通関数として分離！

async def send_reminder_message(bot, channel_id, message):
    # Botがチャンネルを取得
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)