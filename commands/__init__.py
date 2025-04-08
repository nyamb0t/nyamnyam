# commands/__init__.py
# --- Botにすべてのコマンドを登録するためのまとめ役！ここから各コマンドファイルを呼び出すよ！ ---

from .set_channels import setup as setup_set_channels
from .reminder import setup_reminder

async def setup_commands(bot):
    setup_set_channels(bot)
    await setup_reminder(bot)