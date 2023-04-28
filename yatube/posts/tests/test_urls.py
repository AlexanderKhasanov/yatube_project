from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
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

    def test_public_pages_exists_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю"""
        public_pages = [
            '/',
            f'/group/{PostURLTests.group.slug}/',
            f'/profile/{PostURLTests.user.get_username()}/',
            f'/posts/{PostURLTests.post.pk}/',
        ]
        for adress in public_pages:
            with self.subTest(adress=adress):
                response = self.guest_user.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации
        """
        response = self.guest_user.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница /post/<post_id>/edit/ доступна автору"""
        post_id = PostURLTests.user.posts.all()[0].pk
        response = self.authorized_client.get(
            f'/posts/{post_id}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_redirect_no_author(self):
        """Страница /post/<post_id>/edit/ перенаправляет не автора
        на подробную информацию о посте
        """
        user_2 = User.objects.create_user(username='User_2')
        no_author = Client()
        no_author.force_login(user_2)
        post_id = PostURLTests.user.posts.all()[0].pk
        response = no_author.get(
            f'/posts/{post_id}/edit/'
        )
        self.assertRedirects(response, (f'/posts/{post_id}/'))

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post/<post_id>/edit/ перенаправляет анонимного
        пользователя на страницу авторизации
        """
        post_id = PostURLTests.user.posts.all()[0].pk
        response = self.guest_user.get(
            f'/posts/{post_id}/edit/'
        )
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{post_id}/edit/')
        )

    def test_non_existent_page(self):
        """Попытка зайти на несуществующую страницу"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_name = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.get_username()}/': (
                'posts/profile.html'
            ),
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in url_templates_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
