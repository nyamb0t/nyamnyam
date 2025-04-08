# commands/reminder/one_time.py
# --- 一回きりのリマインダーをセットするためのコマンド群！
#     !setonce [日付] [時間] [メッセージ] でリマインドを予約できる！

import discord
from discord.ext import commands
from datetime import datetime
from utils.scheduler import schedule_one_time_reminder
from utils.reminder_storage import save_one_time_reminder, load_one_time_reminders

class OneTimeReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setonce")
    async def set_one_time_reminder(self, ctx, time_str: str, *, message: str):
        """
        !setonce 2025-04-10 18:30 メッセージ
        の形式で一度きりの通知を設定する
        """
        try:
            # 日付と時間をまとめてパース（例：2025-04-10 18:30）
            reminder_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            now = datetime.now()

            if reminder_time <= now:
                await ctx.send("過去の日時は指定できません。")
                return

            # ギルドIDとチャンネル情報を取得
            guild_id = str(ctx.guild.id)
            channel_id = ctx.channel.id

            # 識別用のIDを作成（タイムスタンプをベースにする）
            reminder_id = f"{guild_id}_{reminder_time.timestamp()}"

            # 保存するリマインダー情報
            reminder_data = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "time": reminder_time.isoformat(),
                "message": message,
                "id": reminder_id
            }

            # JSONに保存して、スケジューラーにも登録！
            save_one_time_reminder(reminder_data)
            schedule_one_time_reminder(self.bot, reminder_data)

            await ctx.send(f"1回だけのリマインダーを設定しました：{time_str} に「{message}」")
        except ValueError:
            await ctx.send("日付の形式が正しくありません。例：2025-04-10 18:30")

# コマンドをBotに登録する setup 関数（setup_reminder から呼ばれる）
async def setup(bot):
    await bot.add_cog(OneTimeReminder(bot))



