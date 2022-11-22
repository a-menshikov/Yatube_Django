import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from yatube import settings

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    """Тестирование форм."""

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
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Этот пост для проверки редактирования',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_create_post_form(self):
        """Создание поста при валидном заполнении формы."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Lorem ipsum dolor sit amet',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse
                             ('posts:profile',
                              kwargs={'username': self.user_author.username}
                              ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(group=form_data['group'],
                                            text=form_data['text'],
                                            ).exists())

    def test_edit_post_form(self):
        """Редактирование поста при валидном заполнении формы."""
        form_data = {
            'text': f'{self.post.text} edited',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse
                             ('posts:post_detail',
                              kwargs={'post_id': self.post.id}
                              ))
        self.assertTrue(Post.objects.filter(group=form_data['group'],
                                            text=form_data['text']).exists())

    def test_comment_form(self):
        """Создание комментария при валидном заполнении формы."""
        comment_count = Comment.objects.filter(post=self.post.id).count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.filter(post=self.post.id).count(),
                         comment_count + 1)
        self.assertTrue(Comment.objects.filter(post=self.post.id,
                                               text=form_data['text'],
                                               ).exists())
