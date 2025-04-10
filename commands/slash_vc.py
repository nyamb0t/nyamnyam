# commands/slash_vc.py
# --- スラッシュコマンドでVCの名前変更用チャンネルを設定・解除するコマンド定義ファイル！

import discord
from discord import app_commands
from utils.channel_storage import load_guild_data, save_guild_data
import re

# --- VC設定コマンド（/vcset）
@app_commands.command(name="vcset", description="VC名に部屋番を反映できる")
@app_commands.describe(vc_input="名前をかえるVC（ID･メンション･URL）")
async def vcset(interaction: discord.Interaction, vc_input: str):
    guild = interaction.guild

    # --- すべての17桁以上の数字を抽出して、2番目（チャンネルID）を使う！
    matches = re.findall(r"\d{17,}", vc_input)
    if not matches:
        await interaction.response.send_message("チャンネルID読み取れなかった😿", ephemeral=True)
        return

    # ギルドID/チャンネルID の形式なら、2つめがチャンネルID
    vc_id = int(matches[-1])
    vc_channel = guild.get_channel(vc_id)

    if not isinstance(vc_channel, discord.VoiceChannel):
        await interaction.response.send_message("それVCじゃないかも", ephemeral=True)
        return

    data = load_guild_data(guild.id)
    if data.get("vc_channel") == vc_channel.id:
        await interaction.response.send_message(f"{vc_channel.name} はもう追加済みだよ〜", ephemeral=True)
        return

    data["vc_channel"] = vc_channel.id
    save_guild_data(guild.id, data)
    await interaction.response.send_message(f"{vc_channel.name} に部屋番反映させるね♩", ephemeral=True)

# --- VC解除コマンド（/vcdelete）
@app_commands.command(name="vcdelete", description="VCの名前変更設定を解除するよ")
async def vcdelete(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)
    data["vc_channel"] = None
    save_guild_data(guild_id, data)
    await interaction.response.send_message("VCの名前変えるのやめるね❕おつかれさま〜", ephemeral=True)

# --- Botにコマンド登録する setup 関数（__init__.py から呼び出す）
async def setup(bot: discord.Client):
    bot.tree.add_command(vcset)
    bot.tree.add_command(vcdelete)
    # await bot.tree.sync()  # Discord にコマンドを同期