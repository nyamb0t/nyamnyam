# commands/__init__.py
# --- Botの起動時にすべてのコマンドを登録するためのファイル！

from . import slash_channel  # 数字転送用のスラッシュコマンド
from . import slash_vc       # VC設定用のスラッシュコマンド
from . import slash_show     # 部屋番の設定確認
#from . import slash_debug

# Bot起動時に呼ばれるコマンド登録関数
async def setup_commands(bot):
    # スラッシュコマンドを登録
    await slash_channel.setup(bot)
    await slash_vc.setup(bot)
    await slash_show.setup(bot)
    #await slash_debug.setup(bot)