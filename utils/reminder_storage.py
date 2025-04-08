# utils/reminder_storage.py
# --- リマインダー情報の保存・読み込みに関する処理をまとめたファイル！
#     JSONファイルを使ってリマインダー設定を保持してるよ！

import os
import json

# --- 毎日リマインダーの保存先パスを作る
def get_reminder_file_path(guild_id: int, reminder_type: str) -> str:
    folder = f"data/reminders/{guild_id}"
    os.makedirs(folder, exist_ok=True)  # フォルダがなければ作る
    return f"{folder}/{reminder_type}.json"

# --- 毎日リマインダーを読み込む
def load_reminders(guild_id: int, reminder_type: str):
    path = get_reminder_file_path(guild_id, reminder_type)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- 毎日リマインダーを書き込む
def save_reminders(guild_id: int, reminder_type: str, data):
    path = get_reminder_file_path(guild_id, reminder_type)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- 一回きりリマインダーの保存パスを取得
def get_one_time_reminder_path(guild_id: int) -> str:
    folder = f"data/reminders/{guild_id}"
    os.makedirs(folder, exist_ok=True)
    return f"{folder}/one_time.json"

# --- 一回きりリマインダーを読み込む
def load_one_time_reminders():
    all_reminders = {}
    base_folder = "data/reminders"
    if not os.path.exists(base_folder):
        return all_reminders

    for guild_id in os.listdir(base_folder):
        path = os.path.join(base_folder, guild_id, "one_time.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                all_reminders[guild_id] = json.load(f)
    return all_reminders

# --- 一回きりリマインダーを保存する
def save_one_time_reminder(reminder_data):
    guild_id = reminder_data["guild_id"]
    path = get_one_time_reminder_path(int(guild_id))
    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing.append(reminder_data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)