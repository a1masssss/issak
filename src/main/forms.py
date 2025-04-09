from django import forms
from .models import SummaryNotes


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.label = ''


class PDFUploadForm(BaseForm):
    file = forms.FileField(
        label="Select a PDF file",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf, .docx, .csv, .json, .xlsx"})
        
    )

class YouTubeForm(BaseForm):
    url = forms.URLField(
        label="YouTube URL",
        widget=forms.URLInput(attrs={"placeholder": "https://www.youtube.com/watch?v=..."})
    )
class TextForm(BaseForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Enter text here"}), 
    )
    

class ArticleForm(BaseForm):
    url = forms.URLField(
        label= "Article URL", 
        widget=forms.URLInput(attrs={"placeholder": 'https://link-to-your-article'})
    )
        


class SummaryForm(forms.ModelForm):
    class Meta:
        model = SummaryNotes
        fields = ['title', 'content',]
