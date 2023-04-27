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
            '/group/test-slug/',
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
        print(f'______/post/{PostURLTests.user.posts.all()[0]}/edit/_____')
        response = self.authorized_client.get(
            f'/post/{PostURLTests.user.posts.all()[0].pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_redirect_no_author(self):
        """Страница /post/<post_id>/edit/ перенаправляет не автора
        на подробную информацию о посте
        """
        user_2 = User.objects.create_user(username='User_2')
        no_author = Client()
        no_author.force_login(user_2)
        response = no_author.get(
            f'/post/{PostURLTests.user.posts.all()[0]}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
