import ffmpeg
import multiprocessing
import threading
import tempfile
import time
from tqdm import tqdm

from typing import Dict, Final, Tuple
from rich.progress import track
from rich.console import Console
from os.path import exists  # Needs to be imported specifically
import os
from utils import settings
from utils.cleanup import cleanup
from utils.console import (
    print_step,
    print_substep
)

console = Console()

class ProgressFfmpeg(threading.Thread):
    def __init__(self, vid_duration_seconds, progress_update_callback):
        threading.Thread.__init__(self, name="ProgressFfmpeg")
        self.stop_event = threading.Event()
        self.output_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.vid_duration_seconds = vid_duration_seconds
        self.progress_update_callback = progress_update_callback

    def run(self):
        while not self.stop_event.is_set():
            latest_progress = self.get_latest_ms_progress()
            if latest_progress is not None:
                completed_percent = latest_progress / self.vid_duration_seconds
                self.progress_update_callback(completed_percent)
            time.sleep(1)

    def get_latest_ms_progress(self):
        lines = self.output_file.readlines()

        if lines:
            for line in lines:
                if "out_time_ms" in line:
                    out_time_ms_str = line.split("=")[1].strip()
                    if out_time_ms_str.isnumeric():
                        return float(out_time_ms_str) / 1000000.0
                    else:
                        # Handle the case when "N/A" is encountered
                        return None
        return None

    def stop(self):
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()


def prepare_background(id: str, W: int, H: int) -> str:
    output_path = f"assets/temp/{id}/background_noaudio.mp4"
    output = (
        ffmpeg.input(f"assets/temp/{id}/background.mp4")
        .filter("crop", f"ih*({W}/{H})", "ih")
        .output(
            output_path,
            an=None,
            **{
                "c:v": "h264",
                "b:v": "20M",
                "b:a": "192k",
                "threads": multiprocessing.cpu_count(),
            },
        )
        .overwrite_output()
    )
    try:
        output.run(quiet=True)
    except ffmpeg.Error as e:
        print(e.stderr.decode("utf8"))
        exit(1)
    return output_path

def merge_background_audio(audio: ffmpeg, reddit_id: str):
    """Gather an audio and merge with assets/backgrounds/background.mp3
    Args:
        audio (ffmpeg): The TTS final audio but without background.
        reddit_id (str): The ID of subreddit
    """
    background_audio_volume = settings.config["settings"]["background"]["background_audio_volume"]
    if background_audio_volume == 0:
        return audio  # Return the original audio
    else:
        # sets volume to config
        bg_audio = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp3").filter(
            "volume",
            background_audio_volume,
        )
        # Merges audio and background_audio
        merged_audio = ffmpeg.filter([audio, bg_audio], "amix", duration="longest")
        return merged_audio  # Return merged audio


def make_final_video(
    obj,   
    number_of_clips: int,
    length: int
):
    # settings values
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])
    
    opacity = settings.config["settings"]["opacity"]
    id = obj["id"]

    print_step("Creating the final video 🎥")
    background_clip = ffmpeg.input(prepare_background(id, W=W, H=H))

    audio_clips = list()
    audio_clips = [
        ffmpeg.input(f"assets/temp/{id}/mp3/postaudio-{i}.mp3")
        for i in track(range(number_of_clips + 1), "Collecting the audio files...")
    ]
    audio_clips.insert(0, ffmpeg.input(f"assets/temp/{id}/mp3/title.mp3"))
    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    
    ffmpeg.output(
        audio_concat, f"assets/temp/{id}/audio.mp3", **{"b:a": "192k"}
    ).overwrite_output().run(quiet=True)

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")

    screenshot_width = int((W * 45) // 100)
    audio = ffmpeg.input(f"assets/temp/{id}/audio.mp3")
    final_audio = merge_background_audio(audio, id)

    defaultPath = f"results/{id}"

    if not exists(defaultPath):
        print_substep("The 'results' folder could not be found so it was automatically created.")
        os.makedirs(defaultPath)


    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %")

    def on_update_example(progress) -> None:
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)

    with ProgressFfmpeg(length, on_update_example) as progress:
        path = defaultPath + f"/final_video"
        path = (
            path[:251] + ".mp4"
        )  # Prevent a error by limiting the path length, do not change this.
        try:
            ffmpeg.output(
                background_clip,
                final_audio,
                path,
                f="mp4",
                **{
                    "c:v": "h264",
                    "b:v": "20M",
                    "b:a": "192k",
                    "threads": multiprocessing.cpu_count(),
                },
            ).overwrite_output().global_args("-progress", progress.output_file.name).run(
                quiet=True,
                overwrite_output=True,
                capture_stdout=False,
                capture_stderr=False,
            )
        except ffmpeg.Error as e:
            print(e.stderr.decode("utf8"))
            exit(1)

    old_percentage = pbar.n
    pbar.update(100 - old_percentage)

    pbar.close()
    # save_data(subreddit, filename + ".mp4", title, idx, background_config["video"][2])
    print_step("Removing temporary files 🗑")
    #cleanups = cleanup(id)
    # print_substep(f"Removed {cleanups} temporary files 🗑")
    print_step("Done! 🎉 The video is in the results folder 📁")