from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Case, ChatHistory
from django.utils import timezone
from django.shortcuts import render
from .models import Courtroom
from llmware.models import ModelCatalog
import os

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

def verdict_view(request, courtroom_id):
    # Fetch the courtroom object corresponding to the provided courtroom_id
    courtroom = Courtroom.objects.get(id=courtroom_id)

    # Call get_chat_history on the courtroom object to retrieve the chat history
    chat_history = courtroom.get_chat_history()

    # Prepare the query to the model
    model = ModelCatalog().load_model("tiny-llama-chat-gguf", temperature=0.0, sample=True)
    query = '''As an Expert Judge, your ultimate task is to give a proper formal verdict. Based on the provided case details below, give a final verdict in the format:

     [Final Verdict: (Guilty/Not Guilty Defendant), Insert your final decision here, including any reasoning or justification for your ruling.]

    Case Details_Format:
        # 'chats' contains a list of chat messages within the corresponding courtroom.
        'chats': {}'''.format(chat_history)
    
    # Additional context
    context = '''In India, the process of judicial decision-making is an intricate interplay of legal doctrines, constitutional principles, statutory enactments, and judicial precedents, all orchestrated to achieve the ultimate goal of justice. Judges, seated as the guardians of the law, meticulously navigate through this labyrinthine legal landscape, weighing evidence, scrutinizing arguments, and interpreting laws to render impartial and equitable judgments. At the heart of this process lies the Constitution of India, serving as the supreme legal document that not only delineates the powers and functions of the judiciary but also enshrines fundamental rights and principles that guide judicial deliberations. Within the courtroom, the adversarial system unfolds, with opposing parties engaging in legal combat before a neutral arbiter—the judge. Armed with legal expertise and a keen understanding of the law, judges preside over proceedings, ensuring procedural fairness, and adjudicating disputes with unwavering fidelity to the rule of law.

    Key legal principles, such as the doctrine of precedent, shape judicial decision-making, requiring judges to adhere to prior judicial rulings and established legal principles. This principle of stare decisis fosters consistency and coherence in the application of law, ensuring predictability and stability in the legal system. Moreover, judges engage in statutory interpretation, delving into the legislative intent behind enactments to discern the law's true meaning and effect. Laws such as the Indian Penal Code, Criminal Procedure Code, and Civil Procedure Code form the bedrock of legal adjudication, providing the substantive and procedural framework for addressing civil and criminal disputes.

    In criminal proceedings, the presumption of innocence stands as a cornerstone, placing the burden of proof squarely on the prosecution to establish guilt beyond a reasonable doubt. The Indian Evidence Act governs the admissibility and evaluation of evidence, ensuring that trials are conducted fairly and defendants' rights are safeguarded. Furthermore, judges exercise judicial discretion judiciously, balancing legal principles with equitable considerations to achieve just outcomes. This discretion extends to granting equitable relief in civil disputes, where courts have the authority to issue injunctions, order specific performance, or provide restitution to prevent injustice and ensure fairness.

    Crucially, the independence of the judiciary ensures that judges adjudicate cases free from external influence or bias, upholding the principles of impartiality and judicial integrity. Judicial ethics and professionalism further underscore the judiciary's commitment to upholding the rule of law, fostering public trust in the administration of justice. Ultimately, the process of judicial decision-making in India is a solemn undertaking, guided by legal expertise, ethical principles, and a steadfast commitment to justice, ensuring that the rights and liberties of individuals are protected and justice is served.'''

    # Get the model's response
    response = model.inference(query, add_context=context)
    
    # Extract the 'llm_response' from the model's response dictionary
    llm_response = response.get('llm_response')
    case = courtroom.case
    case.status = 'completed'
    case.verdict = llm_response
    case.save()

    # Render the result in an HTML template
    return render(request, 'final_verdict.html', {'llm_response': llm_response})
