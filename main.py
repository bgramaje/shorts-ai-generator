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
from utils.console import (
    print_step,
    print_substep
)
from video.video_creator import make_final_video
from os.path import exists  # Needs to be imported specifically
import os

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

__VERSION__ = "3.3.0"

print_markdown("## shorts-ai-generator", padding=1)
print_markdown("### Thanks for using this tool! Feel free to contribute to this project on GitHub!", padding=1)

if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11, 12]:
        print("Hey! Unfortunately, this program only works on Python 3.10|11|12.")
        sys.exit()

    ffmpeg_install()

    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    
    # response = """
    #     Did you know that "Attack on Titan" almost didn't happen? The creator, Hajime Isayama, considered shelving the project after the initial pitch was rejected. However, he fine-tuned his concept and it became a massive global sensation. Here's a fun fact: the famous ODM gear actually draws inspiration from ancient martial arts. The fluidity and speed are reminiscent of ninjutsu! And speaking of characters, did you notice how Eren was nearly written as a Titan from the very first chapter? That plot twist was supposed to be revealed much later. There's also an intriguing tidbit about the Titans themselves: their erratic movement was inspired by horror films, aiming to create an unsettling sense of chaos. Plus, the walls' names - Maria
    # """
    response = """
        ¿Sabías que un solo titán promedio es lo suficientemente fuerte como para arrasar con una ciudad entera? ¡Es fascinante! "Attack on Titan" no solo es conocido por sus impresionantes batallas, sino también por su profunda historia y giros emocionales. Uno de 
        los hechos más curiosos es que los titanes fueron inspirados por la sensación de vulnerabilidad e impotencia del creador Hajime Isayama. Además, todos los titanes, sin excepción, tienen una debilidad crucial: un punto detrás de su cuello que, si es cortado, 
        los acabará instantáneamente. Y hablando de sorpresas, ¿sabías que Eren Jaeger se transforma en un titán en el quinto episodio del
    """
    # response = ask_chatgpt("Un short de youtube sobre curiosidades de ataque a los titanes")
    # print(response)

    config is False and sys.exit()
    content = {
        "id": re.sub(r"[^\w\s-]", "", str(uuid.uuid4())),
        "title": str(uuid.uuid4()),
        "text": response
    }
    
    [total_duration, number_of_clips] = save_text_to_mp3(content)

    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }

    defaultPath = f"results/{content['id']}"

    if not exists(defaultPath):
        print_substep("The 'results' folder could not be found so it was automatically created.")
        os.makedirs(defaultPath)

    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])

    background = chop_background(bg_config, total_duration, content)

    [video_path, audio_path] = make_final_video(
        obj=content, 
        length=total_duration, 
        number_of_clips=number_of_clips,
        path=defaultPath
    )