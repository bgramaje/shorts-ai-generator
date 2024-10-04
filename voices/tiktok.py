# documentation for tiktok api: https://github.com/oscie57/tiktok-voice/wiki
import os
import base64
import random
import time
from typing import Optional, Final
import requests
import textwrap
from utils import settings
from utils.console import print_substep, print_step
from pydub import AudioSegment

__all__ = ["TikTok", "TikTokTTSException"]

disney_voices: Final[tuple] = (
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    "en_female_madam_leota",  # Madame Leota
    "en_male_ghosthost",  # Ghost Host
    "en_male_pirate",  # pirate
)

eng_voices: Final[tuple] = (
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    "en_male_narration",  # Narrator
    "en_female_emotional",  # Peaceful
    "en_male_cody",  # Serious
)

non_eng_voices: Final[tuple] = (
    # Western European voices
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    "it_male_m18",  # Italian - Male
    # South american voices
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # asian voices
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
)

vocals: Final[tuple] = (
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_female_ht_f08_glorious",  # Glorious
    "en_male_sing_funny_it_goes_up",  # It Goes Up
    "en_male_m2_xhxs_m03_silly",  # Chipmunk
    "en_female_ht_f08_wonderful_world",  # Dramatic
)

def chunk_text(text: str, chunk_size: int = 300) -> list:
    """Splits text into chunks of up to 'chunk_size' bytes."""
    # Ensure the input is a string
    # print("cactoa")
    # print(type(text))
    if not isinstance(text, str):
        raise ValueError("The input text must be a string.")
    # Ensure text is encoded as bytes and split it while maintaining word boundaries
    text_chunks = textwrap.wrap(text, width=chunk_size)
    return text_chunks


class TikTok:
    """TikTok Text-to-Speech Wrapper"""

    def __init__(
            self,
            identifier: str, 
            path: str = "assets/temp/",
        ):
        headers = {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; "
            "Build/NRD90M;tt-ok/3.12.13.1)",
            "Cookie": f"sessionid={settings.config['settings']['tts']['tiktok_sessionid']}",
        }
        #"https://tiktok-tts.weilnet.workers.dev/api/generation"
        self.URI_BASE = (
            "https://tiktok-tts.weilbyte.dev/api/generate"
        )
        self.max_chars = 200

        self._session = requests.Session()
        # set the headers to the session, so we don't have to do it for every request
        self._session.headers = headers
        self._identifier = identifier
        
        self.path = path + self._identifier + "/mp3"
        os.makedirs(self.path, exist_ok=True)

    def run(self, text: str, random_voice: bool = False):
        """Run voice"""
        if random_voice:
            voice = self.random_voice()
        else:
            voice = settings.config["settings"]["tts"].get("tiktok_voice", None)

        print_step(f"Generating voices for video '{self._identifier}'")
        print_substep(f"Audios will be stored in [green]{self.path}")

        [total_duration, number_of_clips] = self.get_voices(voice=voice, text=text)
        print_substep(f"Total duration of all audio chunks: {total_duration} seconds")
        return [total_duration, number_of_clips]  # Return the total duration

    def get_voices(self, text: str, voice: Optional[str] = None, output_filename: str = "output") -> float:
        """Downloads MP3 audio files for each chunk of text, saves them, and calculates total duration."""
        text = text.replace("+", "plus").replace("&", "and").replace("r/", "")
        text_chunks = chunk_text(text)
        print_substep(f"Splitted text-to-speech content into {len(text_chunks)} chunks")

        total_duration = 0  # Initialize total duration
        for i, chunk in enumerate(text_chunks):
            params = {"text": chunk}
            if voice is not None:
                params["voice"] = voice

            try:
                print_substep(f"Generating audio for chunk {i + 1}/{len(text_chunks)}")
                response = self._session.post(self.URI_BASE, json=params)
            except ConnectionError:
                time.sleep(random.randrange(1, 7))
                response = self._session.post(self.URI_BASE, json=params)

            if response.status_code == 200 and response.headers.get('Content-Type') == 'application/octet-stream':
                chunk_filename = f"{self.path}/{output_filename}_chunk_{i + 1}.mp3"
                with open(chunk_filename, 'wb') as audio_file:
                    audio_file.write(response.content)
                print_substep(f"Chunk {i + 1} saved successfully as {chunk_filename}")

                # Calculate the duration of the chunk and add it to the total
                chunk_audio = AudioSegment.from_mp3(chunk_filename)
                chunk_duration = chunk_audio.duration_seconds
                total_duration += chunk_duration
                del chunk_audio
            else:
                print_substep(f"Failed to download chunk {i + 1}. Status code: {response.status_code}")

        return [total_duration, len(text_chunks)]  # Return total duration of all chunks

    @staticmethod
    def random_voice() -> str:
        return random.choice(eng_voices)


class TikTokTTSException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Code: {self.status_code}, Message: {self.message}"