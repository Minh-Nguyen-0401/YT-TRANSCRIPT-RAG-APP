import os, re
import tempfile
import subprocess
import whisper
from unidecode import unidecode
from youtube_transcript_api import YouTubeTranscriptApi

from dotenv import load_dotenv
load_dotenv()


def get_video_title(youtube_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", youtube_url],
            capture_output=True, text=True, check=True, encoding="utf-8"
        )
        title = result.stdout.strip()
        return title
    except subprocess.CalledProcessError:
        return "transcription"

def sanitize_title(title):
    title = unidecode(title)
    sanitized = re.sub(r'[^\w\s\-]', '', title)
    sanitized = sanitized.lower().strip().replace(' ', '_')
    return sanitized

def read_transcription(title):
    try:
        with open(f"./data_trans/{title}_transcript.txt", "r", encoding="utf-8") as f:
            cur_transcription = f.read()
            return cur_transcription
    except Exception as e:
        print(f"There was an error: {e}")

def extract_yt_direct(youtube_url):
    try:
        url = youtube_url
        video_id = re.search(r'.+?v=(.*)',url)[1]
        trans = YouTubeTranscriptApi.get_transcript(video_id)
        list_trans = []

        for chunk in trans:
            list_trans.append(chunk.get("text"))

        trans_fin = " ".join(list_trans).replace("xa0","")
        trans_fin_san = re.sub(r'[^\w\s\-]', '', trans_fin)
        trans_fin_san = re.sub(r'\s+', ' ', trans_fin_san)
        return trans_fin_san
    except Exception as e:
        return "error"

def extract_transcription(url=None):
    if url != None:
        youtube_url = url
    else:
        youtube_url = str(input("Enter a youtube url: "))
    
    # Get video title
    title = sanitize_title(get_video_title(youtube_url))
    title = title if len(title) < 38 else title[:38] #ensure suitability with pinecone index 

    # Check if transcript already in place
    if not os.path.exists(f"./data_trans/{title}_transcript.txt") or len(read_transcription(title))==0:
        # Case 1: Can extract transcript directly online
        transcription = extract_yt_direct(youtube_url=youtube_url)
        if "error" not in transcription and len(transcription) != 0:
            with open(f"./data_trans/{title}_transcript.txt", "w", encoding="utf-8") as f:
                    f.write(transcription)

        # Case 2: Extract audio & transcribe
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                audio_file_path = os.path.join(temp_dir, "audio.mp3")
                
                # Download only audio using yt-dlp
                subprocess.run([
                    "yt-dlp",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--output", audio_file_path,
                    "--ffmpeg-location", r"C:\Users\ACER\Downloads\ffmpeg-master-latest-win64-gpl\bin",
                    youtube_url
                ], check=True)

                print("Downloaded file path:", audio_file_path)
                print("Exists?", os.path.isfile(audio_file_path))

                os.environ["PATH"] += os.pathsep + r"C:\Users\ACER\Downloads\ffmpeg-master-latest-win64-gpl\bin"
                print("PATH:", os.environ["PATH"])
                
                # Load Whisper model
                """remember to install cuda version that matches your gpu: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"""
                whisper_model = whisper.load_model("base", device="cuda")           
                print("Model device:", whisper_model.device)
                
                # Transcribe
                cur_transcription = whisper_model.transcribe(audio_file_path, fp16=True)["text"].strip()

                with open(f"./data_trans/{title}_transcript.txt", "w", encoding="utf-8") as f:
                    f.write(cur_transcription)

    return read_transcription(title), title