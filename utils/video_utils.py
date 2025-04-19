import os
import uuid
import whisper
from moviepy.editor import VideoFileClip

model = whisper.load_model("base")

def save_video_temporarily(file_data, extension=".mp4") -> str:
    filename = f"temp_{uuid.uuid4()}{extension}"
    with open(filename, "wb") as f:
        f.write(file_data)
    return filename

def extract_audio(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".mp3")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()
    return audio_path

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
