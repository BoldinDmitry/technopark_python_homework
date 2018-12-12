from django.forms import ModelForm, HiddenInput
from blog_platform.models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
        )


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = (
            'post',
            'author_nick',
            'text'
        )
        widgets = {
            'post': HiddenInput()
        }
