import discord
from discord import app_commands
import os

@app_commands.command(name="showdata", description="サーバー設定ファイルの中身を見せるよ")
async def showdata(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    file_path = f"data/{guild_id}_channels.json"  # ←ここ修正！！！

    if not os.path.exists(file_path):
        await interaction.response.send_message("設定ファイルが見つからなかったよ；＿；", ephemeral=True)
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) < 1900:
        await interaction.response.send_message(f"```json\n{content}\n```", ephemeral=True)
    else:
        await interaction.response.send_message("設定ファイルの中身が長すぎて送れなかった；＿；", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(showdata)