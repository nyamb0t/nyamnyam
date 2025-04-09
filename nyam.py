# nyam.py
# --- nyambotの起動スクリプト！Renderではこれが実行されるよ！ ---

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Render用Flaskサーバー
from commands import setup_commands
from events.message_handler import setup_message_handler
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Botに必要なintentsを設定 ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドをここで同期！
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

async def main():
    keep_alive()  # Flaskサーバー起動（Renderの死活監視用）
    await setup_commands(bot)  # コマンド登録
    setup_message_handler(bot)  # メッセージイベント登録
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())