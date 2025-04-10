# commands/__init__.py
# --- Botの起動時にすべてのコマンドを登録するためのファイル！

from . import slash_channel  # 数字転送用のスラッシュコマンド
from . import slash_vc       # VC設定用のスラッシュコマンド
from .reminder import setup_reminder  # リマインダー関係のコマンド登録（このあと対応）

# Bot起動時に呼ばれるコマンド登録関数
async def setup_commands(bot):
    # スラッシュコマンドを登録
    await slash_channel.setup(bot)
    await slash_vc.setup(bot)

    # リマインダー関係（/setdaily など）の登録
    await setup_reminder(bot)