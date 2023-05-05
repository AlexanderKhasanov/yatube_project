from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки моделей',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_post_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected_value in field_post_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
        group = PostModelTest.group
        field_group_verbose_name = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_group_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата публикации добавится автоматически',
            'group': 'Группа, к поторой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
        group = PostModelTest.group
        field_group_help_text = {
            'title': 'Введите название группы (максимум 200 символов)',
            'slug': ('Укажите уникальный адрес для страницы задачи. '
                     'Используйте только латиницу, цифры, дефисы и знаки '
                     'подчёркивания'),
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_group_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = GroupModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_group_verbose_name = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_group_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_group_help_text = {
            'title': 'Введите название группы (максимум 200 символов)',
            'slug': ('Укажите уникальный адрес для страницы задачи. '
                     'Используйте только латиницу, цифры, дефисы и знаки '
                     'подчёркивания'),
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_group_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )
