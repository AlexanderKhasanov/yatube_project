from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='group name',
        help_text='The group name cannot exceed 200 characters'
    )
    slug = models.SlugField(
        max_length=20,
        unique=True,
        verbose_name='the unique address of the group',
        help_text='Slug cannot exceed 200 characters. Slug must be unique'
    )
    description = models.TextField(verbose_name='text describing the group')

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации добавится автоматически'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='group',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к поторой будет относиться пост'
    )

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]
