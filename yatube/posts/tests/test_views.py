from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group
from posts.views import NUMBER_DISPLAY_POSTS

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTest.user.get_username()}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTest.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTest.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_list_page_show_correct_context(self):
        """Страница posts:index сформирована с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Тестовый пост')
        self.assertEqual(first_post.author, PostPagesTest.user)
        self.assertEqual(first_post.group, PostPagesTest.group)

    def test_group_posts_list_page_correct_context(self):
        """Страница posts:group_list сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostPagesTest.group.slug}
        ))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Тестовый пост')
        self.assertEqual(first_post.author, PostPagesTest.user)
        self.assertEqual(first_post.group, PostPagesTest.group)
        self.assertEqual(response.context['group'], PostPagesTest.group)

    def test_profile_posts_list_page_correct_context(self):
        """Страница posts:profile сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostPagesTest.user.get_username()}
        ))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Тестовый пост')
        self.assertEqual(first_post.author, PostPagesTest.user)
        self.assertEqual(first_post.group, PostPagesTest.group)
        self.assertEqual(response.context['author'], PostPagesTest.user)

    def test_post_detail_page_correct_context(self):
        """Страница posts:post_detail сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostPagesTest.post.pk}
        ))
        self.assertEqual(response.context['post'].text, 'Тестовый пост')
        self.assertEqual(response.context['post'].author, PostPagesTest.user)
        self.assertEqual(response.context['post'].group, PostPagesTest.group)
        self.assertEqual(response.context['num_posts'], 1)

    def test_create_page_correct_context(self):
        """Страница posts:post_create сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_correct_context(self):
        """Страница posts:post_edit сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostPagesTest.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields.get(field)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].text, 'Тестовый пост')
        self.assertEqual(response.context['post'].author, PostPagesTest.user)
        self.assertEqual(response.context['post'].group, PostPagesTest.group)
        self.assertEqual(response.context['is_edit'], True)

    def test_new_post_appears_needed_page(self):
        """Если при создании поста указать группу, то он появляется
        на страницах: index, group_list, profile
        """
        # Создаем новый пост
        post_text = 'Новый пост'
        post_form = {
            'text': post_text,
            'group': PostPagesTest.group.pk
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form,
            follow=True
        )
        # Проверка процесса создания поста есть в test_forms.py
        # Тут проверяем только то, что пост появится на нужных страницах
        page_posts = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTest.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTest.user.get_username()}
            ): 'page_obj',
        }
        for adress, page_obj in page_posts.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                page_posts = response.context[page_obj]
                self.assertIn(PostPagesTest.post, page_posts.object_list)

    def test_new_post_missing_unnecessary_group(self):
        """Новый пост не попал в группу, для которой не был предназначен"""
        group_2 = Group.objects.create(
            title='Вторая группа',
            slug='test-slug-2'
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': group_2.slug}
        ))
        self.assertNotIn(
            PostPagesTest.post,
            response.context['page_obj'].object_list
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.num_posts = int(1.5 * NUMBER_DISPLAY_POSTS)
        for i in range(cls.num_posts):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )

    def setUp(self):
        self.client = Client()

    def test_index_first_page_contains_ten_records(self):
        """Первая страница содержит ровно 10 постов"""
        page_context = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.get_username()}
            ): 'page_obj',
        }
        for adress, post_list in page_context.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(
                    len(response.context[post_list]),
                    NUMBER_DISPLAY_POSTS
                )

    def test_index_second_page_contains_three_records(self):
        """На второй странице содержатся оставшиеся посты"""
        page_context = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.get_username()}
            ): 'page_obj',
        }
        for adress, post_list in page_context.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress + '?page=2')
                self.assertEqual(
                    len(response.context[post_list]),
                    PaginatorViewsTest.num_posts - NUMBER_DISPLAY_POSTS
                )
