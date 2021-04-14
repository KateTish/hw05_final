from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
            'group',
            'image'
        ]
        widgets = {
            'text': Textarea(attrs={'placeholder': _('Что нового?')})
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'text'
        ]
