# commands/render/__init__.py
# --- render/daily.py のコマンドをBotに登録するためのファイル！

from .daily import setup as setup_reminder

async def setup_reminder_commands(bot):
    await bot.add_cog(daily.DailyReminder(bot))