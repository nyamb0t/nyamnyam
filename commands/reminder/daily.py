# commands/reminder/daily.py
# --- 毎日決まった時間にメッセージを送るリマインダーのコマンドを定義してるファイル！
#     スラッシュコマンドで登録される！

import discord
from discord import app_commands
from utils.scheduler import schedule_daily_reminder, cancel_daily_reminder
from utils.reminder_storage import load_reminders, save_reminders

REMINDER_TYPE = "daily"  # reminderの種類（フォルダ保存時に使う）
registered_jobs = {}  # 実行中のリマインダーを記録しておく辞書

# --- Botにコマンドを登録する関数（setup_reminder から呼ばれる）
async def setup(bot):
    bot.tree.add_command(setreminder)      # 毎日リマインダーの設定
    bot.tree.add_command(deletereminder)   # 個別削除
    bot.tree.add_command(showreminder)     # 現在のリスト表示
    bot.tree.add_command(clearreminder)    # 全削除

    # Bot起動時に、保存されたリマインダーを再スケジュール！
    for guild in bot.guilds:
        reminders = load_reminders(guild.id, REMINDER_TYPE)
        for rem in reminders:
            schedule_daily_reminder(
                bot,
                guild.id,
                rem["time"],
                rem["message"],
                rem["channel_id"],
                registered_jobs,
                REMINDER_TYPE
            )

# --- スラッシュコマンド定義部分 ---

@app_commands.command(
    name="setreminder",
    description="毎日特定の時間にリマインダーを設定します（JST）"
)
@app_commands.describe(time="時間（例：09:00）", channel="送信先チャンネル", message="送信するメッセージ")
async def setreminder(interaction: discord.Interaction, time: str, message: str, channel: discord.TextChannel = None):
    await interaction.response.defer()

    guild_id = interaction.guild.id
    channel = channel or interaction.channel
    reminders = load_reminders(guild_id, REMINDER_TYPE)

    # 同じ時間・チャンネルの重複チェック
    for r in reminders:
        if r["time"] == time and r["channel_id"] == channel.id:
            await interaction.followup.send("その時間・チャンネルのリマインダーはすでに設定されています。")
            return

    # 新しいリマインダー情報を追加
    reminder = {
        "time": time,
        "message": message,
        "channel_id": channel.id
    }
    reminders.append(reminder)
    save_reminders(guild_id, REMINDER_TYPE, reminders)

    # スケジューラーに追加
    schedule_daily_reminder(bot=interaction.client, guild_id=guild_id, time=time, message=message,
                            channel_id=channel.id, jobs=registered_jobs, reminder_type=REMINDER_TYPE)

    await interaction.followup.send(f"{time} に毎日リマインダーを送るよう設定しました！")

@app_commands.command(name="deletereminder", description="特定のリマインダーを削除します")
@app_commands.describe(time="時間（例：09:00）", channel="チャンネル")
async def deletereminder(interaction: discord.Interaction, time: str, channel: discord.TextChannel):
    await interaction.response.defer()

    guild_id = interaction.guild.id
    reminders = load_reminders(guild_id, REMINDER_TYPE)

    # 指定された時間・チャンネルのリマインダーを削除
    reminders = [r for r in reminders if not (r["time"] == time and r["channel_id"] == channel.id)]
    save_reminders(guild_id, REMINDER_TYPE, reminders)
    cancel_daily_reminder(guild_id, time, channel.id, registered_jobs, REMINDER_TYPE)

    await interaction.followup.send(f"{time} のリマインダーを削除しました。")

@app_commands.command(name="showreminder", description="設定されているリマインダーを表示します")
async def showreminder(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    reminders = load_reminders(guild_id, REMINDER_TYPE)

    if not reminders:
        await interaction.response.send_message("現在、設定されているリマインダーはありません。")
        return

    message = "\n".join([
        f"{r['time']} - <#{r['channel_id']}> - {r['message']}"
        for r in reminders
    ])
    await interaction.response.send_message(f"現在のリマインダー設定：\n{message}")

@app_commands.command(name="clearreminder", description="すべてのリマインダーを削除します")
async def clearreminder(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    reminders = load_reminders(guild_id, REMINDER_TYPE)

    for r in reminders:
        cancel_daily_reminder(guild_id, r["time"], r["channel_id"], registered_jobs, REMINDER_TYPE)

    save_reminders(guild_id, REMINDER_TYPE, [])
    await interaction.response.send_message("すべてのリマインダーを削除しました。")