import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    """Тестирование View."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.wrong_group = Group.objects.create(
            title='Другая группа',
            slug='wrong_slug',
            description='Здесь постов не будет',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text='Lorem ipsum dolor sit amet',
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_author,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user_author.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_page_show_correct_context(self):
        """Страница создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_edit_page_show_correct_context(self):
        """Страница редактирования поста
        сформирована с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              self.post.id}))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsNotNone(response.context.get('is_edit'),
                             'В контексте отсутствует ключ is_edit')
        self.assertTrue(response.context['is_edit'])

    def test_index_page_show_correct_context(self):
        """Главная страница возвращает корректный контекст."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        page_objects = response.context['page_obj'].object_list
        self.assertIsInstance(page_objects, list)
        for post in page_objects:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Страница пользователя возвращает корректный контекст."""
        reverse_url = reverse('posts:profile',
                              kwargs={'username': self.user_author.username})
        response = self.authorized_client.get(reverse_url)
        user_object = response.context['user_object']
        self.assertIsInstance(user_object, User)
        self.assertEqual(user_object, self.user_author)
        page_objects = response.context['page_obj'].object_list
        self.assertIsInstance(page_objects, list)
        self.assertIsNotNone(response.context.get('following'),
                             'В контексте отсутствует ключ following')
        for post in page_objects:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author.username, self.user_author.username)
            self.assertEqual(post.image, self.post.image)

    def test_group_page_show_correct_context(self):
        """Страница группы возвращает корректный контекст."""
        reverse_url = reverse('posts:group_posts',
                              kwargs={'slug': self.group.slug})
        response = self.authorized_client.get(reverse_url)
        group_object = response.context['group']
        self.assertIsInstance(group_object, Group)
        self.assertEqual(group_object, self.group)
        page_objects = response.context['page_obj'].object_list
        self.assertIsInstance(page_objects, list)
        for post in page_objects:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.group.slug, self.group.slug)
            self.assertEqual(post.image, self.post.image)

    def test_post_page_show_correct_context(self):
        """Страница поста возвращает корректный контекст."""
        reverse_url = reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(reverse_url)
        post_object = response.context['post_object']
        self.assertIsInstance(post_object, Post)
        self.assertEqual(post_object.id, self.post.id)
        self.assertIsNotNone(response.context.get('is_author'),
                             'В контексте отсутствует ключ is_author')
        self.assertTrue(response.context['is_author'])
        self.assertEqual(post_object.image, self.post.image)
        self.assertIsInstance(response.context['form'], CommentForm)
        comments = response.context['comments']
        for comment in comments:
            self.assertIsInstance(comment, Comment)
            self.assertEqual(comment.post.id, self.post.id)

    def test_new_post_show_correct_view(self):
        """Проверка корректности отображения нового поста на нужных страницах
        и отсутствия его на странице другой группы."""
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': self.user_author.username}),
            reverse('posts:group_posts',
                    kwargs={'slug': self.post.group.slug}),
        ]
        for reverse_url in reverse_list:
            response = self.authorized_client.get(reverse_url)
            first_object = response.context['page_obj'].object_list[0]
            post_values = {
                first_object.text: self.post.text,
                first_object.pub_date: self.post.pub_date,
                first_object.author: self.post.author,
                first_object.group: self.post.group,
            }
            for resieve_value, etalon_value in post_values.items():
                with self.subTest(resieve_value=resieve_value,
                                  etalon_value=etalon_value):
                    self.assertEqual(resieve_value, etalon_value)
        wrong_group_reverse = reverse('posts:group_posts',
                                      kwargs={'slug':
                                              PostViewsTests.wrong_group.slug})
        wrong_response = self.authorized_client.get(wrong_group_reverse)
        self.assertEqual(len(wrong_response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    """Тестирование пагинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.posts_count = 13
        for i in range(cls.posts_count):
            Post.objects.create(
                author=cls.user_author,
                group=cls.group,
                text='Lorem ipsum dolor sit amet',
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_first_page_contains_ten_records(self):
        """Проверка количества постов на 1 и 2 страницах."""
        page_1_count = 10
        page_2_count = 3
        test_paginator_values = {
            reverse('posts:index'): page_1_count,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): page_1_count,
            reverse('posts:profile',
                    kwargs={'username': self.user_author.username}):
                        page_1_count,
            reverse('posts:index') + '?page=2': page_2_count,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}) + '?page=2':
                        page_2_count,
            reverse('posts:profile',
                    kwargs={'username':
                            self.user_author.username}) + '?page=2':
                        page_2_count,
        }
        for reverse_name, post_count in test_paginator_values.items():
            with self.subTest(reverse_name=reverse_name,
                              post_count=post_count):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), post_count)


class CacheViewsTest(TestCase):
    """Тестирование кэширования."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text='Lorem ipsum dolor sit amet',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_cache_on_index_page(self):
        """Проверка кэширования на главной странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(f'{self.post.text}'
                        in str(response.content))
        Post.objects.get(pk=self.post.id).delete()
        response_with_cache = self.authorized_client.get(reverse
                                                         ('posts:index'))
        self.assertTrue(f'{self.post.text}'
                        in str(response_with_cache.content))
        cache.clear()
        response_clear_cache = self.authorized_client.get(reverse
                                                          ('posts:index'))
        self.assertFalse(f'{self.post.text}'
                         in str(response_clear_cache.content))


class FollowViewsTest(TestCase):
    """Тестирование aфункционала подписок."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_follower = User.objects.create_user(username='follower')
        cls.user_no_follower = User.objects.create_user(username='no_follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text='Lorem ipsum dolor sit amet',
        )

    def setUp(self):
        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.user_author)
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        self.auth_client_no_follower = Client()
        self.auth_client_no_follower.force_login(self.user_no_follower)

    def test_follow_unfollow_process(self):
        """Проверка возможности подписки и отписки
        для авторизованного пользователя."""
        self.auth_client_follower.get(reverse
                                      ('posts:profile_follow',
                                       kwargs={'username':
                                               self.user_author.username}
                                       ))
        self.assertTrue(Follow.objects.filter(user=self.user_follower,
                                              author=self.user_author
                                              ).exists())
        self.auth_client_follower.get(reverse
                                      ('posts:profile_unfollow',
                                       kwargs={'username':
                                               self.user_author.username}
                                       ))
        self.assertFalse(Follow.objects.filter(user=self.user_follower,
                                               author=self.user_author
                                               ).exists())

    def test_post_view_on_follower_page(self):
        """Проверка корректности отображения поста на
        странице подписанного пользователя и отсуствия его
        на странице неподписанного пользователя."""
        self.auth_client_follower.get(reverse
                                      ('posts:profile_follow',
                                       kwargs={'username':
                                               self.user_author.username}
                                       ))
        response_follower = self.auth_client_follower.get(reverse
                                                          ('posts:follow_index'
                                                           ))
        first_object = response_follower.context['page_obj'].object_list[0]
        post_values = {
            first_object.text: self.post.text,
            first_object.pub_date: self.post.pub_date,
            first_object.author: self.post.author,
            first_object.group: self.post.group,
        }
        for resieve_value, etalon_value in post_values.items():
            with self.subTest(resieve_value=resieve_value,
                              etalon_value=etalon_value):
                self.assertEqual(resieve_value, etalon_value)
        response_no_follower = self.auth_client_no_follower.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_no_follower.context['page_obj']), 0)
