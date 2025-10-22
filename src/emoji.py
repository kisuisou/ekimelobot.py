from src.model import Config
from discord import Emoji
import re

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