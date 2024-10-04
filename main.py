#!/usr/bin/env python
import math
import sys
from os import name
from pathlib import Path
from subprocess import Popen
from typing import NoReturn
import uuid
import re

from utils import settings

from utils.console import print_markdown
from utils.ffmpeg_install import ffmpeg_install
from voices.voice_generator import save_text_to_mp3
from video.openai import ask_chatgpt
from video.video_background import (
    chop_background,
    download_background_audio,
    download_background_video,
    get_background_config,
)
from video.video_creator import make_final_video

__VERSION__ = "3.3.0"

print(
    """
██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
 ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
  ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
)
print_markdown("## shorts-ai-generator", padding=1)

print_markdown(
    "### Thanks for using this tool! Feel free to contribute to this project on GitHub! If you have any questions, feel free to join my Discord server or submit a GitHub issue. You can find solutions to many common problems in the documentation: https://reddit-video-maker-bot.netlify.app/"
, padding=1
)

if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11]:
        print(
            "Hey! Congratulations, you've made it so far (which is pretty rare with no Python 3.10). Unfortunately, this program only works on Python 3.10. Please install Python 3.10 and try again."
        )
        sys.exit()
    ffmpeg_install()
    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    
    response = "caca"
    response = ask_chatgpt("A short about anime curiosities of attack on titan")

    config is False and sys.exit()
    prueba = {
        "id": re.sub(r"[^\w\s-]", "", str(uuid.uuid4())),
        "title": str(uuid.uuid4()),
        "text": response
    }
    
    [total_duration, number_of_clips] = save_text_to_mp3(prueba)

    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }

    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    background = chop_background(bg_config, total_duration, prueba)

    make_final_video(obj=prueba, length=total_duration, number_of_clips=number_of_clips)


    