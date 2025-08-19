import os, discord, asyncio
from discord import app_commands, Emoji
from dotenv import load_dotenv
from pathlib import Path
import tomllib

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

SOUND_DIR = Path(config["sound_dir"])

load_dotenv("./.env")

TOKEN=os.environ.get("TOKEN")
SERVER_ID=os.environ.get("SERVER_ID")

intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True          
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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

        data = config["sounds"][ekimelo]
        path = SOUND_DIR / data["file"]

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

        await interaction.response.send_message(data["comment"])
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=path), after=my_after)

@client.event
async def on_ready():
    print("ready")
    await tree.sync(guild=discord.Object(id=int(SERVER_ID)))

client.run(TOKEN)