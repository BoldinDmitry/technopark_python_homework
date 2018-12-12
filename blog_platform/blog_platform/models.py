from django.db import models


class Post(models.Model):
    title = models.CharField(u'Тема', max_length=255)
    text = models.TextField(u'Текст')
    views_count = models.IntegerField(u'Число просмотров', default=0)
    creation_date = models.DateTimeField(u'Дата создания', auto_now_add=True)
    is_hidden = models.BooleanField(default=False)

    def add_view(self):
        self.views_count += 1
        self.save()

    def __str__(self):
        return '{} | {}'.format(self.pk, self.title)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    author_nick = models.CharField(u'Автор', max_length=255)
    text = models.TextField(u'Текст')
    creation_date = models.DateTimeField(u'Дата создания', auto_now_add=True)

    def __str__(self):
        return "{} -> {}".format(self.author_nick, self.post)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
