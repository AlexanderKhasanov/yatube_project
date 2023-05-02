from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostCreateFormTest(TestCase):
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
        self.authorized_client.force_login(PostCreateFormTest.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        post_text = 'Тестовое создание поста'
        post_form = {
            'text': post_text,
            'group': PostCreateFormTest.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostCreateFormTest.user.get_username()}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(
                text=post_text,
                group=PostCreateFormTest.group,
                author=PostCreateFormTest.user,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма меняет запись в Post"""
        posts_count = Post.objects.count()
        new_post_text = PostCreateFormTest.post.text + ' изменен'
        post_form = {
            'text': new_post_text,
            'group': PostCreateFormTest.group.pk
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTest.post.pk}
            ),
            data=post_form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostCreateFormTest.post.pk}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=new_post_text,
                group=PostCreateFormTest.group,
                author=PostCreateFormTest.user
            ).exists()
        )
