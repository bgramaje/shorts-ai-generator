#!/usr/bin/env python
import sys
from pathlib import Path
import uuid
import re
import os
from utils import settings

from utils.console import print_markdown
from utils.ffmpeg_install import ffmpeg_install
from voices.voice_generator import save_text_to_mp3
from video.video_creator import make_final_video

from video.openai import (
    chatgpt_video_content,
    load_openai_response
)

from video.video_background import (
    chop_background,
    download_background_audio,
    download_background_video,
    get_background_config,
)

from utils.console import (
    print_substep
)

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

    response = None

    response = """
    {
        "title": "Un maestro alienígena que enseña a matarlo! 👽", 
        "description": "",
        "tags": "", 
        "content": "¿Sabías que Bell Cranel, el protagonista de Danmachi, tiene un pasado que lo conecta directamente con el poderoso dios Zeus? ⚡ Aunque no se menciona mucho en el anime, Bell fue criado por Zeus antes de unirse a la Familia Hestia. Esta relación explica su fuerte determinación y su ambición de convertirse en un héroe legendario. ¡Incluso su nombre, Bell, podría ser un guiño al 'relámpago' de Zeus! 🌩️ Un detalle que añade un toque épico a su historia y lo conecta con las leyendas mitológicas."
    }"""
    if response is None:
        response = chatgpt_video_content("Un short de Youtube sobre One Piece, es difícil no emocionarse con la despedida del Going Merry. Pero, ¿sabías que Eiichiro Oda dijo que esta escena fue una de las más difíciles de escribir para él? El vínculo entre los personajes y su barco era tan fuerte que sentía como si estuviera despidiendo a un amigo. ¿Te hizo llorar esta escena también?")
        print(response)
    data = load_openai_response(response)

    if data is None:
        print_substep("Could not decode OpenAI response into a json dictionary. Please try again later.")
        sys.exit()

    config is False and sys.exit()
    content = {
        "id": re.sub(r"[^\w\s-]", "", str(uuid.uuid4())),
        "title": data['title'],
        "text": data['content']
    }
    
    [total_duration, number_of_clips, text_chunks] = save_text_to_mp3(content)

    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }

    defaultPath = f"results/{content['id']}"

    if not os.path.exists(defaultPath):
        print_substep("The 'results' folder could not be found so it was automatically created.")
        os.makedirs(defaultPath, exist_ok=True)

    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])

    background = chop_background(bg_config, total_duration, content)

    [video_path, audio_path] = make_final_video(
        obj=content, 
        length=total_duration, 
        number_of_clips=number_of_clips,
        path=defaultPath,
    )