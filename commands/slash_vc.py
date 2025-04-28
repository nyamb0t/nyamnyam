import discord
from discord import app_commands
from utils.channel_storage import load_guild_data, save_guild_data
import re

# --- チャンネルリネーム設定コマンド（/rename_set）
# 指定したVCまたはテキストチャンネルを「リネーム対象」に登録する
@app_commands.command(name="rename_set", description="チャンネル名に部屋番を反映する")
@app_commands.describe(channel_input="名前をかえるチャンネル（ID･メンション･URL）")
async def rename_set(interaction: discord.Interaction, channel_input: str):
    guild = interaction.guild  # コマンドを実行したサーバー情報を取得

    # --- 入力から17桁以上の数字（チャンネルID）を取り出す
    matches = re.findall(r"\d{17,}", channel_input)
    if not matches:
        await interaction.response.send_message("チャンネルID読み取れなかったよ〜😿", ephemeral=True)
        return

    # --- 最後に見つかった数字をチャンネルIDとして使う
    channel_id = int(matches[-1])
    target_channel = guild.get_channel(channel_id)  # サーバー内からチャンネルを取得

    # --- VCかテキストチャンネルじゃなかったらエラー
    if not isinstance(target_channel, (discord.VoiceChannel, discord.TextChannel)):
        await interaction.response.send_message("VC or テキストチャンネルを指定してね😭", ephemeral=True)
        return

    # --- 現在の登録データを読み込む
    data = load_guild_data(guild.id)
    rename_channels = data.get("rename_channels", [])

    # --- すでに登録されていたらスキップ
    if target_channel.id in rename_channels:
        await interaction.response.send_message(f"{target_channel.name} はもう登録されてるよ〜", ephemeral=True)
        return

    # --- 新しくリストに追加して保存
    rename_channels.append(target_channel.id)
    data["rename_channels"] = rename_channels
    save_guild_data(guild.id, data)

    await interaction.response.send_message(f"{target_channel.name} をリネーム対象に追加したよ♩", ephemeral=True)

# --- リネーム設定からチャンネルを削除するコマンド（/rename_delete）
# チャンネルを指定しない → 全部削除
# チャンネルを指定する → そのチャンネルだけ削除
@app_commands.command(name="rename_delete", description="チャンネルの名前を変える設定を削除する")
@app_commands.describe(channel_input="削除するチャンネル（指定しなければ全部きえる！）")
async def rename_delete(interaction: discord.Interaction, channel_input: str = None):
    guild = interaction.guild
    data = load_guild_data(guild.id)
    rename_channels = data.get("rename_channels", [])

    # --- チャンネル指定がない場合（Noneだったら）
    if channel_input is None:
        data["rename_channels"] = []  # リストを空にする
        save_guild_data(guild.id, data)
        await interaction.response.send_message("リネーム対象のチャンネルを全部削除したよ！", ephemeral=True)
        return

    # --- チャンネル指定がある場合
    matches = re.findall(r"\d{17,}", channel_input)
    if not matches:
        await interaction.response.send_message("チャンネルID読み取れなかった😿", ephemeral=True)
        return

    channel_id = int(matches[-1])

    # --- 指定されたチャンネルがリストにない場合
    if channel_id not in rename_channels:
        await interaction.response.send_message("そのチャンネルは登録されてないよ〜", ephemeral=True)
        return

    # --- 指定されたチャンネルをリストから削除
    rename_channels.remove(channel_id)
    data["rename_channels"] = rename_channels
    save_guild_data(guild.id, data)

    await interaction.response.send_message("チャンネルをリネーム対象から削除したよ！", ephemeral=True)

# --- Botにコマンド登録する setup 関数（__init__.py から呼び出される想定）
async def setup(bot: discord.Client):
    bot.tree.add_command(rename_set)     # /rename_set コマンドを登録
    bot.tree.add_command(rename_delete)  # /rename_delete コマンドを登録