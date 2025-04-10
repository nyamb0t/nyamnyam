# commands/slash/set_channels.py
# --- スラッシュコマンドで部屋番送信チャンネルやVC名変更用のVCを設定・解除するファイル！

import discord
from discord import app_commands
import os
import json
import re

# --- ギルドごとの設定ファイルを保存するフォルダ
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- ギルドごとのJSONファイルのパスを返す関数
def get_guild_file(guild_id: int) -> str:
    return os.path.join(DATA_DIR, f"{guild_id}_channels.json")

# --- 設定ファイルの読み込み
def load_guild_data(guild_id: int):
    path = get_guild_file(guild_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"text_channels": [], "vc_channel": None, "last_sent": {}}

# --- 設定ファイルの保存
def save_guild_data(guild_id: int, data):
    path = get_guild_file(guild_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- スラッシュコマンドをまとめるクラス（Cog）
class ChannelManager(app_commands.Group):

    def __init__(self):
        super().__init__(name="channel", description="部屋番転送チャンネルやVCの設定を管理")

    @app_commands.command(name="set", description="部屋番を転送するテキストチャンネルを追加するよ！")
    async def setch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """部屋番転送先のテキストチャンネルを追加"""
        data = load_guild_data(interaction.guild.id)
        if channel.id not in data["text_channels"]:
            data["text_channels"].append(channel.id)
            save_guild_data(interaction.guild.id, data)
            await interaction.response.send_message(f"{channel.mention} に部屋番送るようにしたよ♩")
        else:
            await interaction.response.send_message(f"{channel.mention} はもう追加済みだよ〜")

    @app_commands.command(name="delete", description="部屋番の転送チャンネルを削除するよ！")
    async def deletech(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """テキストチャンネルの設定削除、または全削除"""
        data = load_guild_data(interaction.guild.id)
        if channel is None:
            data["text_channels"] = []
            save_guild_data(interaction.guild.id, data)
            await interaction.response.send_message("全部のチャンネルへの送信をやめたよ❕")
        elif channel.id in data["text_channels"]:
            data["text_channels"].remove(channel.id)
            save_guild_data(interaction.guild.id, data)
            await interaction.response.send_message(f"{channel.mention} への送信を解除したよ❣️")
        else:
            await interaction.response.send_message("そのチャンネルは登録されてないみたい！")

    @app_commands.command(name="setvc", description="部屋番を反映するVCを設定するよ！")
    async def setvc(self, interaction: discord.Interaction, vc_input: str):
        """VCのメンション・ID・URLから対象VCを設定"""
        match = re.search(r'\d{17,}', vc_input)
        if not match:
            await interaction.response.send_message("チャンネルのIDが読み取れなかったよ〜！")
            return

        vc_id = int(match.group())
        vc_channel = interaction.guild.get_channel(vc_id)

        if not isinstance(vc_channel, discord.VoiceChannel):
            await interaction.response.send_message("指定されたチャンネルはVCじゃないかも！")
            return

        data = load_guild_data(interaction.guild.id)
        if data.get("vc_channel") == vc_channel.id:
            await interaction.response.send_message(f"{vc_channel.name} はもう設定済みだよ〜")
            return

        data["vc_channel"] = vc_channel.id
        save_guild_data(interaction.guild.id, data)
        await interaction.response.send_message(f"{vc_channel.name} に部屋番反映させるようにしたよ♩")

    @app_commands.command(name="deletevc", description="VCの部屋番反映をやめるよ！")
    async def deletevc(self, interaction: discord.Interaction):
        """VCへの部屋番反映を解除"""
        data = load_guild_data(interaction.guild.id)
        data["vc_channel"] = None
        save_guild_data(interaction.guild.id, data)
        await interaction.response.send_message("VCの名前を変更するのやめたよ〜！")

# --- このクラスをBotに登録する関数（setup_commandsから呼ばれる）
async def setup(bot: discord.Client):
    bot.tree.add_command(ChannelManager())