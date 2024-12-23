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
from openai import OpenAI

import sys

__all__ = ["TikTok", "TikTokTTSException"]

console = Console()


class OpenAItts:
    """TikTok text-to-speech"""

    def __init__(
        self,
        model: str,
        voice: str,
        identifier: str,
        path: str = "assets/temp/",
    ):

        self.model = model
        self.voice = voice

        self.client = OpenAI(
            api_key=settings.config["settings"]["openai"].get("api_key", None)
        )

        self._identifier = identifier

        self.path = path + self._identifier + "/mp3"
        os.makedirs(self.path, exist_ok=True)

    def run(self, text: str):
        """Run voice"""
        print_step(f"Generating voices for video '{self._identifier}'")
        print_substep(f"Audios will be stored in [green]{self.path}")

        [total_duration, number_of_clips, text_chunks] = self.get_voices(
            voice=self.voice, text=text
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
        """
        Downloads MP3 audio files for each chunk of text, saves them,
        and calculates total duration."""
        text = text.replace("+", "plus").replace("&", "and").replace("r/", "")

        # response = self.client.audio.speech.create(
        #     model="tts-1", voice="alloy", input=text
        # )

        chunk_filename = f"{self.path}/{output_filename}_chunk_1.mp3"

        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=voice,
            input=text,
            response_format="mp3"
        ) as response:
            with open(chunk_filename, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)


        chunk_audio = AudioSegment.from_mp3(chunk_filename)

        return [
            chunk_audio.duration_seconds,
            1,
            text,
        ]  # Return total duration of all chunks


class TikTokTTSException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Code: {self.status_code}, Message: {self.message}"
