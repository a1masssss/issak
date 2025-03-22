from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ChatBotView, TextFormView, UploadPDFView, SubmitYouTubeView, UploadPageView

urlpatterns = [
    path("", UploadPageView.as_view(), name="upload_page"),
    path("upload_pdf/", UploadPDFView.as_view(), name="upload_file"),
    path("submit_youtube/", SubmitYouTubeView.as_view(), name="submit_youtube"),
    path("submit_text/", TextFormView.as_view(), name="submit_text"),
    path("chat/", ChatBotView.as_view(), name="chatbot"),
]


# Добавляем поддержку раздачи загруженных файлов (например, PDF)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
