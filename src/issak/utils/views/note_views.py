from django.shortcuts import get_object_or_404, redirect, render

from main.forms import SummaryForm
from main.models import SummaryNotes


def note_edit_view(request, pk):
    obj = get_object_or_404(SummaryNotes, pk=pk)
    if request.method == "POST":
        form = SummaryForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            return redirect("summary_detail", summary_id=obj.id)
    else:
        form = SummaryForm(instance=obj)

    return render(request, 'summarizer/edit.html', {'form': form})

def note_delete_view(request, pk):
    note = get_object_or_404(SummaryNotes, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("/main/summary_list")
    return redirect("/notes")
