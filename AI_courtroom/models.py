from django.db import models
from User_Profile.models import User, Case

class Courtroom(models.Model):
    SPEAKER_CHOICES = [
        ('Petitioner', 'Petitioner'),
        ('Defendant', 'Defendant'),
        ('AI', 'AI'),
    ]

    case = models.OneToOneField(Case, related_name='courtroom', on_delete=models.CASCADE)
    current_speaker = models.CharField(max_length=50, choices=SPEAKER_CHOICES, default='AI')
    chat_history = models.ManyToManyField('ChatHistory', related_name='courtrooms', blank=True)

    def __str__(self):
        return f"Courtroom for Case {self.case.id}"

    def get_chat_history(self):
        # Filter ChatHistory objects by courtroom id and order by timestamp
        chat_history = ChatHistory.objects.filter(courtroom_id=self.id).order_by('timestamp')
        
        # Format chat history into a list of dictionaries
        chats = []
        for chat in chat_history:
            chats.append({
                'sender_username': chat.sender.username if chat.sender else "AI",
                'sender_role': chat.sender_role,
                'message': chat.message,
                'timestamp': chat.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
        return chats

class ChatHistory(models.Model):
    SENDER_CHOICES = [
        ('Petitioner', 'Petitioner'),
        ('Defendant', 'Defendant'),
        ('AI', 'AI'),
    ]

    courtroom = models.ForeignKey(Courtroom, related_name='chats', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sender_user', on_delete=models.CASCADE, blank=True, null=True)
    sender_role = models.CharField(max_length=50, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Chat in Courtroom {self.courtroom.id} by {self.sender} at {self.timestamp}"

class LLMModel(models.Model):
    OPTIONS = (
    ('tiny-llama-chat-gguf', 'tiny-llama-chat-gguf'),
    ('bling-1b', 'bling-1b'),
    ('bling-falcon-1.3b', 'bling-falcon-1.3b'),
    ('bling-sheared-llama-1.3b', 'bling-sheared-llama-1.3b'),
    ('bling-red-pajamas-3b', 'bling-red-pajamas-3b'),
    ('bling-sheared-llama-2.7b', 'bling-sheared-llama-2.7b'),
    ('bling-stablelm-3b', 'bling-stablelm-3b'),
    ('bling-cerebras-1.3b', 'bling-cerebras-1.3b'),
    ('bling-tiny-llama-1b', 'bling-tiny-llama-1b'),
    ('dragon-yi-6b', 'dragon-yi-6b'),
    ('dragon-stablelm-7b', 'dragon-stablelm-7b'),
    ('dragon-mistral-7b', 'dragon-mistral-7b'),
    ('dragon-red-pajama-7b', 'dragon-red-pajama-7b'),
    ('dragon-deci-6b', 'dragon-deci-6b'),
    ('dragon-falcon-7b', 'dragon-falcon-7b'),
    ('dragon-llama-7b', 'dragon-llama-7b'),
    ('dragon-deci-7b', 'dragon-deci-7b'),
    ('bling-phi-3', 'bling-phi-3'),
    ('bling-phi-3-gguf', 'bling-phi-3-gguf'),
)


    text_option = models.CharField(max_length=50, choices=OPTIONS)

    def __str__(self):
        return self.text_option