from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class FormsTests(TestCase):
    """Тестирование форм"""

    def setUp(self):
        self.guest_client = Client()

    def test_create_post_form(self):
        """Создание поста при валидном заполнении формы"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Гвидо',
            'last_name': 'Ван-Россум',
            'username': 'pythondaddy',
            'email': 'gvido@python.com',
            'password1': 'veryhardpassword',
            'password2': 'veryhardpassword',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(first_name=form_data['first_name'],
                                            last_name=form_data['last_name'],
                                            username=form_data['username'],
                                            email=form_data['email'],
                                            ).exists())
