import discord
from discord import app_commands
from utils.channel_storage import load_guild_data, save_guild_data
import re

# --- チャンネルリネーム設定コマンド（/renameset）
# チャンネルID・メンション・URLを受け取って、リネーム対象として登録する
@app_commands.command(name="renameset", description="チャンネル名に部屋番を反映できる")
@app_commands.describe(channel_input="名前をかえるチャンネル（ID･メンション･URL）")
async def renameset(interaction: discord.Interaction, channel_input: str):
    guild = interaction.guild  # コマンドを送ったサーバー情報を取得

    # --- 入力された文字列から、17桁以上の数字（DiscordのID）を探す
    matches = re.findall(r"\d{17,}", channel_input)
    if not matches:
        await interaction.response.send_message("チャンネルID読み取れなかった😿", ephemeral=True)
        return

    # --- 最後に見つかった数字をチャンネルIDとして使う
    channel_id = int(matches[-1])
    target_channel = guild.get_channel(channel_id)  # サーバー内からそのIDのチャンネルを探す

    # --- チャンネルの型チェック（ボイスチャンネル or テキストチャンネルのみOK）
    if not isinstance(target_channel, (discord.VoiceChannel, discord.TextChannel)):
        await interaction.response.send_message("それVCでもテキストチャンネルでもないかも", ephemeral=True)
        return
        
    data = load_guild_data(guild.id)
    rename_channels = data.get("rename_channels", [])  # ← "rename_channels"キーのリストを取る（なければ空リスト）
    
    if target_channel.id in rename_channels:
        await interaction.response.send_message(f"{target_channel.name} はもう登録されてるよ〜", ephemeral=True)
        return
    
    rename_channels.append(target_channel.id)  # リストに追加！
    
    data["rename_channels"] = rename_channels  # データに上書き保存
    save_guild_data(guild.id, data)  # 保存！
    
    await interaction.response.send_message(f"{target_channel.name} をリネーム対象に追加したよ♩", ephemeral=True)

# --- リネーム設定解除コマンド（/renamedelete）
# 登録したチャンネル設定を解除する
@app_commands.command(name="renamedelete", description="チャンネル名変更設定を解除するよ")
async def renamedelete(interaction: discord.Interaction):
    guild_id = interaction.guild.id  # サーバーIDを取得
    data = load_guild_data(guild_id)  # サーバーの設定ファイルを読み込む

    # --- リネーム設定を消す（Noneにする）
    data["rename_channel"] = None
    save_guild_data(guild_id, data)

    # --- 完了メッセージを送信
    await interaction.response.send_message("チャンネル名変えるのやめるね❕おつかれさま〜", ephemeral=True)

# --- Botにコマンド登録する setup 関数（__init__.py から呼び出される想定）
async def setup(bot: discord.Client):
    bot.tree.add_command(renameset)    # /renameset コマンドを登録
    bot.tree.add_command(renamedelete) # /renamedelete コマンドを登録