from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Case, ChatHistory
from django.utils import timezone

@login_required
def courtroom_view(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if not (request.user == case.filed_by or request.user == case.case_against):
        return redirect('home')  # Ensure only involved users can access the courtroom

    return render(request, 'AI_courtroom.html', {'case': case})

@login_required
def send_message(request, case_id):
    if request.method == 'POST':
        case = get_object_or_404(Case, id=case_id)
        sender = request.user

        message = request.POST.get('message')
        if message:
            ChatHistory.objects.create(
                courtroom=case.courtroom,
                sender=sender,
                sender_role='Petitioner' if sender == case.filed_by else 'Defendant',
                message=message,
                timestamp=timezone.now()
            )
            return redirect('courtroom_view',case_id = case_id)
    return redirect('courtroom_view',case_id = case_id)