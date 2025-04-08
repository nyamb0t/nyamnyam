# commands/reminder/__init__.py
# --- 毎日リマインダー・一度きりリマインダーのコマンドをまとめてBotに登録する場所！
#     ここでそれぞれの setup を呼び出して準備するよ！

from . import daily  # 毎日リマインダーの処理が入ってる
from . import one_time  # 一回きりのリマインダー処理

# この関数は setup_commands(bot) の中から呼ばれて、リマインダー関係をすべてBotに登録する！
async def setup_reminder(bot):
    await daily.setup(bot)       # 毎日リマインダーのコマンドを登録
    await one_time.setup(bot)    # 一度きりリマインダーのコマンドを登録