# commands/reminder/daily.py
# --- 毎日決まった時間にリマインダーを送るコマンドを管理するファイル
#     通常のテキストコマンド（!setdailyなど）で操作する！

import discord
from discord.ext import commands
from utils.scheduler import schedule_daily_reminder, cancel_daily_reminder
from utils.reminder_storage import load_reminders, save_reminders

REMINDER_TYPE = "daily"  # reminderタイプの識別子（保存フォルダなどで使う）
registered_jobs = {}     # スケジューラーに登録されているリマインダーを記録する辞書

# --- メインクラス（Cog）：Botにコマンドをまとめて登録できる仕組み
class DailyReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- !setdaily 09:00 [チャンネル] メッセージ
    # 時間・チャンネル・メッセージを指定して、毎日のリマインダーを登録！
    @commands.command(name="setdaily")
    async def set_daily(self, ctx, time: str, channel: discord.TextChannel = None, *, message: str):
        channel = channel or ctx.channel  # チャンネルが指定されてなければ、コマンドを打ったチャンネルを使う
        guild_id = ctx.guild.id

        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # 同じ時間・同じチャンネルにすでにあるか確認
        for r in reminders:
            if r["time"] == time and r["channel_id"] == channel.id:
                await ctx.send("その時間・チャンネルのリマインダーはすでに設定されてるよ！")
                return

        # リストに追加して保存
        reminder = {
            "time": time,
            "message": message,
            "channel_id": channel.id
        }
        reminders.append(reminder)
        save_reminders(guild_id, REMINDER_TYPE, reminders)

        # スケジューラーに登録
        schedule_daily_reminder(self.bot, guild_id, time, message, channel.id, registered_jobs, REMINDER_TYPE)

        await ctx.send(f"{time} に毎日リマインダー送るようにしたよ！")

    # --- !deletedaily 09:00 [チャンネル]
    # 指定した時間・チャンネルのリマインダーを削除！
    @commands.command(name="deletedaily")
    async def delete_daily(self, ctx, time: str, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        guild_id = ctx.guild.id

        reminders = load_reminders(guild_id, REMINDER_TYPE)
        new_reminders = [r for r in reminders if not (r["time"] == time and r["channel_id"] == channel.id)]

        # 削除対象が見つからなかった場合
        if len(reminders) == len(new_reminders):
            await ctx.send("その時間・チャンネルのリマインダーは見つからなかったよ…！")
            return

        # 保存を更新＋スケジューラーからも削除
        save_reminders(guild_id, REMINDER_TYPE, new_reminders)
        cancel_daily_reminder(guild_id, time, channel.id, registered_jobs, REMINDER_TYPE)

        await ctx.send(f"{time} のリマインダーを削除したよ！")

    # --- !showdaily
    # 現在のリマインダー設定を一覧表示
    @commands.command(name="showdaily")
    async def show_daily(self, ctx):
        guild_id = ctx.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        if not reminders:
            await ctx.send("いま設定されてる毎日リマインダーはないよ！")
            return

        # 表示用メッセージを作成
        lines = [f"{r['time']} - <#{r['channel_id']}> - {r['message']}" for r in reminders]
        await ctx.send("現在のリマインダー設定：\n" + "\n".join(lines))

    # --- !cleardaily
    # 全てのリマインダーを削除（保存とスケジューラーの両方）
    @commands.command(name="cleardaily")
    async def clear_daily(self, ctx):
        guild_id = ctx.guild.id
        reminders = load_reminders(guild_id, REMINDER_TYPE)

        # スケジューラーからキャンセル
        for r in reminders:
            cancel_daily_reminder(guild_id, r["time"], r["channel_id"], registered_jobs, REMINDER_TYPE)

        # 保存ファイルを空に
        save_reminders(guild_id, REMINDER_TYPE, [])
        await ctx.send("すべてのリマインダーを削除したよ〜")

# --- このファイルをBotに読み込ませるための setup 関数（__init__.py から呼ばれる）
def setup(bot):
        await bot.add_cog(DailyReminder(bot))