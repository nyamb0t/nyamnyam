# commands/__init__.py
# --- Botに読み込むコマンドをまとめて登録する場所！
#     各モジュールのsetup関数を呼び出して、Botに組み込んでいく。

# set_channelsモジュールから setup 関数をインポート
from .set_channels import setup as setup_set_channels

# reminderモジュール（毎日/一回きりのリマインダー）から setup_reminder をインポート
from .reminder import setup_reminder

# この関数が実際にBotに全コマンドを登録する役目を持つ
async def setup_commands(bot):
    # set_channelsのコマンドを登録
    setup_set_channels(bot)
    # リマインダー関連のコマンド（非同期で読み込む）
    await setup_reminder(bot)