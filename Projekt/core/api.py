from typing import List
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, logout as django_logout
from .models import Tweet, Comment, Hashtag, Profile, Like, Notification
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

api = NinjaAPI(csrf=True)

class ProfileSchema(Schema):
    username: str
    bio: str
    location: str
    website: str
    profile_picture_url: str
    created_at: str

    @staticmethod
    def resolve_username(obj: Profile):
        return obj.user.username

    @staticmethod
    def resolve_profile_picture_url(obj: Profile):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None
    
    @staticmethod
    def resolve_created_at(obj: Profile):
        return obj.created_at.isoformat()

class TweetSchema(Schema):
    id: int
    content: str
    author: ProfileSchema
    created_at: str
    likes_count: int
    comments_count: int

    @staticmethod
    def resolve_author(obj: Tweet):
        user = User.objects.get(id=obj.author.id)
        return Profile.objects.get(user=user)

    @staticmethod
    def resolve_created_at(obj: Tweet):
        return obj.created_at.isoformat()


class CommentSchema(Schema):
    id: int
    content: str
    author: ProfileSchema
    tweet_id: int
    created_at: str

    @staticmethod
    def resolve_author(obj: Comment):
        user = User.objects.get(id=obj.author.id)
        return Profile.objects.get(user=user)

    @staticmethod
    def resolve_tweet_id(obj: Comment):
        return obj.tweet.id

    @staticmethod
    def resolve_created_at(obj: Comment):
        return obj.created_at.isoformat()

class HashtagSchema(Schema):
    id: int
    name: str
    tweets_count: int

class TweetInSchema(Schema):
    content: str

class CommentInSchema(Schema):
    content: str

class LoginSchema(Schema):
    username: str
    password: str

@api.get("/auth", auth=None)
def auth(request):
    if request.user.is_authenticated:
        return {"authenticated": True, "user": request.user.username}
    return {"authenticated": False}

@api.post("/auth/login", auth=None)
def login(request, payload: LoginSchema):
    user = User.objects.filter(username=payload.username).first()
    if user and user.check_password(payload.password):
        django_login(request, user)
        return {"success": True}
    return HttpError(401, "Invalid credentials")

@api.post("/auth/logout", auth=None)
def logout(request):
    if request.user.is_authenticated:
        django_logout(request)
        return {"success": True}
    return HttpError(401, "Not authenticated")

# Tweets
@api.get("/tweets", response=List[TweetSchema])
def list_tweets(request):
    """
    Returns a list of all tweets.
    """
    return Tweet.objects.all()

@api.get("/tweets/{tweet_id}", response=TweetSchema)
def get_tweet(request, tweet_id: int):
    """
    Returns a single tweet by its ID.
    """
    return get_object_or_404(Tweet, id=tweet_id)

@api.post("/tweets", response=TweetSchema)
def create_tweet(request, payload: TweetInSchema):
    """
    Creates a new tweet.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    tweet = Tweet.objects.create(author=request.user, content=payload.content)
    tweet.extract_hashtags()
    return tweet

@api.delete("/tweets/{tweet_id}")
def delete_tweet(request, tweet_id: int):
    """
    Deletes a tweet by its ID.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if tweet.author != request.user:
        raise HttpError(403, "You do not have permission to delete this tweet")
    tweet.delete()
    return JsonResponse({"success": True})

# Comments
@api.get("/tweets/{tweet_id}/comments", response=List[CommentSchema])
def list_tweet_comments(request, tweet_id: int):
    """
    Returns a list of comments for a specific tweet.
    """
    tweet = get_object_or_404(Tweet, id=tweet_id)
    return tweet.comments.all()

@api.post("/tweets/{tweet_id}/comments", response=CommentSchema)
def create_comment(request, tweet_id: int, payload: CommentInSchema):
    """
    Creates a new comment on a tweet.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comment = Comment.objects.create(tweet=tweet, author=request.user, content=payload.content)
    return comment

@api.delete("/comments/{comment_id}")
def delete_comment(request, comment_id: int):
    """
    Deletes a comment by its ID.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        raise HttpError(403, "You do not have permission to delete this comment")
    comment.delete()
    return JsonResponse({"success": True})

# Likes
@api.post("/tweets/{tweet_id}/like", response=TweetSchema)
def like_tweet_toggle(request, tweet_id: int):
    """
    Likes a tweet.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    tweet = get_object_or_404(Tweet, id=tweet_id)
    like = Like.objects.filter(user=request.user, tweet=tweet).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, tweet=tweet)
    return tweet

@api.post("/comments/{comment_id}/like", response=CommentSchema)
def like_comment_toggle(request, comment_id: int):
    """
    Likes a comment.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    comment = get_object_or_404(Comment, id=comment_id)
    like = Like.objects.filter(user=request.user, comment=comment).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, comment=comment)
    return comment

# Users
@api.get("/users/@{username}", response=ProfileSchema)
def get_user_profile(request, username: str):
    """
    Returns the profile for a specific user.
    """
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Profile, user=user)

@api.get("/users/me", response=ProfileSchema)
def get_current_user_profile(request):
    """
    Returns the profile of the currently authenticated user.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    user = request.user
    return get_object_or_404(Profile, user=user)


@api.get("/hashtags", response=List[HashtagSchema])
def list_hashtags(request):
    """
    Returns a list of all hashtags.
    """
    return Hashtag.objects.all()

@api.get("/hashtags/{hashtag_name}", response=List[TweetSchema])
def get_hashtag_tweets(request, hashtag_name: str):
    """
    Returns tweets associated with a specific hashtag.
    """
    hashtag = get_object_or_404(Hashtag, name=hashtag_name)
    return hashtag.tweets.all()
