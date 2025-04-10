# commands/slash_channel.py
# --- スラッシュコマンドで数字転送用チャンネルを設定・解除するコマンド定義ファイル！

import discord
from discord import app_commands
from utils.channel_storage import load_guild_data, save_guild_data

# --- チャンネル追加コマンド（/chset）
@app_commands.command(name="chset", description="5桁の数字を転送するチャンネルを追加するよ！")
@app_commands.describe(channel="転送先のチャンネル")
async def chset(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)

    if channel.id in data["text_channels"]:
        await interaction.response.send_message(f"{channel.mention} はもう追加済みだよ〜", ephemeral=True)
        return

    data["text_channels"].append(channel.id)
    save_guild_data(guild_id, data)

    await interaction.response.send_message(f"{channel.mention} に部屋番送るようにするね♩", ephemeral=True)

# --- チャンネル削除コマンド（/chdelete）
@app_commands.command(name="chdelete", description="数字の転送をやめたいチャンネルを解除するよ！")
@app_commands.describe(channel="解除したいチャンネル（指定しないと全部解除）")
async def chdelete(interaction: discord.Interaction, channel: discord.TextChannel = None):
    guild_id = interaction.guild.id
    data = load_guild_data(guild_id)

    if channel is None:
        # 引数なし → 全削除
        data["text_channels"] = []
        save_guild_data(guild_id, data)
        await interaction.response.send_message("全部のチャンネルへの送信やめるね❕", ephemeral=True)
        return

    if channel.id not in data["text_channels"]:
        await interaction.response.send_message("そのチャンネルは登録されてないかも！", ephemeral=True)
        return

    data["text_channels"].remove(channel.id)
    save_guild_data(guild_id, data)
    await interaction.response.send_message(f"{channel.mention} への送信を解除したよ❣️", ephemeral=True)

# --- Botにコマンド登録する setup 関数（__init__.py から呼び出す）
async def setup(bot: discord.Client):
    bot.tree.add_command(chset)
    bot.tree.add_command(chdelete)
    await bot.tree.sync()  # コマンドをDiscordに同期！