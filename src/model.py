from attrs import define

@define
class SoundConfig:
    file: str
    name: list[str]
    comment: str

@define
class EmojiConfig:
    name: str
    id: int

@define
class Config:
    sound_dir: str
    sounds: list[SoundConfig]
    emoji: list[EmojiConfig]
