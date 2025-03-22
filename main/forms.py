from django import forms


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.label = ''


class PDFUploadForm(BaseForm):
    file = forms.FileField(
        label="Select a PDF file",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf"})
        
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
    
        
