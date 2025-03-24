from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .models import PDFDocument, Video
import fitz as pymupdf
import anthropic
import openai
import yt_dlp
import os
from django.conf import settings
from .forms import PDFUploadForm, TextForm, YouTubeForm
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from anthropic import Anthropic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import json
import openai
import yt_dlp
import uuid
import os
from django.http import StreamingHttpResponse, JsonResponse
from django.views import View

# Initialize API clients
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Summarize text using Anthropic API with more detailed output
def summarize_with_anthropic(text):
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,  # Increase max tokens for more detailed summaries
        temperature=0.3,
        messages=[{"role": "user", "content": f"Provide a detailed and structured summary of the following text, preserving key details:\n\n{text}.well-structured, easy to read, and include emojis. Ensure clarity, readability, and visual appeal while keeping it effective."}]
    )
    return response.content[0].text.strip()

def transcribe_audio_openai(audio_path):
    openai.api_key = settings.OPENAI_API_KEY
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    return transcript["text"]



def extract_pdf_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])



def download_youtube_audio(youtube_url):
    unique_id = str(uuid.uuid4())
    ydl_opts = {
        'format': 'bestaudio/best',
        # Use '%(ext)s' to let yt-dlp pick the initial extension,
        # then have ffmpeg rename it to ".mp3" via postprocessor.
        'outtmpl': f'audio_{unique_id}.%(ext)s',
        'noplaylist': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)

        # After postprocessing, the final filename is stored here:
        final_filename = info_dict["requested_downloads"][0]["filepath"]
        return final_filename



class UploadPDFView(View):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")  # Get the uploaded file
        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        file_name = default_storage.save(f"uploads/pdfs/{file.name}", ContentFile(file.read()))

        # Save to database
        pdf_doc = PDFDocument(file=file_name)
        pdf_doc.save()

        # Extract text and generate summary
        text = extract_pdf_text(pdf_doc.file.path)
        
        # Store the full text in session for chat functionality
        request.session['pdf_text'] = text
        
        summary = summarize_with_anthropic(text[:800000])

        return render(self.request, 'summarizer/detail_pdf.html', {'pdf_name': file_name, 'summary': summary})
class SubmitYouTubeView(FormView):
    template_name = "summarizer/upload.html"
    form_class = YouTubeForm
    success_url = reverse_lazy("submit_youtube")

    def form_valid(self, form):
        youtube_url = form.cleaned_data["url"]
        video = Video(url=youtube_url)
        video.save()

        audio_path = download_youtube_audio(youtube_url)
        full_text = transcribe_audio_openai(audio_path)  # Extract full content
        summary = summarize_with_anthropic(full_text[:800000])  # Increased limit

        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return render(self.request, 'summarizer/detail_youtube.html', {
            'youtube_url': youtube_url, 
            'summary': summary


        })

class TextFormView(FormView):
    template_name = "summarizer/upload.html"
    form_class = TextForm
    success_url = reverse_lazy("submit_text")

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        summary = summarize_with_anthropic(text[:800000]) 
        return render(self.request, 'summarizer/detail_text.html', {'summary': summary})
    


    
class UploadPageView(View):
    def get(self, request):
        return render(request, "summarizer/upload.html", {
            "pdf_form": PDFUploadForm(),
            "youtube_form": YouTubeForm(), 
            "text_form": TextForm()
        })
    



class ChatBotView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse incoming JSON request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)
            
            # Get stored PDF text
            pdf_text = request.session.get("pdf_text", "")
            if not pdf_text:
                return JsonResponse({
                    "response": "No transcript found in session"
                }, status=400)

            # Debug: Log the received message
            logger.info(f"Received user message: {user_message}")

            # Construct prompt for OpenAI
            prompt = f"""
            You are an AI assistant helping a user understand a text.
            Text:
            {pdf_text[:10000]}  # Limit to 10,000 chars for OpenAI request

            The user asks:
            {user_message}

            Please answer based ONLY on the text above.
            """

            # Debug: Log the constructed prompt
            logger.info(f"Generated prompt: {prompt[:200]}...")  # Log the first 200 chars

            def event_stream():
                try:
                    response_iter = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        stream=True     
                    )

                    for chunk in response_iter:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            text_piece = delta["content"]
                            yield f"data: {text_piece}\n\n"

                except Exception as e:
                    logger.error(f"Streaming error: {str(e)}")
                    yield f"data: [Error: {str(e)}]\n\n"

            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
        except openai.error.AuthenticationError:
            logger.error("Invalid OpenAI API key")
            return JsonResponse({"error": "OpenAI API authentication failed"}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)