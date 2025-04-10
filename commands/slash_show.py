# --- スラッシュコマンドで現在のVC/チャンネル設定状況を確認するコマンド！

import discord
from discord import app_commands
from utils.channel_storage import load_guild_data

@app_commands.command(name="shownumber", description="部屋番をおくるチャンネルとvcがみれる🔥")
async def shownumber(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)

    # VCの設定確認
    vc_channel_id = data.get("vc_channel")
    vc_channel = interaction.guild.get_channel(vc_channel_id) if vc_channel_id else None
    vc_info = f"　‪‪⋆  <#{vc_channel.id}>" if vc_channel else "　ɴᴏᴛ ꜰᴏᴜɴᴅ..."

    # テキストチャンネルの設定確認
    text_channel_ids = data.get("text_channels", [])
    if text_channel_ids:
        text_info = "\n".join([f"‪‪　︎⋆  <#{ch_id}>" for ch_id in text_channel_ids])
    else:
        text_info = "　ɴᴏᴛ ꜰᴏᴜɴᴅ..."

    message = (
        f"** ⋆⸜ ꜱᴛᴀᴛᴜꜱ ⸝⋆ **\n"
        f" ᴠᴏɪᴄᴇ ᴄʜᴀᴛ\n{vc_info}\n"
        f" ʀᴏᴏᴍ ɴᴜᴍʙᴇʀ\n{text_info}"
    )
    await interaction.response.send_message(message)

# --- setup 関数（__init__.py から呼ばれる）
async def setup(bot: discord.Client):
    bot.tree.add_command(shownumber)