from django.db.models.signals import post_save
from django.dispatch import receiver
from AI_courtroom.models import Courtroom
from User_Profile.models import Case

@receiver(post_save, sender=Case)
def create_courtroom_for_case(sender, instance, created, **kwargs):
    if created:
        Courtroom.objects.create(case=instance, current_speaker='AI')
