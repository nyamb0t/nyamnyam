import discord
from discord import app_commands
from utils.channel_storage import load_guild_data

# --- スラッシュコマンドで現在の数字転送/リネーム設定を確認するコマンド！
@app_commands.command(name="shownumber", description="数字を送るチャンネルとリネームチャンネルが見れるよ")
async def shownumber(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)

    # --- 数字転送チャンネルの設定確認
    text_channel_ids = data.get("text_channels", [])
    if text_channel_ids:
        text_info = "\n".join([f"　⋆ <#{ch_id}>" for ch_id in text_channel_ids])
    else:
        text_info = "　ɴᴏᴛ ꜰᴏᴜɴᴅ..."

    # --- リネーム対象チャンネルの設定確認
    rename_channel_ids = data.get("rename_channels", [])
    if rename_channel_ids:
        rename_info = "\n".join([f"　⋆ <#{ch_id}>" for ch_id in rename_channel_ids])
    else:
        rename_info = "　ɴᴏᴛ ꜰᴏᴜɴᴅ..."

    # --- メッセージをまとめる
    message = (
        f"**⋆⸜ ꜱᴛᴀᴛᴜꜱ ⸝⋆**\n\n"
        f"**・数字を送るチャンネル**\n{text_info}\n\n"
        f"**・チャンネル名を変えるチャンネル**\n{rename_info}"
    )

    await interaction.response.send_message(message)

# --- setup 関数（__init__.py から呼び出される想定）
async def setup(bot: discord.Client):
    bot.tree.add_command(shownumber)