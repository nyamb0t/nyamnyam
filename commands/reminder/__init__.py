# commands/reminder/__init__.py
# --- リマインダー関連のコマンドをBotに登録するファイル！

from .daily import setup as setup_reminder
from .daily import reload_all_daily_reminders

# メインから呼ばれる setup_reminder 関数（Botにコマンドを登録する）
async def setup_reminder_commands(bot):
    await setup_reminder(bot)
    await reload_all_daily_reminders(bot)