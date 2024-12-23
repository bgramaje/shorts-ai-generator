from typing import Tuple

from rich.console import Console

from .tiktok import TikTok
from .openai import OpenAItts
from .eleven_labs import ElevenLabs

from utils import settings
from utils.console import print_step, print_table

console = Console()

TTSProviders = {
    "TikTok": TikTok,
}

def save_text_to_mp3(obj) -> Tuple[int, int]:
    """Saves text to MP3 files.

    Args:
        reddit_obj (): Reddit object received from reddit API in reddit/subreddit.py

    Returns:
        tuple[int,int]: (total length of the audio, the number of comments audio was generated for)
    """
    # retrieve voice choice from config.toml file
    voice = settings.config["settings"]["tts"]["voice_choice"]
    if(str(voice).casefold() != 'tiktok'):
        return
    # create the text-2-speech engine
    # engine = TikTok(identifier=obj["id"])
    #onyx
    #engine = OpenAItts(identifier=obj["id"], model="tts-1", voice="echo")
    engine = ElevenLabs(identifier=obj["id"])

    [total_duration, number_of_clips, text_chunks] =  engine.run(text=obj["text"])
    return [total_duration, number_of_clips, text_chunks]

