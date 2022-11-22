from django.test import Client, TestCase, override_settings


@override_settings(DEBUG=False)
class PostURLTests(TestCase):
    """Тестирование кастомных страниц ошибок"""
    def setUp(self):
        self.guest_client = Client()

    def test_404_custom_page(self):
        """Проверка корректности кастомного шаблона 404"""
        non_exist_url = '/blablabla'
        response = self.guest_client.get(non_exist_url)
        template = 'core/404.html'
        self.assertTemplateUsed(response, template)
