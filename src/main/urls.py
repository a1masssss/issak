from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import TextChatBotView, YoutubeChatBotView, PDFChatBotView, ArticleChatBotView,  TextView, UploadPDFView, SubmitYouTubeView, UploadPageView, GenerateFlashCardsView, ArticleView, pricing_page
from main import views
from issak.utils.views.note_views import note_edit_view, note_delete_view
from issak.utils.views.summary_views import summary_list, summary_detail

urlpatterns = [
    # navabar
    path("", UploadPageView.as_view(), name="upload_page"), #upload_page
    path('summary_list', summary_list,  name = 'notes'),
    path('pricing', pricing_page, name = 'pricing_page'),
    path('summary/<uuid:summary_id>/', summary_detail, name = 'summary_detail'), 

    
    # upload content
    path("upload_pdf", UploadPDFView.as_view(), name="upload_file"),
    path("submit_youtube", SubmitYouTubeView.as_view(), name="submit_youtube"),
    path("submit_text", TextView.as_view(), name="submit_text"),
    path('submit_article', ArticleView.as_view(), name = 'submit_article'), 
    
    # chat-bots
    path("pdf-chat/", PDFChatBotView.as_view(), name="pdf_chat"),
    path("youtube-chat/", YoutubeChatBotView.as_view(), name = 'youtube_chat'),
    path('plain-text/', TextChatBotView.as_view(), name = 'plain_text'),
    path('article-chat/', ArticleChatBotView.as_view(), name= 'article_chat'),  


    # flashcards
    path("generate_flashcards/<str:source>/", GenerateFlashCardsView.as_view(), name="generate_flashcards"),



    # edit
    path("edit/<uuid:pk>/", note_edit_view, name = "edit_view"),
    path("delete/<uuid:pk>/", note_delete_view, name = "delete_view"),


]

# Добавляем поддержку раздачи загруженных файлов (например, PDF)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
