import whisper
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from utils.console import print_step, print_substep

from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"}
)

# load model
model = whisper.load_model(name="turbo", download_root="./models")

def transcribe_audio(audio_path: str, raw_text: str):
    try:
        if not os.path.isfile(audio_path):
            print(f"Audio file {audio_path} does not exist.")
            return None

        if os.path.getsize(audio_path) == 0:
            print(f"Audio file {audio_path} is empty.")
            return None

        print_step("Transcribing audio information using Whisper 📁")
        initial_prompt = f"""
            You are going to transcribe an audio with the following content in quotes:
            '{raw_text}'
            Please make sure that what you predict is the same as the given raw text.
        """
        
        # Transcribe the audio file with word timestamps
        result = model.transcribe(
            audio_path,
            word_timestamps=True,
            language="es",
            initial_prompt=initial_prompt
        )

        word_timings = []
        for segment in result["segments"]:
            for word in segment["words"]:
                print(word)
                word_timings.append(
                    {"word": word["word"], "start": word["start"], "end": word["end"]}
                )

        print_substep("Finished transcribing audio information using Whisper 📁")
        return word_timings

    except RuntimeError as e:
        print(f"Error transcribing audio: {str(e)}")
        return None


def generate_captions(
    word_timings,
    video_path: str,
    output_path: str,
):
    print_step("Generating captions for the video 📁")
    # read video
    video = VideoFileClip(video_path)
    # create text clips for each word and overlay them at the correct time
    text_clips = []
    for word_info in word_timings:
        word = word_info["word"]
        start_time = word_info["start"]
        end_time = word_info["end"]
        text_clip = (
            TextClip(
                word,
                fontsize=50,
                color="white",
                font="Poppins-Black",
                stroke_color="black",
                stroke_width=2,
            )
            .set_position(("center", "center"))
            .set_start(start_time)
            .set_end(end_time)
        )

        # Append to list of text clips
        text_clips.append(text_clip)

    print_substep("Finished generating captions for the video 📁")
    # # Combine the original video with the text clips
    final_video = CompositeVideoClip([video] + text_clips)
    final_video.write_videofile(output_path, fps=video.fps, logger=None)
    print_step(f"🎉 Done! 📁 The video is in {output_path} ")
