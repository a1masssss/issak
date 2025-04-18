import os
import tempfile
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(video_url: str) -> dict:
    try:
        cookie_path = os.getenv('YOUTUBE_COOKIES_FILE', 'cookies.txt') 
        ydl_opts = {
            'quiet': True,
            'verbose': True,
            'skip_download': True,
            'cookiefile': cookie_path,
            'cache_dir': tempfile.gettempdir(),  # make sure yt-dlp doesn’t try writing elsewhere
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
            except Exception as e:
                return {"error": f"yt-dlp failed: {str(e)}"}

        video_id = info.get('id', '')
        title = info.get('title', '')
        thumbnail_url = info.get('thumbnail', '')

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ru'])
            full_transcript = " ".join(entry['text'] for entry in transcript)

            # 💡 Limit for OpenAI input on low-RAM plans
            max_length = 2000
            full_transcript = full_transcript[:max_length]

        except Exception as e:
            return {"error": f"Transcript error: {str(e)}"}

        return {
            "transcript": full_transcript,
            "image_url": thumbnail_url,
            "youtube_title": title,
        }

    except yt_dlp.utils.DownloadError as e:
        return {"error": f"yt-dlp download error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
