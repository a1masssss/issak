from django.shortcuts import get_object_or_404, render
from main.models import SummaryNotes


def summary_list(request):
    SORT_OPTIONS = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'text': 'Text',
        'file': 'File',
        'youtube': 'YouTube',
        'article': 'Article'
    }
    
    # Get sort parameter with 'newest' as default
    sort_by = request.GET.get('sort', 'newest').lower()
    
    # Filter by user first
    summaries = SummaryNotes.objects.filter(user=request.user)
    
    # Apply sorting/filtering based on the option
    if sort_by in ['newest', 'oldest']:
        summaries = summaries.order_by(SORT_OPTIONS[sort_by])
    elif sort_by in SORT_OPTIONS:
        summaries = summaries.filter(content_type=SORT_OPTIONS[sort_by])
    
    return render(request, 'summarizer/notes.html', {
        'summaries': summaries,
        'current_sort': sort_by,
        'sort_options': SORT_OPTIONS.keys()
    })
# @cache_page(60 * 60 * 2)  # 2hr
def summary_detail(request, summary_id):
    summary_obj = get_object_or_404(SummaryNotes, id=summary_id)
    summary_text = summary_obj.content
    summary_type = summary_obj.content_type

    if summary_type == "Article":
        return render(
            request,
            "summarizer/detail_article.html",
            {
                "summary": summary_text,
            },
        )
    elif summary_type == "Text":
        return render(
            request,
            "summarizer/detail_text.html",
            {
                "summary": summary_text,
            },
        )
    
    elif summary_type == "YouTube":
        return render(
            request,
            "summarizer/detail_youtube.html",
            {
                "summary": summary_text,
            },
        )
    
    else:
        return render(
            request,
            "summarizer/detail_pdf.html",
            {
                "summary": summary_text,
            },
        )