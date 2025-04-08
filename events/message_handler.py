# events/message_handler.py
# --- メッセージの中にある「5桁の数字」を検出して、転送したりVC名を変更したりする処理！

import re
import discord
import os
import json
from datetime import datetime

DATA_DIR = "data"

# --- サーバーごとのデータファイルのパスを作る
def get_guild_file(guild_id):
    return os.path.join(DATA_DIR, f"{guild_id}_channels.json")

# --- ファイルから設定を読み込む
def load_guild_data(guild_id):
    path = get_guild_file(guild_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"text_channels": [], "vc_channel": None, "last_sent": {}}

# --- 設定を保存する
def save_guild_data(guild_id, data):
    path = get_guild_file(guild_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- on_message イベントをセットする関数（nyam.py から呼ばれる）
def setup_message_handler(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Bot自身のメッセージは無視！

        await bot.process_commands(message)  # コマンド処理（!setch など）も忘れず！

        if message.content.startswith("!"):
            return  # コマンド系は無視（数字検出しない）

        # --- メッセージから5桁の数字を探す（前後が数字じゃない場合に限定）
        five_digit_numbers = re.findall(r'(?<!\d)\d{5}(?!\d)', message.content)
        if not five_digit_numbers:
            return

        number = five_digit_numbers[0]  # 複数あっても最初の1つだけ使う
        guild_id = message.guild.id
        data = load_guild_data(guild_id)

        now = datetime.utcnow().timestamp()
        last_sent = data.get("last_sent", {})

        if number not in last_sent:
            last_sent[number] = {}

        # --- 転送設定されてるテキストチャンネルに送る
        for channel_id in data.get("text_channels", []):
            if channel_id == message.channel.id:
                continue  # 送信元チャンネルならスキップ！

            last_time = last_sent[number].get(str(channel_id), 0)
            if now - last_time < 300:
                continue  # 同じ内容を5分以内に送ってたらスキップ！

            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(number)
                last_sent[number][str(channel_id)] = now  # 最終送信時刻を更新

        # --- VC名の変更処理（【12345】 に更新）
        vc_channel_id = data.get("vc_channel")
        if vc_channel_id:
            vc_channel = bot.get_channel(vc_channel_id)
            if vc_channel:
                current_name = vc_channel.name
                # 【xxxxx】 がついてたら取り除く
                base_name = re.sub(r'【\d{5}】$', '', current_name).strip()
                new_name = f"{base_name}  【{number}】"
                if current_name != new_name:
                    try:
                        await vc_channel.edit(name=new_name)
                    except Exception as e:
                        print(f"VC名前変更失敗: {e}")

        # --- 保存して終了
        data["last_sent"] = last_sent
        save_guild_data(guild_id, data)