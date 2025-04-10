# commands/set_channels.py
# --- スラッシュコマンド版：チャンネルの設定、VC名の変更など、部屋番系のコマンドを管理するファイル！

import discord
from discord import app_commands
from discord.ext import commands
import os
import json

# --- 設定ファイルを保存するフォルダ
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # フォルダがなければ作る

# --- ギルド（サーバー）ごとの保存ファイルパスを返す関数
def get_guild_file(guild_id):
    return os.path.join(DATA_DIR, f"{guild_id}_channels.json")

# --- ギルドの設定ファイルを読み込む関数
def load_guild_data(guild_id):
    path = get_guild_file(guild_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # ファイルがなければ初期データを返す
    return {"text_channels": [], "vc_channel": None, "last_sent": {}}

# --- ギルドの設定データを保存する関数
def save_guild_data(guild_id, data):
    path = get_guild_file(guild_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- スラッシュコマンドの管理クラス（Cog）
class ChannelSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- /setch チャンネル
    @app_commands.command(name="setch", description="部屋番を送るチャンネルを設定します")
    @app_commands.describe(channel="送信先チャンネル")
    async def setch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        data = load_guild_data(guild_id)

        if channel.id not in data["text_channels"]:
            data["text_channels"].append(channel.id)
            save_guild_data(guild_id, data)
            await interaction.response.send_message(f"{channel.name} に部屋番送るようにするね♩")
        else:
            await interaction.response.send_message(f"{channel.name} はもう追加済みだよ〜")

    # --- /deletech チャンネル（省略可）
    @app_commands.command(name="deletech", description="部屋番送信チャンネルを解除します")
    @app_commands.describe(channel="解除するチャンネル（未指定で全解除）")
    async def deletech(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        guild_id = interaction.guild.id
        data = load_guild_data(guild_id)

        if channel is None:
            data["text_channels"] = []
            save_guild_data(guild_id, data)
            await interaction.response.send_message("全部のチャンネルへの送信やめるね❕")
        elif channel.id in data["text_channels"]:
            data["text_channels"].remove(channel.id)
            save_guild_data(guild_id, data)
            await interaction.response.send_message(f"{channel.name} への送信を解除したよ❣️")
        else:
            await interaction.response.send_message("そのチャンネルは登録されてないかも！")

    # --- /setvc VCチャンネル
    @app_commands.command(name="setvc", description="部屋番を反映するVCを設定します")
    @app_commands.describe(vc_channel="部屋番をつけるVCチャンネル")
    async def setvc(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        guild_id = interaction.guild.id
        data = load_guild_data(guild_id)

        if data.get("vc_channel") == vc_channel.id:
            await interaction.response.send_message(f"{vc_channel.name} はもう追加済みだよ〜")
            return

        data["vc_channel"] = vc_channel.id
        save_guild_data(guild_id, data)
        await interaction.response.send_message(f"{vc_channel.name} に部屋番反映させるね♩")

    # --- /deletevc
    @app_commands.command(name="deletevc", description="部屋番のVC反映を解除します")
    async def deletevc(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = load_guild_data(guild_id)

        data["vc_channel"] = None
        save_guild_data(guild_id, data)
        await interaction.response.send_message("VCの名前変えるのやめるね❕おつかれさま〜")

# --- BotにこのCogを登録する setup 関数（commands/__init__.py から呼び出される）
async def setup(bot):
    await bot.add_cog(ChannelSettings(bot))