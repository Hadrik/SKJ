from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import Profile, Tweet, Hashtag, Comment, Like, Follow, Notification
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TweetForm, CommentForm, SearchForm

def register(request):
    """
    View pro registraci nového uživatele.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Účet pro {username} byl vytvořen! Nyní se můžete přihlásit.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def timeline(request):
    """
    Hlavní timeline - zobrazuje tweety přihlášeného uživatele a uživatelů, které sleduje.
    """
    # Získat ID uživatelů, které aktuální uživatel sleduje
    following_users = request.user.following.values_list('following', flat=True)
    
    # Přidat ID aktuálního uživatele
    user_ids = list(following_users)
    user_ids.append(request.user.id)
    
    # Získat tweety pro timeline
    tweets = Tweet.objects.filter(author__id__in=user_ids).order_by('-created_at')
    
    # Formulář pro nový tweet
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()
            # Extrahovat hashtagy
            tweet.extract_hashtags()
            messages.success(request, 'Váš tweet byl úspěšně zveřejněn!')
            return redirect('timeline')
    else:
        form = TweetForm()
    
    context = {
        'tweets': tweets,
        'form': form,
    }
    return render(request, 'core/timeline.html', context)

@login_required
def profile(request, username):
    """
    Zobrazení profilu uživatele.
    """
    user = get_object_or_404(User, username=username)
    tweets = user.tweets.order_by('-created_at')
    
    # Kontrola, zda přihlášený uživatel sleduje zobrazovaného uživatele
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.following.filter(following=user).exists()
    
    context = {
        'profile_user': user,
        'tweets': tweets,
        'is_following': is_following
    }
    return render(request, 'core/profile.html', context)

@login_required
def tweet_detail(request, pk):
    """
    Detail tweetu se všemi komentáři.
    """
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all().order_by('created_at')
    
    # Kontrola, zda přihlášený uživatel dal like tomuto tweetu
    user_liked = tweet.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
    
    # Formulář pro nový komentář
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.tweet = tweet
            comment.save()
            
            # Vytvoření notifikace pro autora tweetu (pokud není přihlášený uživatel)
            if tweet.author != request.user:
                Notification.objects.create(
                    recipient=tweet.author,
                    sender=request.user,
                    notification_type='comment',
                    tweet=tweet,
                    comment=comment
                )
            
            messages.success(request, 'Váš komentář byl přidán!')
            return redirect('tweet_detail', pk=tweet.pk)
    else:
        form = CommentForm()
    
    context = {
        'tweet': tweet,
        'comments': comments,
        'form': form,
        'user_liked': user_liked
    }
    return render(request, 'core/tweet_detail.html', context)

@login_required
def tweet_delete(request, pk):
    """
    Smazání tweetu.
    """
    tweet = get_object_or_404(Tweet, pk=pk)
    
    if request.method == 'POST':
        if request.user == tweet.author:
            tweet.delete()
            messages.success(request, 'Tweet byl úspěšně smazán!')
            return redirect('timeline')
        else:
            messages.error(request, 'Nemáte oprávnění k odstranění tohoto tweetu.')
            return redirect('tweet_detail', pk=tweet.pk)
    
    context = {
        'tweet': tweet
    }
    return render(request, 'core/tweet_delete.html', context)

@login_required
def profile_update(request):
    """
    Aktualizace profilu uživatele.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Váš profil byl aktualizován!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile_edit.html', context)

@login_required
def follow_toggle(request, username):
    """
    Přepínání sledování uživatele.
    """
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        messages.warning(request, 'Nemůžete sledovat sami sebe!')
        return redirect('profile', username=username)
    
    follow_obj = Follow.objects.filter(follower=request.user, following=user_to_follow).first()
    
    if follow_obj:
        # Už sleduje - zrušit sledování
        follow_obj.delete()
        messages.info(request, f'Přestali jste sledovat {username}.')
    else:
        # Ještě nesleduje - začít sledovat
        Follow.objects.create(follower=request.user, following=user_to_follow)
        messages.success(request, f'Nyní sledujete {username}!')
    
    return redirect('profile', username=username)

