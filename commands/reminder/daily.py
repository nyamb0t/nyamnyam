# commands/render/daily.py
# --- 毎日決まった時間にリマインダーを送るコマンド定義ファイル！

import discord
from discord.ext import commands
from discord import app_commands
from utils.scheduler import schedule_daily_reminder, cancel_daily_reminder
from utils.reminder_storage import load_reminders, save_reminders

REMINDER_TYPE = "daily"
registered_jobs = {}

class DailyReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- /setdaily 00:00 [チャンネル] メッセージ
    @app_commands.command(name="setdaily", description="毎日決まった時間にリマインダーを送るよ")
    @app_commands.describe(time="時間（例: 09:00）", channel="送信先チャンネル", message="送るメッセージ")
    async def set_daily(self, interaction: discord.Interaction, time: str, message: str, channel: discord.TextChannel = None):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        channel = channel or interaction.channel
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # 重複チェック
        for r in reminders:
            if r["time"] == time and r["channel_id"] == channel.id:
                await interaction.followup.send("その時間とチャンネルにはもう設定されてるよ！")
                return

        # 保存
        reminder = {"time": time, "message": message, "channel_id": channel.id}
        reminders.append(reminder)
        save_reminders(guild_id, REMINDER_TYPE, reminders)

        # スケジュール登録
        schedule_daily_reminder(self.bot, guild_id, time, message, channel.id, registered_jobs, REMINDER_TYPE)

        await interaction.followup.send(f"まいにちおしらせするね！\n時間:{time}\n{channel.mention}\n{r['message']}")

    # --- /deletedaily 00:00 [チャンネル]
    @app_commands.command(name="deletedaily", description="特定のリマインダーを削除するよ")
    @app_commands.describe(time="時間（例: 09:00）", channel="送信先チャンネル")
    async def delete_daily(self, interaction: discord.Interaction, time: str, channel: discord.TextChannel = None):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        channel = channel or interaction.channel
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # 削除
        new_reminders = [r for r in reminders if not (r["time"] == time and r["channel_id"] == channel.id)]
        if len(reminders) == len(new_reminders):
            await interaction.followup.send("その設定は見つからなかったよ！")
            return

        save_reminders(guild_id, REMINDER_TYPE, new_reminders)
        cancel_daily_reminder(guild_id, time, channel.id, registered_jobs, REMINDER_TYPE)

        await interaction.followup.send(f"このmeowをけしたよ！\n時間:{time}\n{channel.mention}\n{r['message']}")

    # --- /showdaily
    @app_commands.command(name="showdaily", description="現在のリマインダーを一覧表示するよ")
    async def show_daily(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        if not reminders:
            await interaction.response.send_message("設定されてるリマインダーはないよ〜！")
            return

        lines = [f"‪‪❤︎‬ {r['time']} <#{r['channel_id']}> - {r['message']}" for r in reminders]
        await interaction.response.send_message("**いまのリマインダー設定**\n" + "\n".join(lines))

    # --- /cleardaily
    @app_commands.command(name="cleardaily", description="すべてのリマインダーを削除するよ")
    async def clear_daily(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        for r in reminders:
            cancel_daily_reminder(guild_id, r["time"], r["channel_id"], registered_jobs, REMINDER_TYPE)

        save_reminders(guild_id, REMINDER_TYPE, [])
        await interaction.response.send_message("すべて削除したよ〜！")
        
# --- Botにコマンド登録する setup 関数（クラスの外に！）
async def setup(bot: discord.Client):
    await bot.add_cog(DailyReminder(bot))