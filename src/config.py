from src.model import SoundConfig

def build_dict(sounds: list[SoundConfig]) -> tuple[dict[str, SoundConfig], dict[str, str]]: 
    """名前からファイル名なだちを返せるようなdictを生成する

    :params sounds: configファイルのうち[[sound]]セクションのもの
    :type txt: list[SoundConfig]
    :returns: 名前をkey、ファイル名などのconfigをvalueにしたdict、その他の名前を正しい名前に変換するためのdict（aliasがkey、正式名がvalue）
    :rtype: tuple[dict[str, SoundConfig], dict[str, str]]
    """
    names: dict[str, SoundConfig] = {}
    aliases: dict[str, str] = {}
    for sound in sounds:
        name = sound.name[0]
        alias = sound.name[1:]
        names[name] = sound
        for n in alias:
            aliases[n] = name
    return (names, aliases)