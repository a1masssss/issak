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


from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

# Initialize API clients
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
openai.api_key = settings.OPENAI_API_KEY

# Summarize text using Anthropic API with more detailed output
def summarize_with_anthropic(text):
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,  # Increase max tokens for more detailed summaries
        temperature=0.3,
        messages=[{"role": "user", "content": f"Provide a detailed and structured summary of the following text, preserving key details:\n\n{text}.well-structured, easy to read, and include emojis. Ensure clarity, readability, and visual appeal while keeping it effective."}]
    )
    return response.content[0].text.strip()

# Transcribe audio using OpenAI Whisper API with full content extraction
def transcribe_audio_openai(audio_path):
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file    =audio_file
        )
    return transcript.text

# Extract text from PDF using PyMuPDF
def extract_pdf_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])

# Download audio from YouTube efficiently
def download_youtube_audio(youtube_url):
    filename = f"audio_{uuid.uuid4()}.m4a"  # Use m4a to avoid extra conversion
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': filename,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return filename

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
        summary = summarize_with_anthropic(text[:800000])

        return render(self.request, 'summarizer/detail_pdf.html', {'pdf_name': file_name, 'summary':summary})

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
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            # Retrieve stored PDF text
            pdf_text = request.session.get("pdf_text", "")

            # Construct AI prompt with document context
            prompt = f"""
            You are an AI assistant helping a user understand a document. Here is the extracted text from the PDF:
            
            {pdf_text[:8000]}  # Limit the context to avoid token overflow
            
            Now, answer the following user question based on the document:
            {user_message}
            """

            # Send message to Claude 3 Haiku
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=256,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            ai_reply = response.content[0].text.strip()

            # Return AI response as HTML snippet
            return JsonResponse({"response": ai_reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



