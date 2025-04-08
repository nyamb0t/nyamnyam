# commands/set_channels.py
# --- チャンネルの設定、VC名の変更など、部屋番系のコマンドを管理するファイル！

import discord
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

# --- チャンネル追加コマンド（!setch #チャンネル）
@commands.command(name='setch')
async def set_channel(ctx, channel: discord.TextChannel):
    data = load_guild_data(ctx.guild.id)
    if channel.id not in data["text_channels"]:
        data["text_channels"].append(channel.id)
        save_guild_data(ctx.guild.id, data)
        await ctx.send(f"{channel.name} に部屋番送るようにするね♩")
    else:
        await ctx.send(f"{channel.name} はもう追加済みだよ〜")

# --- チャンネル削除コマンド（!deletech #チャンネル or !deletech）
@commands.command(name='deletech')
async def delete_channel(ctx, channel: discord.TextChannel = None):
    data = load_guild_data(ctx.guild.id)
    if channel is None:
        # 引数なしの場合、全てのチャンネル設定を解除
        data["text_channels"] = []
        save_guild_data(ctx.guild.id, data)
        await ctx.send("全部のチャンネルへの送信やめるね❕")
    elif channel.id in data["text_channels"]:
        data["text_channels"].remove(channel.id)
        save_guild_data(ctx.guild.id, data)
        await ctx.send(f"{channel.name} への送信を解除したよ❣️")
    else:
        await ctx.send("そのチャンネルは登録されてないかも！")

# --- VC設定コマンド（!setvc #ボイスチャンネル）
@commands.command(name='setvc')
async def set_vc(ctx, vc_channel: discord.VoiceChannel):
    data = load_guild_data(ctx.guild.id)
    data["vc_channel"] = vc_channel.id
    save_guild_data(ctx.guild.id, data)
    await ctx.send(f"{vc_channel.name}に部屋番反映させるね♩")

# --- VC解除コマンド（!deletevc）
@commands.command(name='deletevc')
async def delete_vc(ctx):
    data = load_guild_data(ctx.guild.id)
    data["vc_channel"] = None
    save_guild_data(ctx.guild.id, data)
    await ctx.send("VCの名前変えるのやめるね❕おつかれさま〜")

# --- Botにコマンドを登録するための関数（setup_commandsから呼び出される）
def setup(bot):
    bot.add_command(set_channel)
    bot.add_command(delete_channel)
    bot.add_command(set_vc)
    bot.add_command(delete_vc)