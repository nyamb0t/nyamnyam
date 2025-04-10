# utils/channel_storage.py
# --- サーバーごとのチャンネル設定を保存・読み込むユーティリティ関数！

import os
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- 保存先ファイルのパスを取得
def get_guild_file(guild_id):
    return os.path.join(DATA_DIR, f"{guild_id}_channels.json")

# --- データの読み込み
def load_guild_data(guild_id):
    path = get_guild_file(guild_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"text_channels": [], "vc_channel": None, "last_sent": {}}

# --- データの保存
def save_guild_data(guild_id, data):
    path = get_guild_file(guild_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)