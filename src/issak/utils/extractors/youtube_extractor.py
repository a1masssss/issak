

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import os
import tempfile
import shutil

def get_youtube_transcript(video_url: str) -> dict:
    try:

        temp_dir = tempfile.mkdtemp()
        cookie_path = os.getenv('YOUTUBE_COOKIES_FILE')
        

        ydl_opts = {
            'quiet': True,
            'verbose': True,
            'skip_download': True,
            'cookiefile': cookie_path,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            },
            # These options help avoid writing to the filesystem
            'no_cache_dir': True,
            'no_write_cache': True,
            'cachedir': temp_dir,  # Use our temp directory for any needed cache
            'cookiesfrombrowser': None  # Ensure this option is not used
        }
        
        # Extract video info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        # Verify we got video info
        if not info:
            return {"error": "Failed to extract video information"}
            
        video_id = info['id']
        title = info.get('title', 'Unknown Title')
        thumbnail_url = info.get('thumbnail', '')
        
        # Get transcript - separate try block to handle transcript-specific errors
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ru'])
            full_transcript = " ".join([entry['text'] for entry in transcript])
            
            if not full_transcript:
                return {"error": "Empty transcript returned"}
        except Exception as e:
            return {"error": f"Could not retrieve transcript: {str(e)}"}
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Ignore cleanup errors
        
        # Return successful result
        return {
            "transcript": full_transcript,
            "image_url": thumbnail_url,
            "youtube_title": title,
        }
        
    except yt_dlp.utils.DownloadError as e:
        return {"error": f"Error while fetching video: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}