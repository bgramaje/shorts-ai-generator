# documentation for tiktok api: https://github.com/oscie57/tiktok-voice/wiki
import os
import base64
import random
import time
from typing import Optional
import requests
import textwrap
from utils import settings
from utils.console import print_substep, print_step
from pydub import AudioSegment
from rich.console import Console
import sys

__all__ = ["TikTok", "TikTokTTSException"]

console = Console()


def chunk_text(text: str, chunk_size: int = 300) -> list:
    """Splits text into chunks of up to 'chunk_size' bytes."""
    if not isinstance(text, str):
        raise ValueError("The input text must be a string.")
    # Ensure text is encoded as bytes and split it while maintaining word boundaries
    text_chunks = textwrap.wrap(text, width=chunk_size)
    return text_chunks


class TikTok:
    """TikTok text-to-speech"""

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
        # "https://tiktok-tts.weilnet.workers.dev/api/generation"
        self.URI_BASE = "https://tiktok-tts.weilbyte.dev/api/generate"
        self.max_chars = 200

        self._session = requests.Session()
        # set the headers to the session, so we don't have to do it for every request
        self._session.headers = headers
        self._identifier = identifier

        self.path = path + self._identifier + "/mp3"
        os.makedirs(self.path, exist_ok=True)

    def run(self, text: str):
        """Run voice"""
        voice = settings.config["settings"]["tts"].get("tiktok_voice", None)
        if voice is None:
            console.print(
                "[red]"
                + "Parameter 'tiktok_voice' has not been configured. Please configure it"
            )
            sys.exit(1)

        print_step(f"Generating voices for video '{self._identifier}'")
        print_substep(f"Audios will be stored in [green]{self.path}")

        [total_duration, number_of_clips, text_chunks] = self.get_voices(
            voice=voice, text=text
        )
        print_substep(f"Total duration of all audio chunks: {total_duration} seconds")
        return [
            total_duration,
            number_of_clips,
            text_chunks,
        ]  # Return the total duration

    def get_voices(
        self, text: str, voice: Optional[str] = None, output_filename: str = "output"
    ) -> float:
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

            if (
                response.status_code == 200
                and response.headers.get("Content-Type") == "application/octet-stream"
            ):
                chunk_filename = f"{self.path}/{output_filename}_chunk_{i + 1}.mp3"
                with open(chunk_filename, "wb") as audio_file:
                    audio_file.write(response.content)
                print_substep(f"Chunk {i + 1} saved successfully as {chunk_filename}")

                # Calculate the duration of the chunk and add it to the total
                chunk_audio = AudioSegment.from_mp3(chunk_filename)
                chunk_duration = chunk_audio.duration_seconds
                total_duration += chunk_duration
                del chunk_audio
            else:
                print_substep(
                    f"Failed to download chunk {i + 1}. Status code: {response.status_code}"
                )

        return [
            total_duration,
            len(text_chunks),
            text_chunks,
        ]  # Return total duration of all chunks


class TikTokTTSException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Code: {self.status_code}, Message: {self.message}"
