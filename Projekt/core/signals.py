from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Follow, Notification

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Vytvoří profil po registraci uživatele.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Uloží profil po aktualizaci uživatele.
    """
    instance.profile.save()

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """
    Vytvoří notifikaci o novém sledujícím.
    """
    if created:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow'
        )