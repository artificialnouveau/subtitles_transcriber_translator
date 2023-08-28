from datetime import timedelta
import os
import whisper
from googletrans import Translator, LANGUAGES
from moviepy.editor import *
import torch
import yt_dlp
from tqdm import tqdm
import subprocess
from googletrans import Translator, LANGUAGES
import argparse

# Download the YouTube video as a video + audio
def download_youtube_video_yt_dlp(url, save_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f"{save_path}/%(title)s.%(ext)s",
        'merge_output_format': 'mp4'
    }
    info_dict = {}
    def progress_hook(d):
        nonlocal info_dict
        if d['status'] == 'finished':
            info_dict = d
    ydl_opts.update({'progress_hooks': [progress_hook]})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return info_dict.get('filename')



def transcribe_audio(input_path, srt_output_path, lang='en', whisper_model = "base"):
    model = whisper.load_model(whisper_model)
    print("Whisper model loaded.")
    
    transcribe = model.transcribe(audio=input_path, language=lang)
    segments = transcribe['segments']
    
    srt_data = ""
    
    # Initialize the tqdm progress bar
    with tqdm(total=len(segments), desc="Transcribing", ncols=100) as pbar:
        for segment in segments:
            startTime = str(timedelta(seconds=int(segment['start']))).replace(":", ",") + '000'
            endTime = str(timedelta(seconds=int(segment['end']))).replace(":", ",") + '000'
            text = segment['text']
            segmentId = segment['id'] + 1
            srt_data += f"{segmentId}\n{startTime} --> {endTime}\n{text.strip()}\n\n"
            
            # Update the progress bar
            pbar.update(1)
        
    with open(srt_output_path, 'w', encoding='utf-8') as f:
        f.write(srt_data)
    
    print(f"SRT file created at {srt_output_path}")
    
    return srt_output_path



def translate_srt(input_srt_file, src_language = 'en', target_language = 'zh-cn'):
    translator = Translator()
    translated_subtitles = []

    # Read the SRT file
    with open(input_srt_file, 'r', encoding='utf-8') as f:
        srt_data = f.readlines()

    current_subtitle = []

    for idx, line in enumerate(srt_data):
        print(f"Processing line {idx+1} ({line.strip()})")

        if line.strip() == '':
            # print("Empty line detected. Translating current subtitle.")
            joined_subtitle_text = ' '.join(current_subtitle[2:])

            # print(f"Attempting to translate: {joined_subtitle_text}")

            try:
                translated_text = translator.translate(joined_subtitle_text, src=src_language, dest=target_language).text
                print(f"Translation successful: {translated_text}")
            except IndexError:
                print(f"Failed to translate subtitle: {joined_subtitle_text}")
                translated_text = joined_subtitle_text  # Fallback to the original text

            translated_subtitles.append(current_subtitle[:2] + [translated_text, '\n'])
            current_subtitle = []
        else:
            current_subtitle.append(line.strip())

    # Write to the output SRT file
    output_srt_file = input_srt_file.replace(".srt", f"_{target_language}.srt")

    with open(output_srt_file, 'w', encoding='utf-8') as f:
        for idx, subtitle in enumerate(translated_subtitles):
            for line in subtitle[:-1]:
                f.write(f"{line}\n")
            if idx < len(translated_subtitles) - 1:
                f.write("\n")
    return output_srt_file


def convert_webm_to_mp4(webm_path):
    mp4_path = webm_path.replace(".webm", ".mp4")
    cmd = [
        "ffmpeg",
        "-i", webm_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        mp4_path
    ]
    subprocess.run(cmd)
    return mp4_path


def embed_subtitles_ffmpeg(video_path, srt_path):
    output_path = video_path.replace(".mp4", "_with_subtitles.mp4")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:v", "libx264",
        "-c:a", "copy",
        "-strict", "experimental",
        output_path
    ]
    subprocess.run(cmd)
    return output_path



# Main function
def main():
    parser = argparse.ArgumentParser(description="Video Transcription and Translation Tool")
    
    parser.add_argument('--url', help='URL of the YouTube video to download', default=None)
    parser.add_argument('--video_path', help='Path of an existing video', default=None)
    parser.add_argument('--whipser_model', help='Whisper Model Type', default="base")
    parser.add_argument('--srt_output_path', help='Path to save the transcribed SRT file', default="SrtFiles/Translated.srt")
    parser.add_argument('--src_lang', help='Source language for translation', default='en')
    parser.add_argument('--target_lang', help='Target language for translation', default='zh-cn')

    args = parser.parse_args()

    if not os.path.exists("SrtFiles"):
        os.makedirs("SrtFiles")
    if not os.path.exists("DownloadedVideos"):
        os.makedirs("DownloadedVideos")

    if args.url and not args.video_path:
        video_path = download_youtube_video_yt_dlp(args.url, "DownloadedVideos")
        print(f"Video downloaded at {video_path}")
    elif args.video_path and not args.url:
        video_path = args.video_path
    else:
        print("Either --url or --video_path should be specified, not both.")
        return
    
    srt_filename = transcribe_audio(video_path, args.srt_output_path, lang=args.src_lang, whisper_model = args.whishper_model)
    print(f"SRT file created at {srt_filename}")

    translated_srt_filename = translate_srt(srt_filename, args.src_lang, args.target_lang)
    print(f"Translated SRT file created at {translated_srt_filename}")

    # Convert WebM to MP4 if needed
    if video_path.endswith('.webm'):
        video_path = convert_webm_to_mp4(video_path)

    output_video_path = embed_subtitles_ffmpeg(video_path, translated_srt_filename)
    print(f"Video with embedded subtitles created at {output_video_path}")

if __name__ == "__main__":
    main()
