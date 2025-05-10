from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Follow, Notification, Like, Comment

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

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """
    Vytvoří notifikaci o novém lajku.
    """
    if created:
        Notification.objects.create(
            recipient=instance.comment.author if instance.comment else instance.tweet.author,
            sender=instance.user,
            notification_type='like',
            tweet=instance.tweet if instance.tweet else None,
            comment=instance.comment if instance.comment else None
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """
    Vytvoří notifikaci o novém komentáři.
    """
    if created:
        Notification.objects.create(
            recipient=instance.tweet.author,
            sender=instance.author,
            notification_type='comment',
            tweet=instance.tweet
        )