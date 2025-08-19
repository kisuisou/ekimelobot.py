import os, discord, asyncio
from discord import app_commands
from dotenv import load_dotenv

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

        if not os.path.exists(f"./ekimelo/{ekimelo}.mp3"):
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

        await interaction.response.send_message(f"{ekimelo}を再生します")
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=f"./ekimelo/{ekimelo}.mp3"), after=my_after)

@client.event
async def on_ready():
    print("ready")
    await tree.sync(guild=discord.Object(id=int(SERVER_ID)))

client.run(TOKEN)