# commands/slash_show_number.py
# --- /shownumber：現在のVC・転送チャンネルの設定状況を表示するコマンド

import discord
from discord import app_commands
from utils.channel_storage import load_guild_data

@app_commands.command(name="shownumber", description="いまのVC・転送チャンネルの設定を確認するよ")
async def shownumber(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)

    # --- VCの表示（未設定ならその旨を表示）
    vc_channel = interaction.guild.get_channel(data.get("vc_channel")) if data.get("vc_channel") else None
    vc_display = f"‪‪　{vc_channel.name}" if vc_channel else "　まだ設定されてないよ！"

    # --- テキストチャンネルの表示（未設定ならその旨を表示）
    text_channels = data.get("text_channels", [])
    if text_channels:
        text_display = "\n".join([f"‪‪　<#{ch_id}>" for ch_id in text_channels])
    else:
        text_display = "　まだ設定されてないよ！"

    # --- メッセージを作成して送信
    message = (
        "**いまの設定**\n"
        "**【VC】**\n"
        f"{vc_display}\n"
        "**【転送チャンネル】**\n"
        f"{text_display}"
    )
    await interaction.response.send_message(message)