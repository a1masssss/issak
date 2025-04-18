import json
import openai


from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from issak.utils.extractors.article_parcer import parse_article
from issak.utils.extractors.pdf_extractor import extract_pdf_text
from issak.utils.extractors.youtube_extractor import get_youtube_transcript

from .models import PDFDocument, SummaryNotes, Video
from .forms import PDFUploadForm, TextForm, YouTubeForm, ArticleForm
from main.serializers import FlashcardSerializer



from issak.utils.summarizers.openai_summarize import summarize_with_openai
from issak.utils.generators.generate_title import generate_title_from_text
from issak.utils.generators.generate_stream import generate_stream_response
from issak.utils.generators.generate_flashcards import generate_flashcards_from_summary


# class based views
class UploadPageView(View):
    def get(self, request):
        return render(request, "summarizer/upload.html", {
            "pdf_form": PDFUploadForm(),
            "youtube_form": YouTubeForm(), 
            "text_form": TextForm(),
            "article_form": ArticleForm()
        })

# @method_decorator(cache_page(60 * 60 * 2), name="post") #2hr

class UploadPDFView(View):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")  
        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        file_name = default_storage.save(f"uploads/pdfs/{file.name}", ContentFile(file.read()))
        pdf_doc = PDFDocument(file=file_name, user = request.user)
        pdf_doc.save()

        
        text = extract_pdf_text(pdf_doc.file.path)
        pdf_title = generate_title_from_text(text[:1000]) 
        summary = summarize_with_openai(text)

        request.session['pdf_text'] = text

        if summary:
            self.save_to_db(pdf_title, summary, file_name)

        messages.success(request, "Note successfully saved to AI Notes")

        return render(self.request, 'summarizer/detail_pdf.html', {'pdf_name': file_name, 'summary': summary})
    
    def save_to_db(self, pdf_title, summary, source_url):
        SummaryNotes.objects.create(
            user = self.request.user, 
            title = pdf_title, 
            content = summary, 
            source_url = source_url,
            content_type = 'File'
        )
    
# @method_decorator(cache_page(60 * 60 * 2), name="form_valid") #2hr
class SubmitYouTubeView(FormView):
    template_name = "summarizer/upload.html"
    form_class = YouTubeForm
    success_url = reverse_lazy("submit_youtube")

    def form_valid(self, form):
        youtube_url = form.cleaned_data["url"]
        video = Video(url=youtube_url, user = self.request.user)
        video.save()
        full_text = get_youtube_transcript(youtube_url) 
        summary = summarize_with_openai(full_text)
        yt_content = full_text.get('transcript', '')
        yt_title = full_text.get('youtube_title', '')
        yt_image = full_text.get('image_url', '')
        print(len(yt_content))
        print("*" * 100)

        self.request.session['youtube_text'] = yt_content 



        if summary.strip():
            self.save_to_db(yt_title, yt_image, summary, youtube_url)

        messages.success(self.request, "Note saved to AI Notes")

        return render(self.request, 'summarizer/detail_youtube.html', {
            'youtube_url': youtube_url, 
            'summary': summary, 
            'yt_image': yt_image,
        })
    
    def save_to_db(self, yt_title, yt_image, summary, source_url):
        SummaryNotes.objects.create(
            user=self.request.user,
            title = yt_title, 
            image_url = yt_image,
            content = summary, 
            source_url = source_url, 
            content_type = 'YouTube'
        )
# @method_decorator(cache_page(60 * 60 * 2), name="form_valid") #2h

class TextView(FormView):
    template_name = "summarizer/upload.html"
    form_class = TextForm
    success_url = reverse_lazy("submit_text")

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        summary = summarize_with_openai(text[:800000])
        self.request.session['plain_text'] = text


        if summary.strip():
            title = generate_title_from_text(text[:1000])
            self.save_to_db(title, summary)

        messages.success(self.request, "Note saved to AI Notes")

        return render(self.request, 'summarizer/detail_text.html', {
            'summary': summary, 
            })

    def save_to_db(self, title, summary):
        SummaryNotes.objects.create(
            user=self.request.user,
            title=title,
            content=summary,
            source_url='No Url', 
            content_type = 'Text'
        )


