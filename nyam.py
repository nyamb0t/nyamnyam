# nyam.py
# --- nyambotの起動スクリプト！Renderではこれが実行されるよ！ ---

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive
from commands import setup_commands
from events.message_handler import setup as setup_message_handler
from commands.reminder import setup_reminder_commands 
from utils.scheduler import start_scheduler
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Botのクラスを拡張して、setup_hookでスラッシュコマンドを同期する！
class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()  # Bot起動時にスラッシュコマンドを同期！

# --- Botのインスタンスを作成（prefixは無視されるけど一応"!"にしておく）
intents = discord.Intents.all()
bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドの同期はここで！
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

    # バックアップログの送信（必要に応じてコメントアウトでON/OFF）
    await send_backup_to_discord()

# --- バックアップログを送る関数（バックアップ内容をDiscordに送る）
async def send_backup_to_discord():
    channel_id = 1359758903998415060  # 送信先チャンネルのID
    channel = bot.get_channel(channel_id)
    if not channel:
        print("送信先チャンネルが見つからなかった！")
        return

    for filename in os.listdir("backup"):
        path = os.path.join("backup", filename)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content) < 1900:
                await channel.send(f"**{filename} の中身：**\n```json\n{content}\n```")
            else:
                await channel.send(f"**{filename}** の内容が長すぎて全部は送れなかったよ！")

# --- メイン関数でBotを起動！
async def main():
    keep_alive()
    start_scheduler()
    await setup_commands(bot)         # スラッシュコマンドの登録
    await setup_message_handler(bot)  # 数字転送・VC名変更のイベント登録
    await setup_reminder_commands(bot)  # リマインダー機能
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())