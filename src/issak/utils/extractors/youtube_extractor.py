
import yt_dlp
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import os
from googleapiclient.discovery import build
import re
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_transcript(video_url: str) -> dict:

    cookie_path = os.getenv('YOUTUBE_COOKIES_FILE')
    if os.path.exists(cookie_path):
        print(f"Cookie file exists at {cookie_path}")
        print(f"File permissions: {oct(os.stat(cookie_path).st_mode)[-3:]}")
    else:
        print(f"Cookie file not found at {cookie_path}")

    try:
        ydl_opts = {
        'quiet': True,
        'verbose': True,
        'skip_download': True,
        'cookiefile': cookie_path,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            },
        # Prevent writing to cookie file
            'no_cache_dir': True,
            'no_write_cache': True
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



def get_youtube_transcript2(video_url: str) -> dict:
    try:
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
        if not video_id_match:
            return {"error": "Invalid YouTube URL format"}
        
        video_id = video_id_match.group(1)
        
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        # Get video details
        video_response = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            return {"error": "Video not found"}
        
        video_info = video_response['items'][0]['snippet']
        title = video_info['title']
        thumbnail_url = video_info['thumbnails']['high']['url']
        
        # Get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['en', 'ru'], 
                cookies=os.getenv('YOUTUBE_COOKIES_FILE'),
                )
            full_transcript = " ".join([entry['text'] for entry in transcript])
            
            if not full_transcript:
                return {"error": "Empty transcript returned"}
        except Exception as e:
            return {"error": f"Could not retrieve transcript: {str(e)}"}
        
        return {
            "transcript": full_transcript,
            "image_url": thumbnail_url,
            "youtube_title": title,
        }
        
    except Exception as e:
        return {"error": f"API error: {str(e)}"}