class ArticleView(FormView):
    template_name = 'summarizer/upload.html'
    form_class = ArticleForm 
    success_url = reverse_lazy('submit_article')

    def form_valid(self, form):
        article_url  = form.cleaned_data['url']
        # article = Article(url=article_url)
        text = parse_article(article_url)
        article_title = text.get('title', 'Untitled')
        article_text = text.get('content', '')[:120000]
        article_img = text.get('top_image', '')
        print(len(article_text))
        summary = summarize_with_openai(article_text)
        print(article_text)


        self.request.session['article_text'] = text

        if summary.strip():
            self.save_to_db(article_title, article_url, summary, article_img)

        messages.success(self.request, "Note saved to AI Notes")

        return render(self.request, 'summarizer/detail_article.html', {
            'article_url': article_url, 
            'summary': summary,  
            'article_title': article_title,
            'article_img': article_img,
        })
    

    def save_to_db(self, article_title, article_url, summary, image_url):
        SummaryNotes.objects.create(
            user=self.request.user,
            title = article_title, 
            content = summary, 
            source_url = article_url, 
            image_url = image_url,
            content_type = 'Article'
        )


class PDFChatBotView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse incoming JSON request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)
            

            pdf_text = request.session.get("pdf_text", "")
            if not pdf_text:
                return JsonResponse({"response": "No transcript found in session"}, status=400)

            # Construct prompt for OpenAI
            prompt = f"""
            You are an AI assistant helping a user understand a this PDF document.
            Text:
            {pdf_text}

            The user asks:
            {user_message}

            Please answer simply and briefly in 3–5 sentences.
            Respond in the same language as the provided text.
            Answer only based on the article text above.

            Please answer based ONLY on the PDF content above.
            """

            return StreamingHttpResponse(generate_stream_response(prompt), content_type='text/event-stream')

        except json.JSONDecodeError:

            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
        except openai.error.AuthenticationError:

            return JsonResponse({"error": "OpenAI API authentication failed"}, status=500)
        except Exception as e:

            return JsonResponse({"error": "An unexpected error occurred"}, status=500)
class YoutubeChatBotView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error":"user message can't be empty"}, status = 400)
        
        youtube_text = request.session.get('youtube_text', '')
        if not youtube_text:
            return JsonResponse({"error": "no youtube transctipt found in session"}, status=400)

        prompt = f"""
        You are an AI assistant helping a user understand a youtube video transcript.
        Text:
        {youtube_text[:10000]}  

        The user asks:
        {user_message}

        Please answer simply and briefly in 3–5 sentences.
        Respond in the same language as the provided text.
        Answer only based on the article text above.

        Please answer based ONLY on the content above.
        """

        return StreamingHttpResponse(generate_stream_response(prompt), content_type='text/event-stream')   
class TextChatBotView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error":"user message can't be empty"}, status = 400)
        
        plain_text = request.session.get('plain_text', '')
        if not plain_text:
            return JsonResponse({"error": "no text found in session"}, status=400)
        


        prompt = f"""
        You are an AI assistant helping a user understand a plain text.
        Text:
        {plain_text[:10000]}  # Limit to 10,000 chars for OpenAI request

        The user asks:
        {user_message}

        Please answer simply and briefly in 3–5 sentences.
        Respond in the same language as the provided text.
        Answer only based on the article text above.


        Please answer based ONLY on the text above.
        """


        return StreamingHttpResponse(generate_stream_response(prompt), content_type='text/event-stream')
class ArticleChatBotView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user_message = data.get("message", '').strip()
        if not user_message:
            return JsonResponse({"error: Message can't be empty"}, status = 400)
        
        article_text = request.session.get("article_text", "")

        if not article_text:
            return JsonResponse({"error: no article text found in session"}, status = 400)
        
        prompt = f"""
        You are an AI assistant helping a user understand content from article.
        Text:
        {article_text}

        The user asks:
        {user_message}

        Please answer simply and briefly in 3–5 sentences.
        Respond in the same language as the provided text.
        Answer only based on the article text above.

        Please answer based ONLY on the text above.
        """
        return StreamingHttpResponse(generate_stream_response(prompt), content_type= "text/event-stream")
    



class GenerateFlashCardsView(View):
    def get(self, request, source=None, *args, **kwargs):
        valid_sources = ['plain_text', 'youtube_text', 'article_text', 'pdf_text']
        if source not in valid_sources:
            return JsonResponse({'error': f'Invalid source "{source}"'}, status=400)

        summary = request.session.get(source)
        if not summary:
            return JsonResponse({'error': f'No summary found in session for "{source}"'}, status=400)

        try:
            raw_data = generate_flashcards_from_summary(summary)
            serializer = FlashcardSerializer(data=raw_data, many=True)
            serializer.is_valid(raise_exception=True)
            return JsonResponse({'flashcards': serializer.validated_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def pricing_page(request):
    return render(request, 'other/pricing.html')