import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import os 



def get_youtube_transcript(video_url:str) -> dict:
    try:
        cookie_file = os.getenv("YOUTUBE_COOKIE_FILE")
        ydl_opts = {'quiet': True,
                    'cookiefile': cookie_file,
                    }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        video_id = info['id']
        title = info['title']
        thumbnail_url = info['thumbnail']

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
        return {"error": f"Error while fetching video: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}