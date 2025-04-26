import discord
from discord import app_commands
import os

# --- 特別コマンド：サーバーの設定ファイルの中身をDiscordに送信する
@app_commands.command(name="showdata", description="サーバー設定ファイルの中身を見せるよ")
async def showdata(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)  # このコマンドを送ったサーバーのIDを文字列で取得
    file_path = f"data/{guild_id}.json"   # そのサーバー用のJSONファイルのパス

    # --- ファイルが存在するかチェック
    if not os.path.exists(file_path):
        await interaction.response.send_message("設定ファイルが見つからなかったよ；＿；", ephemeral=True)
        return

    # --- ファイルを開いて中身を読む
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 内容をDiscordに送る（文字数が長すぎるとエラーになるので注意）
    if len(content) < 1900:
        await interaction.response.send_message(f"```json\n{content}\n```", ephemeral=True)
    else:
        await interaction.response.send_message("設定ファイルの中身が長すぎて送れなかった；＿；", ephemeral=True)

# --- setup関数（Botにコマンド登録するやつ）
async def setup(bot):
    bot.tree.add_command(showdata)