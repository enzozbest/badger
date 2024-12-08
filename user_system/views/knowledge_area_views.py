from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from user_system.forms.knowledge_area_form import KnowledgeAreaForm
from user_system.models.knowledge_area_model import KnowledgeArea


@login_required
def add_knowledge_areas(request):
    """Allow a logged-in tutor to add their knowledge areas to their profile."""
    if not request.user.is_tutor:
        return redirect('profile')

    form = KnowledgeAreaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        subject = form.cleaned_data['subject']

        if KnowledgeArea.objects.filter(user=request.user, subject=subject).exists():
            pass
        else:
            knowledge_area = form.save(commit=False)
            knowledge_area.user = request.user
            knowledge_area.save()

        return redirect('add_knowledge_areas')

    knowledge_areas = KnowledgeArea.objects.filter(user=request.user)  # Only retrieve knowledge areas of this tutor
    existing_subjects = [area.subject for area in knowledge_areas]

    return render(request, 'add_knowledge_areas.html',
                  {'form': form, 'knowledge_areas': knowledge_areas, 'existing_subjects': existing_subjects})


@login_required
def delete_knowledge_area(request, area_id):
    """Allow a logged-in tutor to delete a previously-added knowledge area."""
    knowledge_area = get_object_or_404(KnowledgeArea, id=area_id, user=request.user)
    knowledge_area.delete()
    return redirect('add_knowledge_areas')
