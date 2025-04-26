# events/message_handler.py
# --- メッセージの監視をして、5桁の数字を検出＆転送、VC名変更をするイベントハンドラ！

import discord
from discord.ext import commands
import re
import time
from utils.channel_storage import load_guild_data, save_guild_data

recent_numbers = {}  # サーバーごとに、最近送信された数字を記録（重複送信防止）

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        data = load_guild_data(guild_id)

        # --- 5桁の数字を検出
        match = re.search(r"\b\d{5,6}\b", message.content)
        if not match:
            return

        number = match.group()

        # --- 重複送信を5分以内は防ぐ
        now = time.time()
        if guild_id not in recent_numbers:
            recent_numbers[guild_id] = {}
        if number in recent_numbers[guild_id]:
            if now - recent_numbers[guild_id][number] < 300:
                return  # 5分以内に同じ数字が送られてたらスキップ

        recent_numbers[guild_id][number] = now  # 今回の送信を記録

        # --- 転送チャンネルに送信
        for channel_id in data["text_channels"]:
            if message.channel.id == channel_id:
                continue  # 元のチャンネルには送らない

            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(number)

        # --- VCの名前を変更
        vc_id = data.get("vc_channel")
        print(f"DEBUG: vc_id = {vc_id}")
        
        if vc_id:
            vc_channel = self.bot.get_channel(vc_id)
            print(f"DEBUG: vc_channel = {vc_channel}")  # ← ここ追加！
            print(f"DEBUG: vc_channel name = {vc_channel.name}")
            
            if isinstance(vc_channel, discord.VoiceChannel):
                # すでに同じ番号が入ってるなら変更不要
                if f"【{number}】" in vc_channel.name:
                    print("DEBUG: すでに同じ番号が入ってるから変更しないよ")
                    return

                # もともと別の数字が入ってる場合は置き換える、それ以外はつける
                if re.search(r"【\d{5,6}】", vc_channel.name):
                    new_name = re.sub(r"【\d{5,6}】", f"【{number}】", vc_channel.name)
                else:
                    new_name = f"{vc_channel.name} 【{number}】"
                    
                    print(f"DEBUG: VC名を {new_name} に変更するよ")
                await vc_channel.edit(name=new_name)

# --- このイベントをBotに登録する setup 関数
async def setup(bot):
    await bot.add_cog(MessageHandler(bot))