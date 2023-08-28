# Subtitles Transcription and Translation Tool

This script allows you to download a YouTube video, transcribe it (using Whisper AI), translate the transcription into a different language, and then embed the translated subtitles into the video.

## Requirements

1. Python 3.x
2. Install required Python packages:
    ```
    pip install whisper googletrans moviepy yt-dlp tqdm
    ```
3. FFmpeg installed (used for video conversions)

## How to Run

### Command-Line Arguments

The script accepts several command-line arguments for customization:

- `--url`: URL of the YouTube video to download
- `--video_path`: Path of an existing video
- `--whisper_model`: Whisper model, by default it is 'base'
- `--srt_output_path`: Path to save the transcribed SRT file (default is `SrtFiles/Translated.srt`)
- `--src_lang`: Source language for translation (default is `en`)
- `--target_lang`: Target language for translation (default is `zh-cn`)

You can use either `--url` to download a YouTube video or `--video_path` to use an existing video file, but not both.

### Usage Examples

1. To download a YouTube video, transcribe, translate and embed subtitles:

    ```bash
    python your_script.py --url https://www.youtube.com/watch?v=AC2J9CkTKBo
    ```

2. To use an existing video file, transcribe, translate and embed subtitles:

    ```bash
    python your_script.py --video_path /path/to/existing/video.mp4
    ```

3. To specify other optional parameters:

    ```bash
    python your_script.py --url https://www.youtube.com/watch?v=AC2J9CkTKBo --whisper_model "base" --srt_output_path my_srt.srt --src_lang en --target_lang es
    ```

### Output

The script will produce an MP4 video with embedded subtitles in the target language.
