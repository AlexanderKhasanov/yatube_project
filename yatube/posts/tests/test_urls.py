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
