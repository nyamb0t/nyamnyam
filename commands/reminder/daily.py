# --- daily.py：毎日決まった時間にリマインダーを送るコマンド定義ファイル！

import discord
from discord.ext import commands
from discord import app_commands
from utils.scheduler import schedule_daily_reminder, cancel_daily_reminder
from utils.reminder_storage import load_reminders, save_reminders

REMINDER_TYPE = "daily"
registered_jobs = {}

# --- ボタンのUI定義
class ConfirmAddButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @discord.ui.button(label="ʏᴇꜱ", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.send_message("追加しました👌🏻", ephemeral=True)
        self.stop()

    @discord.ui.button(label="ɴᴏ", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.send_message("キャンセルしたよ✌🏻", ephemeral=True)
        self.stop()

class DailyReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily_set", description="毎日決まった時間におしらせする")
    @app_commands.describe(time="時間（例: 10:27）", channel="おくるチャンネル", message="おくるメッセージ")
    async def daily_set(self, interaction: discord.Interaction, time: str, message: str, channel: discord.TextChannel = None):
        guild_id = interaction.guild.id
        channel = channel or interaction.channel
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # --- 重複チェックしてボタンで確認させる
        for r in reminders:
            if r["time"] == time and r["channel_id"] == channel.id:
                # 新しく追加しようとしてるリマインダーも仮に作る
                new_reminder = {"time": time, "message": message, "channel_id": channel.id}
                
                # 既存リマインダーと新規リマインダーをまとめて表示する
                warning_message = (
                　　　f"同じ時間とチャンネルに先客がいます🐱\n"
                　　　f"\n**《現在登録されているもの》**\n"
                　　　f"　{time} {channel.mention} ···▸﻿ {r['message']}\n"
                　　　f"\n**《今回追加しようとしているもの》**\n"
                　　　f"　{time} {channel.mention} ···▸﻿ {new_reminder['message']}\n"
                　　　f"\n追加する？"
                )
                
                view = ConfirmAddButton()
                await interaction.response.send_message(warning_message, view=view, ephemeral=True)
                timeout = await view.wait()
                
                if view.value is None or view.value is False or timeout:
                    return
                break
            
        else:
            # 重複していない場合のみ defer する
            await interaction.response.defer()

        # --- 保存処理
        reminder = {"time": time, "message": message, "channel_id": channel.id}
        reminders.append(reminder)
        save_reminders(guild_id, REMINDER_TYPE, reminders)

        # --- スケジューリング
        schedule_daily_reminder(self.bot, guild_id, time, message, channel.id, registered_jobs, REMINDER_TYPE)

        # --- 同じ時間の他チャンネルへの通知チェック
        duplicates = [r for r in reminders if r["time"] == time and r["channel_id"] != channel.id]
        if duplicates:
            warning_lines = [
                f"‪‪   {r['time']} <#{r['channel_id']}> ···▸﻿ {r['message']}" for r in duplicates
            ]
            warning = "\n\n!! 同じ時間のmeowがあるよ₍˄. ̫.˄ ₎੭\n" + "\n".join(warning_lines)
        else:
            warning = ""

        await interaction.followup.send(
            f"まいにちおしらせするね🐾\n"
            f"   {time} {channel.mention} ···▸﻿ {message}"
            + warning
        )

# --- DailyReminder クラスの中
    @app_commands.command(name="daily_delete", description="毎日のおしらせをやめる")
    @app_commands.describe(time="時間（例: 10:27）")
    async def daily_delete(self, interaction: discord.Interaction, time: str):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        targets = [r for r in reminders if r["time"] == time]
        if not targets:
            await interaction.followup.send("その時間のᴍᴇᴏᴡはみつからなかったよ〜^ㅜ.ㅜ^")
            return

        class ReminderDeleteView(discord.ui.View):
            def __init__(self, reminders_list):
                super().__init__(timeout=60)
                self.reminders_list = reminders_list

                for idx, reminder in enumerate(reminders_list):
                    label = f"{reminder['message']}>"
                    self.add_item(self.ReminderButton(label, idx))

            class ReminderButton(discord.ui.Button):
                def __init__(self, label, index):
                    super().__init__(label=label, style=discord.ButtonStyle.danger)
                    self.index = index

                async def callback(self, interaction: discord.Interaction):
                    reminder = self.view.reminders_list[self.index]
                    updated = [r for r in load_reminders(guild_id, REMINDER_TYPE) if r != reminder]
                    save_reminders(guild_id, REMINDER_TYPE, updated)
                    cancel_daily_reminder(guild_id, reminder["time"], reminder["channel_id"], registered_jobs, REMINDER_TYPE)
                    await interaction.response.send_message(
                        f"このᴍᴇᴏᴡをけしたよ！\n   {reminder['time']} <#{reminder['channel_id']}> ···▸﻿ {reminder['message']}",
                        ephemeral=True
                    )
                    self.view.stop()

        view = ReminderDeleteView(targets)
        lines = [f"{r['time']} <#{r['channel_id']}> ···▸﻿ {r['message']}" for r in targets]
        await interaction.followup.send(
            "**削除したいmeowを選んでね！**\n" + "\n".join(lines),
            view=view
        )

    @app_commands.command(name="show_daily", description="毎日のおしらせ予定が一覧でみれる")
    async def show_daily(self, interaction: discord.Interaction):
        reminders = load_reminders(interaction.guild.id, REMINDER_TYPE)
        if not reminders:
            await interaction.response.send_message("꒰ིྀ  ᴍᴇᴏᴡ ʟɪꜱᴛ  ꒱ ིྀ\n    おしらせ予定はありません🐾")
            return

        lines = [f"‪‪    {r['time']} <#{r['channel_id']}> ···▸﻿ {r['message']}" for r in reminders]
        await interaction.response.send_message("꒰ིྀ  ᴍᴇᴏᴡ ʟɪꜱᴛ  ꒱ ིྀ\n" + "\n".join(lines))

    @app_commands.command(name="daily_clear", description="毎日のおしらせを全部なくす")
    async def daily_clear(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        for r in reminders:
            cancel_daily_reminder(guild_id, r["time"], r["channel_id"], registered_jobs, REMINDER_TYPE)

        save_reminders(guild_id, REMINDER_TYPE, [])
        await interaction.response.send_message("ぼうけん の しょ が きえました ！")

# --- コマンド登録と再スケジュール処理
async def setup(bot: discord.Client):
    await bot.add_cog(DailyReminder(bot))
    await reload_all_daily_reminders(bot)

async def reload_all_daily_reminders(bot):
    from utils.reminder_storage import load_reminders
    from utils.scheduler import schedule_daily_reminder
    import os

    base_folder = "data/reminders"
    if not os.path.exists(base_folder):
        return

    for guild_folder in os.listdir(base_folder):
        if not guild_folder.isdigit():
            continue

        guild_id = int(guild_folder)
        path = os.path.join(base_folder, guild_folder, "daily.json")
        if not os.path.exists(path):
            continue

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