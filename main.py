import os, discord, asyncio
from discord import app_commands, Emoji
from dotenv import load_dotenv
from attrs import define
from cattrs import structure
from pathlib import Path
import tomllib
import re

@define
class SoundConfig:
    file: str
    comment: str

@define
class EmojiConfig:
    name: str
    id: int

@define
class Config:
    sound_dir: str
    sounds: dict[str, SoundConfig]
    emoji: list[EmojiConfig]

with open('config.toml', 'rb') as f:
    config = structure(tomllib.load(f), Config)

SOUND_DIR = Path(config.sound_dir)

load_dotenv("./.env")

TOKEN=os.environ.get("TOKEN")
SERVER_ID=os.environ.get("SERVER_ID")

def load_emoji(client, config: Config) -> dict[str, Emoji]:
    """tomlにあるemojiを全てdiscordに照会しemoji objectを得てdictにする

    :param client: discordクライアント 
    :type client: Discord.Client
    :param config: configのdata class 
    :type config: Config
    :returns: emojiの名前をkey、Emojiの実体をvalueとしたdict（e.g. `{':st:': (some Emoji object)}`）
    :rtype: dict[str, Emoji]
    """
    emojis: dict[str, Emoji] = {}
    for emoji_config in config.emoji:
        name = emoji_config.name
        emoji = client.get_emoji(emoji_config.id)
        if emoji is None:
            continue
        emojis[f':{name}:'] = emoji
    return emojis

def replace_custom_emojis(txt: str, d: dict[str, Emoji]) -> str:
    """コマンドへの返答にemoji（e.g. `:st:`）が含められていた場合、discordのEmoji objectに変換する

    :param txt: 変換対象の文字列
    :type txt: str
    :param d: Emoji変換用dict（load_emojiで返されるdictを想定）
    :type d: dict[str, Emoji]
    :returns: custom emojiをdiscordで読めるように変換した文字列
    :rtype: str
    """
    # `:st:|:jr_west:`のようなregexパターンを作る
    pattern = '|'.join(re.escape(k) for k in d.keys()) 
    return re.sub(pattern, lambda m: str(d[m.group(0)]), txt)

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

        data = config.sounds[ekimelo]
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
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=str(path)), after=my_after)

@client.event
async def on_ready():
    print("ready")
    await tree.sync(guild=discord.Object(id=int(SERVER_ID)))
    global emojis
    emojis = load_emoji(client, config)

client.run(TOKEN)