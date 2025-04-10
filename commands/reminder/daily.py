# commands/render/daily.py
# --- 毎日決まった時間にリマインダーを送るコマンド定義ファイル！

import discord
from discord.ext import commands
from discord import app_commands
from utils.scheduler import schedule_daily_reminder, cancel_daily_reminder
from utils.reminder_storage import load_reminders, save_reminders

REMINDER_TYPE = "daily"
registered_jobs = {}

class ConfirmAddButton(discord.ui.View): # y/nボタンの定義？
    def __init__(self, bot, interaction, time, message, channel):
        super().__init__(timeout=60)
        self.bot = bot
        self.interaction = interaction
        self.time = time
        self.message = message
        self.channel = channel
        self.value = None

    @discord.ui.button(label="追加する", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.send_message("追加しました👌🏻", ephemeral=True)
        self.stop()

    @discord.ui.button(label="やめとく", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.send_message("キャンセルしたよ✌🏻", ephemeral=True)
        self.stop()

class DailyReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- /setdaily 00:00 [チャンネル] メッセージ
    @app_commands.command(name="setdaily", description="毎日決まった時間におしらせする")
    @app_commands.describe(time="時間（例: 10:27）", channel="おくるチャンネル", message="おくるメッセージ")
    async def set_daily(self, interaction: discord.Interaction, time: str, message: str, channel: discord.TextChannel = None):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        channel = channel or interaction.channel
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # --- 重複チェックしてボタンで確認させる
        for r in reminders:
            if r["time"] == time and r["channel_id"] == channel.id:
                view = ConfirmAddButton(self.bot, interaction, time, message, channel)
                await interaction.response.send_message(
                    f"同じ時間とチャンネルに先客がいます😭\n"
                    f"‪‪   {time} {channel.mention} ‪‪❤︎‬ {r['message']}"
                    "追加で登録する？",
                    view=view,
                    ephemeral=True
                )
                await view.wait()
                
                if view.value is None or view.value is False:
                    return  # キャンセル or 無操作
                    
                break  # 追加で登録へ続行

        # 保存
        reminder = {"time": time, "message": message, "channel_id": channel.id}
        reminders.append(reminder)
        save_reminders(guild_id, REMINDER_TYPE, reminders)

        # スケジュール登録
        schedule_daily_reminder(self.bot, guild_id, time, message, channel.id, registered_jobs, REMINDER_TYPE)
        
        # --- 同じ時間の別チャンネルのリマインダーがあるかチェック
        duplicates = [r for r in reminders if r["time"] == time and r["channel_id"] != channel.id]
        if duplicates:
            warning_lines = [
                f"‪‪❤︎‬ {r['time']} <#{r['channel_id']}> - {r['message']}"
                for r in duplicates
            ]
            warning = "\n\n同じ時間のmeowがあるよт  ̫ т重複してないかみて〜\n" + "\n".join(warning_lines)
        else:
            warning = ""
        
        # --- 設定完了のメッセージと一緒に送信
        await interaction.followup.send(
            f"まいにちおしらせするね🐾\n"
            f"   {time} {channel.mention} ❤︎‬ {message}"
            + warning
        )

    # --- /deletedaily 00:00 [チャンネル]
    @app_commands.command(name="deletedaily", description="毎日のおしらせをやめる")
    @app_commands.describe(time="時間（例: 10:27）", channel="設定してたチャンネル")
    async def delete_daily(self, interaction: discord.Interaction, time: str, channel: discord.TextChannel = None):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        channel = channel or interaction.channel
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # 削除対象を見つけて保持しておく
        target = next((r for r in reminders if r["time"] == time and r["channel_id"] == channel.id), None)
        
        if not target:
            await interaction.followup.send("時間かチャンネルまちがえてないかな。。？")
            return
        
        # 削除処理
        new_reminders = [r for r in reminders if r != target]
        save_reminders(guild_id, REMINDER_TYPE, new_reminders)
        cancel_daily_reminder(guild_id, time, channel.id, registered_jobs, REMINDER_TYPE)
        
        await interaction.followup.send(
            f"このmeowをけしたよ！\n   {time} {channel.mention} ‪‪❤︎‬ {target['message']}"
        )

    # --- /showdaily
    @app_commands.command(name="showdaily", description="毎日のおしらせ予定が一覧でみれる")
    async def show_daily(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        if not reminders:
            await interaction.response.send_message("おしらせの予定は0️⃣です！")
            return

        lines = [f"‪‪❤︎‬ {r['time']} <#{r['channel_id']}> - {r['message']}" for r in reminders]
        await interaction.response.send_message("**꒰ིྀ mnow list ꒱ིྀ**" + "\n".join(lines))

    # --- /cleardaily
    @app_commands.command(name="cleardaily", description="毎日のおしらせを全部なくす")
    async def clear_daily(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        for r in reminders:
            cancel_daily_reminder(guild_id, r["time"], r["channel_id"], registered_jobs, REMINDER_TYPE)

        save_reminders(guild_id, REMINDER_TYPE, [])
        await interaction.response.send_message("ぼうけん の しょ が きえました ！")
        
# --- Botにコマンド登録する setup 関数（クラスの外に！）
async def setup(bot: discord.Client):
    await bot.add_cog(DailyReminder(bot))
    await reload_all_daily_reminders(bot)
    
# --- Bot起動時にすべてのリマインダーを再登録する
async def reload_all_daily_reminders(bot):
    from utils.reminder_storage import load_reminders
    from utils.scheduler import schedule_daily_reminder
    import os

    base_folder = "data/reminders"
    if not os.path.exists(base_folder):
        return

    for guild_folder in os.listdir(base_folder):
        if not guild_folder.isdigit():
            continue  # フォルダ名が数字じゃない（.gitkeepなど）はスキップ！

        guild_id = int(guild_folder)
        path = os.path.join(base_folder, guild_folder, "daily.json")
        if not os.path.exists(path):
            continue

        from utils.reminder_storage import load_reminders
        reminders = load_reminders(guild_id, "daily")
        for r in reminders:
            schedule_daily_reminder(
                bot,
                guild_id,
                r["time"],
                r["message"],
                r["channel_id"],
                registered_jobs,
                REMINDER_TYPE
            )