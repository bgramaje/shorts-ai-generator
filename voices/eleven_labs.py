import os
import random
import time
import sys
import textwrap
from typing import Optional
from pydub import AudioSegment
from elevenlabs import save, Voice, VoiceSettings
from elevenlabs.client import ElevenLabs as _ElevenLabs

from utils import settings
from utils.console import print_substep, print_step
from rich.console import Console

__all__ = ["ElevenLabs", "ElevenLabsTTSException"]

console = Console()


def chunk_text(text: str, chunk_size: int = 300) -> list:
    """Splits text into chunks of up to 'chunk_size' characters."""
    if not isinstance(text, str):
        raise ValueError("The input text must be a string.")
    return textwrap.wrap(text, width=chunk_size)


class ElevenLabs:
    """Eleven Labs Text-to-Speech"""

    def __init__(
        self,
        identifier: str,
        path: str = "assets/temp/",
    ):
        self.max_chars = 300
        self.client = _ElevenLabs(
            api_key=settings.config["settings"]["tts"].get("elevenlabs_api_key", None)
        )
        # print(self.client.models.get_all())
        self.voice = Voice(
            voice_id=settings.config["settings"]["tts"].get(
                "elevenlabs_voice_name", None
            ),
            settings=self.client.voices.get_settings(
                settings.config["settings"]["tts"].get("elevenlabs_voice_name", None)
            ),
        )
        self.api_key = settings.config["settings"]["tts"].get(
            "elevenlabs_api_key", None
        )

        if self.api_key is None or self.voice is None:
            console.print(
                "[red]API key or voice is not configured. Please update your settings."
            )
            sys.exit(1)

        self._identifier = identifier
        self.path = os.path.join(path, self._identifier, "mp3")
        os.makedirs(self.path, exist_ok=True)

    def run(self, text: str):
        """Run voice generation for a given text."""
        print_step(f"Generating voices for video '{self._identifier}'")
        print_substep(f"Audios will be stored in [green]{self.path}")

        [total_duration, number_of_clips, text_chunks] = self.get_voices(text=text)
        print_substep(f"Total duration of all audio chunks: {total_duration} seconds")
        return [total_duration, number_of_clips, text_chunks]

    def get_voices(self, text: str, output_filename: str = "output") -> float:
        """Generates MP3 audio files for text chunks and calculates total duration."""
        text = text.replace("+", "plus").replace("&", "and").replace("r/", "")
        text_chunks = chunk_text(text, self.max_chars)
        print_substep(f"Split text-to-speech content into {len(text_chunks)} chunks")

        total_duration = 0
        for i, chunk in enumerate(text_chunks):
            print_substep(f"Generating audio for chunk {i + 1}/{len(text_chunks)}")
            try:
                audio = self.client.generate(
                    text=chunk, voice=self.voice, model="eleven_turbo_v2_5"
                )
                chunk_filename = os.path.join(
                    self.path, f"{output_filename}_chunk_{i + 1}.mp3"
                )
                save(audio, chunk_filename)
                print_substep(f"Chunk {i + 1} saved successfully as {chunk_filename}")

                # Calculate duration
                chunk_audio = AudioSegment.from_mp3(chunk_filename)
                total_duration += chunk_audio.duration_seconds
                del chunk_audio
            except Exception as e:
                print_substep(f"Failed to generate audio for chunk {i + 1}. Error: {e}")

        return [total_duration, len(text_chunks), text_chunks]


class ElevenLabsTTSException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Code: {self.status_code}, Message: {self.message}"
