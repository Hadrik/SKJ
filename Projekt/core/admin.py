from django.contrib import admin
from .models import Profile, Tweet, Hashtag, Comment, Like, Follow, Notification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'created_at', 'likes_count', 'comments_count')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'tweet', 'created_at')
    search_fields = ('author__username', 'content', 'tweet__content')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author', 'tweet')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_owner', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_type(self, obj):
        return 'Tweet' if obj.tweet else 'Comment'
    content_type.short_description = 'Type'
    
    def content_owner(self, obj):
        if obj.tweet:
            return obj.tweet.author.username
        return obj.comment.author.username
    content_owner.short_description = 'Owner'

    def content_preview(self, obj):
        if obj.tweet:
            return obj.tweet.content[:50] + ('...' if len(obj.tweet.content) > 50 else '')
        return obj.comment.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'tweet', 'comment')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('follower', 'following')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipient', 'sender', 'tweet', 'comment')