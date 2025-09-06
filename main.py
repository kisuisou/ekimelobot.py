import os, discord, asyncio
from discord import app_commands, Emoji
from dotenv import load_dotenv
from cattrs import structure
from pathlib import Path
import tomllib

from src.model import Config
from src.emoji import load_emoji, replace_custom_emojis
from src.config import build_dict

with open('config.toml', 'rb') as f:
    config = structure(tomllib.load(f), Config)

SOUND_DIR = Path(config.sound_dir)

name_dict, alias_dict = build_dict(config.sounds)

load_dotenv("./.env")

TOKEN=os.environ.get("TOKEN")
SERVER_ID=os.environ.get("SERVER_ID")

intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True          
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
emoji: dict[str, Emoji] | None = None

@tree.command(name="emplay",description="駅メロを流します")
async def emplay_command(interaction: discord.Interaction, ekimelo: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ ボイスチャンネルに入ってから実行してください。")
            return

        voice_channel = interaction.user.voice.channel

        if interaction.guild.voice_client:
            vc = interaction.guild.voice_client
        else:
            vc = await voice_channel.connect()

        global name_dict
        global alias_dict
        if ekimelo in alias_dict:
            name = alias_dict[ekimelo]
            data = name_dict[name]
        elif ekimelo in name_dict:
            data = name_dict[ekimelo]
        else:
            await interaction.response.send_message("❌ 駅メロが見つかりませんでした。")
            return
        path = SOUND_DIR / data.file

        if not os.path.exists(path):
            await interaction.response.send_message("❌ ファイルが見つかりませんでした。")
            return

        if vc.is_playing():
            vc.stop()

        def my_after(error):
            coro = vc.disconnect()
            fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
            try:
                fut.result()
            except:
                pass

        global emojis
        comment = replace_custom_emojis(data.comment, emojis)
        await interaction.response.send_message(f'▶️ {comment}')
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=str(path), before_options="-nostdin", options="-vn -ar 48000 -ac 2 -f s16le"), after=my_after)

@client.event
async def on_ready():
    print("ready")
    await tree.sync(guild=discord.Object(id=int(SERVER_ID)))
    global emojis
    emojis = load_emoji(client, config)

client.run(TOKEN)