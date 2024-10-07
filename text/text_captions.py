import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from utils.console import (
    print_step,
    print_substep
)

def transcribe_audio(
    audio_path: str,
):
    print_step("Transcribing audio information using whisper 📁")
    model = whisper.load_model(name="small", download_root="./models")

    result = model.transcribe(
        audio_path, 
        word_timestamps=True, 
        language="es"
    )

    # create dictionary
    word_timings = []
    for segment in result['segments']:
        for word in segment['words']:
            word_timings.append({
                'word': word['word'], 
                'start': word['start'], 
                'end': word['end']
            })
    
    print_substep("> Finished transcribing audio information using whisper 📁")
    return word_timings


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
        word = word_info['word']
        start_time = word_info['start']
        end_time = word_info['end']

        # create a textClip for each word, you can customize the font, size, position, etc.
        text_clip = TextClip(
            word, 
            fontsize=50, 
            color='white', 
            font="Poppins-Black", 
            stroke_color="black", 
            stroke_width=2
        ) \
            .set_position(('center', 'center')) \
            .set_start(start_time) \
            .set_end(end_time)
        
        # Append to list of text clips
        text_clips.append(text_clip)
    
    print_substep("> Finished generating captions for the video 📁")
    # # Combine the original video with the text clips
    final_video = CompositeVideoClip([video] + text_clips)
    final_video.write_videofile(output_path, fps=video.fps)
    print_step("Done! 🎉 The video is in the results folder 📁")

