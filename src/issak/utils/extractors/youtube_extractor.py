import os
import shutil
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(video_url: str) -> dict:
    try:
        env_cookie_path = os.getenv('YOUTUBE_COOKIES_FILE')
        default_cookie_path = 'cookies.txt'  
        source_cookie_path = env_cookie_path if env_cookie_path else default_cookie_path

        tmp_cookie_path = '/tmp/cookies.txt'
        if not os.path.exists(tmp_cookie_path):
            try:
                shutil.copy(source_cookie_path, tmp_cookie_path)
            except PermissionError:
                return {"error": "Cannot copy cookies.txt to writable path (/tmp). Check permissions."}
            except FileNotFoundError:
                return {"error": f"Cookie file not found at {source_cookie_path}"}

        # 3. yt-dlp с указанием куки-файла
        ydl_opts = {
            'quiet': True,
            'cookiefile': tmp_cookie_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        video_id = info['id']
        title = info.get('title', '')
        thumbnail_url = info.get('thumbnail', '')

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ru'])
            full_transcript = " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            return {"error": f"Could not retrieve transcript: {str(e)}"}

        return {
            "transcript": full_transcript,
            "image_url": thumbnail_url,
            "youtube_title": title,
        }

    except yt_dlp.utils.DownloadError as e:
        return {"error": f"yt-dlp error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
