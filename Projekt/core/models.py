from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    """
    Rozsireni User modelu
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    website = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})
    
    @property
    def followers_count(self):
        return self.user.followers.count()
    
    @property
    def following_count(self):
        return self.user.following.count()
    
class Tweet(models.Model):
    """
    Model pro tweety
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    content = models.TextField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='tweet_images', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}..."
    
    def get_absolute_url(self):
        return reverse('tweet_detail', kwargs={'pk': self.pk})
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    def extract_hashtags(self):
        import re
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, self.content)
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
            self.hashtags.add(hashtag)
    
class Comment(models.Model):
    """
    Model pro komentare k tweetum
    """
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username}: {self.content[:20]}..."
    
class Like(models.Model):
    """
    Model pro lajky
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Like je k tweetu nebo komentari, ne k obojim
            models.CheckConstraint(
                check=(
                    models.Q(tweet__isnull=False, comment__isnull=True) |
                    models.Q(tweet__isnull=True, comment__isnull=False)
                ),
                name='valid_like'
            ),
            # tweet nebo komentar muze byt userem likenuty jenom jednou
            models.UniqueConstraint(
                fields=['user', 'tweet'],
                name='unique_tweet_like',
                condition=models.Q(tweet__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_like',
                condition=models.Q(comment__isnull=False)
            ),
        ]

    def __str__(self):
        if self.tweet:
            return f"{self.user.username} liked tweet {self.tweet.author.username}"
        else:
            return f"{self.user.username} liked comment {self.comment.author.username}"
    
class Hashtag(models.Model):
    """
    Model pro hashtagy
    """
    name = models.CharField(max_length=30, unique=True)
    tweets = models.ManyToManyField(Tweet, related_name='hashtags', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"
    
    def get_absolute_url(self):
        return reverse('hashtag_tweets', kwargs={'name': self.name})
    
    @property
    def tweets_count(self):
        return self.tweets.count()
    
class Follow(models.Model):
    """
    Model pro sledovani uzivatelu
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # user muze sledovat nekoho jenom jednou
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follow'
            ),
            # user nemuze followovat sam sebe
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_follow'
            ),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
class Notification(models.Model):
    """
    Model pro oznameni
    """
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        if self.notification_type == 'like' and self.tweet:
            return f"{self.sender.username} liked your tweet"
        if self.notification_type == 'like' and self.comment:
            return f"{self.sender.username} liked your comment"
        elif self.notification_type == 'comment':
            return f"{self.sender.username} commented on your tweet"
        elif self.notification_type == 'follow':
            return f"{self.sender.username} started following you"
        else:
            return "Notification"