@login_required
def like_toggle(request, pk, content_type):
    """
    Přepínání "líbí se" pro tweet nebo komentář.
    """
    if request.method != 'POST':
        messages.error(request, 'Neplatný požadavek!')
        return redirect(request.META.get('HTTP_REFERER', 'timeline'))
    
    if content_type not in ['tweet', 'comment']:
        messages.error(request, 'Neplatný typ obsahu!')
        return redirect(request.META.get('HTTP_REFERER', 'timeline'))
    
    if content_type == 'tweet':
        obj = get_object_or_404(Tweet, pk=pk)
        like = Like.objects.filter(user=request.user, tweet=obj).first()
    else:  # comment
        obj = get_object_or_404(Comment, pk=pk)
        like = Like.objects.filter(user=request.user, comment=obj).first()
    
    if like:
        # Už má like - odebrat
        like.delete()
    else:
        # Ještě nemá like - přidat
        if content_type == 'tweet':
            like = Like(user=request.user, tweet=obj)
            # Vytvoření notifikace pro autora tweetu (pokud není přihlášený uživatel)
            if obj.author != request.user:
                Notification.objects.create(
                    recipient=obj.author,
                    sender=request.user,
                    notification_type='like',
                    tweet=obj
                )
        else:
            like = Like(user=request.user, comment=obj)
            # Vytvoření notifikace pro autora komentáře (pokud není přihlášený uživatel)
            if obj.author != request.user:
                Notification.objects.create(
                    recipient=obj.author,
                    sender=request.user,
                    notification_type='like',
                    comment=obj
                )
        like.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'timeline'))

def search(request):
    """
    Vyhledávání tweetů, uživatelů nebo hashtagů.
    """
    results = []
    search_type = 'tweets'  # Výchozí typ vyhledávání
    
    if request.method == 'GET' and 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_type = form.cleaned_data['search_type']
            
            if search_type == 'tweets':
                results = Tweet.objects.filter(content__icontains=query).order_by('-created_at')
            elif search_type == 'users':
                results = User.objects.filter(
                    Q(username__icontains=query) | 
                    Q(profile__bio__icontains=query) |
                    Q(profile__location__icontains=query)
                )
            elif search_type == 'hashtags':
                # Odstranit # ze začátku, pokud existuje
                if query.startswith('#'):
                    query = query[1:]
                results = Hashtag.objects.filter(name__icontains=query)
    else:
        form = SearchForm()
    
    context = {
        'form': form,
        'results': results,
        'search_type': search_type,
        'query': request.GET.get('query', '')
    }
    return render(request, 'core/search_results.html', context)

@login_required
def hashtag_tweets(request, name):
    """
    Zobrazení tweetů s konkrétním hashtagem.
    """
    hashtag = get_object_or_404(Hashtag, name=name)
    tweets = hashtag.tweets.order_by('-created_at')
    
    context = {
        'hashtag': hashtag,
        'tweets': tweets
    }
    return render(request, 'core/hashtag_tweets.html', context)

@login_required
def notifications(request):
    """
    Zobrazení notifikací pro přihlášeného uživatele.
    """
    # Získání všech notifikací pro přihlášeného uživatele
    notifications = request.user.notifications.order_by('-created_at')
    
    # Označení všech notifikací jako přečtené
    unread_notifications = notifications.filter(is_read=False)
    for notification in unread_notifications:
        notification.is_read = True
        notification.save()
    
    context = {
        'notifications': notifications
    }
    return render(request, 'core/notifications.html', context)

@login_required
def following_list(request, username):
    """
    Zobrazení seznamu sledovaných uživatelů.
    """
    user = get_object_or_404(User, username=username)
    following = user.following.all().select_related('following').order_by('-created_at')
    
    context = {
        'profile_user': user,
        'following': [follow.following for follow in following]
    }
    return render(request, 'core/following_list.html', context)

@login_required
def followers_list(request, username):
    """
    Zobrazení seznamu sledujících.
    """
    user = get_object_or_404(User, username=username)
    followers = user.followers.all().select_related('follower').order_by('-created_at')
    
    context = {
        'profile_user': user,
        'followers': [follow.follower for follow in followers]
    }
    return render(request, 'core/followers_list.html', context)