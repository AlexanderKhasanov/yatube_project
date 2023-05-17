from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        cache.clear()

    def test_public_pages_exists_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю"""
        public_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.get_username()}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ),
        ]
        for adress in public_pages:
            with self.subTest(adress=adress):
                response = self.guest_user.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации
        """
        post_create_url = reverse('posts:post_create')
        response = self.guest_user.get(post_create_url, follow=True)
        self.assertRedirects(
            response,
            reverse('auth:login') + '?next=' + post_create_url
        )

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница /post/<post_id>/edit/ доступна автору"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTests.post.pk}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_no_author(self):
        """Страница /post/<post_id>/edit/ перенаправляет не автора
        на подробную информацию о посте
        """
        user_2 = User.objects.create_user(username='User_2')
        no_author = Client()
        no_author.force_login(user_2)
        response = no_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTests.post.pk}
        ))
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostURLTests.post.pk}
        ))

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post/<post_id>/edit/ перенаправляет анонимного
        пользователя на страницу авторизации
        """
        post_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTests.post.pk}
        )
        response = self.guest_user.get(post_edit_url)
        self.assertRedirects(
            response,
            reverse('auth:login') + '?next=' + post_edit_url
        )

    def test_follow_redirect_anonymous(self):
        """При попытке подписаться неаторизованный пользователь
        перенаправляется на страницу авторизации
        """
        follow_url = reverse(
            'posts:profile_follow', kwargs={'username': PostURLTests.user}
        )
        response = self.guest_user.get(follow_url)
        self.assertRedirects(
            response,
            reverse('auth:login') + '?next=' + follow_url
        )

    def test_non_existent_page(self):
        """Попытка зайти на несуществующую страницу"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.get_username()}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_add_comment_url_redirect_anonymous(self):
        """Страница /<int:post_id>/comment/ перенаправляет анонимного
        пользователя на страницу авторизации
        """
        post_create_url = reverse(
            'posts:add_comment', kwargs={'post_id': PostURLTests.post.pk}
        )
        response = self.guest_user.get(post_create_url, follow=True)
        self.assertRedirects(
            response,
            reverse('auth:login') + '?next=' + post_create_url
        )
