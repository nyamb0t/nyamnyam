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
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドをここで同期！
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

    # --- Discordにファイル内容を送る（コメントアウトでON/OFF） ---
    # await send_backup_to_discord()

# --- バックアップを送る関数 ---
async def send_backup_to_discord():
    #channel_id = 送信先チャンネルのIDをここに！  # 例: 944884833191084062
    channel = bot.get_channel(channel_id)
    if not channel:
        print("送信先チャンネルが見つからなかった！")
        return

    for filename in os.listdir("backup"):
        path = os.path.join("backup", filename)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Discordのメッセージとして送る（長すぎたら省略）
            if len(content) < 1900:
                await channel.send(f"**{filename} の中身：**\n```json\n{content}\n```")
            else:
                await channel.send(f"**{filename}** の内容が長すぎて全部は送れなかったよ！")

async def main():
    keep_alive()  # Flaskサーバー起動（Renderの死活監視用）
    await setup_commands(bot)  # コマンド登録
    setup_message_handler(bot)  # メッセージイベント登録
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())