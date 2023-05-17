import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, Comment, Follow
from posts.views import NUMBER_DISPLAY_POSTS

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.test_img = SimpleUploadedFile(
            name='test.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.test_img
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTest.user)
        cache.clear()

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
        self.assertEqual(first_post.image, 'posts/test.gif')

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
        self.assertEqual(first_post.image, 'posts/test.gif')
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
        self.assertEqual(first_post.image, 'posts/test.gif')
        self.assertEqual(response.context['author'], PostPagesTest.user)
        self.assertEqual(response.context['following'], False)

    def test_post_detail_page_correct_context(self):
        """Страница posts:post_detail сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostPagesTest.post.pk}
        ))
        self.assertEqual(response.context['post'].text, 'Тестовый пост')
        self.assertEqual(response.context['post'].author, PostPagesTest.user)
        self.assertEqual(response.context['post'].group, PostPagesTest.group)
        self.assertEqual(response.context['post'].image, 'posts/test.gif')

    def test_create_page_correct_context(self):
        """Страница posts:post_create сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
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

    def test_new_comment_appears_post_detail(self):
        """После создания комментария, он появляется на странице
        post_detail
        """
        comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=PostPagesTest.user,
            post=PostPagesTest.post
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTest.post.pk}
            )
        )
        post_comments = response.context['comments']
        self.assertIn(comment, post_comments)

    def test_cache_index(self):
        """Проверка кеширования главной страницы"""
        test_post = Post.objects.create(
            author=PostPagesTest.user,
            text='Test cache',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        content = response.content
        test_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, content)

    def test_follow_authorized(self):
        """Авторизированный пользователь может подписаться"""
        author = User.objects.create_user(username='Author')
        count_follow = Follow.objects.count()
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': author.get_username()}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': author.get_username()}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=PostPagesTest.user,
                author=author
            ).exists()
        )

    def test_unfollow_authorized(self):
        """Авторизированный пользователь может отписаться"""
        author = User.objects.create_user(username='Author')
        count_follow = Follow.objects.count()
        Follow.objects.create(
            user=PostPagesTest.user,
            author=author
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': author.get_username()}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': author.get_username()}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow)
        self.assertFalse(
            Follow.objects.filter(
                user=PostPagesTest.user,
                author=author
            ).exists()
        )

    def test_new_post_show_follower(self):
        """Новый пост пользователя показывается подписчикам ленте подписок"""
        author = User.objects.create_user(username='Author')
        Follow.objects.create(
            user=PostPagesTest.user,
            author=author
        )
        new_post = Post.objects.create(
            text='Новый пост автора, на который ты подписан',
            author=author
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        page_posts = response.context['page_obj']
        self.assertIn(new_post, page_posts)

    def test_new_post_dont_show_nofollower(self):
        """Новый пост пользователя не показывается
        не подписчикам ленте подписок
        """
        author = User.objects.create_user(username='Author')
        user_2 = User.objects.create_user(username='NoFollower')
        no_follower = Client()
        no_follower.force_login(user_2)
        Follow.objects.create(
            user=PostPagesTest.user,
            author=author
        )
        new_post = Post.objects.create(
            text='Новый пост автора, на который ты подписан',
            author=author
        )
        response = no_follower.get(reverse('posts:follow_index'))
        page_posts = response.context['page_obj']
        self.assertNotIn(new_post, page_posts)


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
        cache.clear()

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
