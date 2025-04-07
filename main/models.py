from django.db import models
import uuid
from django.conf import settings

class PDFDocument(models.Model):
    file = models.FileField(upload_to='uploads/pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'pdf')

    def __str__(self):
        return f"PDF {self.id}"


class Video(models.Model):
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'video')

    def __str__(self):
        return f"Video {self.id} - {self.url}"


class Text(models.Model):
    text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'text')

    def __str__(self):
        return f"Text {self.id}"


class Article(models.Model):
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'article')
    

    def __str__(self):
        return f"Article url {self.url}"
    
class SummaryNotes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255) 
    content = models.TextField()
    image_url = models.URLField(max_length = 500, null=True, blank=True)
    source_url = models.URLField(blank=True, null=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title