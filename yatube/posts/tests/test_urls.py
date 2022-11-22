from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from ..utils import check_urls_redirect, check_urls_status

User = get_user_model()


class PostURLTests(TestCase):
    """Тестирование URL."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_non_author = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Lorem ipsum dolor sit amet',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.user_non_author)

    def test_urls_exists_at_desired_location(self):
        """URL-адрес возвращает корректный статус."""
        urls_guest_client = {
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/comment': HTTPStatus.MOVED_PERMANENTLY,
            f'/profile/{self.user_author.username}/follow':
                HTTPStatus.MOVED_PERMANENTLY,
            f'/profile/{self.user_author.username}/unfollow':
                HTTPStatus.MOVED_PERMANENTLY,
            '/blablabla/': HTTPStatus.NOT_FOUND,
        }
        urls_authorized_client = {
            '': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/profile/{self.user_author.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            f'/posts/{self.post.id}/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
            f'/profile/{self.user_non_author.username}/follow/':
                HTTPStatus.FOUND,
            f'/profile/{self.user_non_author.username}/unfollow/':
                HTTPStatus.FOUND,
        }
        check_urls_status(self, self.guest_client, urls_guest_client)
        check_urls_status(self, self.authorized_client, urls_authorized_client)

    def test_urls_redirect(self):
        """URL-адрес перенаправляет на корректную страницу."""
        urls_guest_client = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
            f'/posts/{self.post.id}/comment/':
                f'/auth/login/?next=/posts/{self.post.id}/comment/',
            f'/profile/{self.user_author.username}/follow/':
                f'/auth/login/?next=/profile/{self.user_author.username}'
                f'/follow/',
            f'/profile/{self.user_author.username}/unfollow/':
                f'/auth/login/?next=/profile/{self.user_author.username}'
                f'/unfollow/',
        }
        urls_authorized_client_non_author = {
            f'/posts/{self.post.id}/edit/': f'/posts/{self.post.id}/',
            f'/posts/{self.post.id}/comment/': f'/posts/{self.post.id}/',
            f'/profile/{self.user_author.username}/follow/':
                f'/profile/{self.user_author.username}/',
            f'/profile/{self.user_author.username}/unfollow/':
                f'/profile/{self.user_author.username}/',
        }
        check_urls_redirect(self, self.guest_client, urls_guest_client)
        check_urls_redirect(self, self.authorized_client_non_author,
                            urls_authorized_client_non_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user_author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
