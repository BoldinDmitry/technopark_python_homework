from django.shortcuts import render
from blog_platform.models import Post, Comment
from blog_platform.forms import PostForm, CommentForm
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from abc import ABC, abstractmethod


class AllPostsView(ListView):
    """
    Отображение списка постов
    """

    model = Post
    template_name = 'posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get('sorted_by') in ['-creation_date', '-views_count']:
            posts = Post.objects.filter(is_hidden=False).order_by(
                self.request.GET.get('sorted_by')
            )
        elif self.request.GET.get('title'):
            posts = Post.objects.filter(
                is_hidden=False,
                title__icontains=self.request.GET.get('title')
            )
        else:
            posts = Post.objects.filter(is_hidden=False)

        context['posts'] = posts
        return context


class PostsView(DetailView):
    """
    Отображение одного поста
    """
    model = Post
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(post=context['post'].pk).order_by('creation_date')
        context['comments'] = comments
        context['comment_add_url'] = "/post/{}/add_comment".format(context['post'].id)
        Post.objects.get(pk=context['post'].pk).add_view()
        return context


class Creation(CreateView, ABC):
    """
    Базовый класс создания объекта с помощью формы
    """
    template_name = 'creation_form.html'
    form_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _model = self.form_class.Meta.model
        _model_name = _model._meta.verbose_name
        context['model_name'] = _model_name.lower()
        return context

    @abstractmethod
    def get_success_url(self):
        pass


class CreationPost(Creation):
    """
    Создать пост
    """
    form_class = PostForm

    def get_success_url(self):
        return '/'


class CreationComment(Creation):
    """
    Создать коммент
    """
    form_class = CommentForm

    def get_initial(self):
        return {
            "post": self.kwargs['post_pk']
        }

    def get_success_url(self):
        return "/post/{}".format(self.kwargs['post_pk'])
