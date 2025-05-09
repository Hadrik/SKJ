from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Tweet, Comment

class UserRegisterForm(UserCreationForm):
    """
    Formulář pro registraci nového uživatele.
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    """
    Formulář pro aktualizaci uživatelských údajů.
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """
    Formulář pro aktualizaci profilu.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'profile_picture', 'website']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TweetForm(forms.ModelForm):
    """
    Formulář pro vytváření tweetů.
    """
    class Meta:
        model = Tweet
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What\'s happening?'}),
        }

class CommentForm(forms.ModelForm):
    """
    Formulář pro komentáře.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Tweet your reply'}),
        }

class SearchForm(forms.Form):
    """
    Formulář pro vyhledávání.
    """
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Search Twitter'})
    )
    search_type = forms.ChoiceField(
        choices=[('tweets', 'Tweets'), ('users', 'Users'), ('hashtags', 'Hashtags')],
        initial='tweets',
        widget=forms.RadioSelect
    )