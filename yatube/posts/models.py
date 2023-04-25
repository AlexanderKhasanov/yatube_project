from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название группы (максимум 200 символов)'
    )
    slug = models.SlugField(
        max_length=20,
        unique=True,
        verbose_name='Адрес для страницы группы',
        help_text=(
            'Укажите уникальный адрес для страницы задачи. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания'
        )
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы'
    )

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
