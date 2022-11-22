from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, count_first_symbols

User = get_user_model()


class PostModelTest(TestCase):
    """Тестирование моделей"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='default_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Lorem ipsum dolor sit amet',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_group = PostModelTest.group
        test_post = PostModelTest.post
        models_str_view = {
            test_group: self.group.title,
            test_post: self.post.text[:count_first_symbols],
        }
        for object, expected_value in models_str_view.items():
            with self.subTest(field=object):
                self.assertEqual(
                    str(object), expected_value)

    def check_fields_meta_parametrs(self, attribute, test_model, attr_values):
        """Проверяет мета-параметр на соответствие."""
        for field, expected_value in attr_values.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(test_model._meta.get_field(field),
                                 attribute), expected_value)

    def run_test_scheme(self, test_scheme, attribute):
        """В цикле запускает проверку для каждого предмета
        теста с заданным мета-параметром."""
        for object, values in test_scheme.items():
            PostModelTest.check_fields_meta_parametrs(self,
                                                      attribute=attribute,
                                                      test_model=object,
                                                      attr_values=values)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        test_group = PostModelTest.group
        test_post = PostModelTest.post
        check_attribute = 'verbose_name'
        group_verboses = {
            'title': 'Название сообщества',
            'slug': 'Псевдоним сообщества',
            'description': 'Описание сообщества',
        }
        post_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        test_scheme = {
            test_group: group_verboses,
            test_post: post_verboses,
        }
        PostModelTest.run_test_scheme(self, test_scheme, check_attribute)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        test_group = PostModelTest.group
        test_post = PostModelTest.post
        check_attribute = 'help_text'
        group_help_text = {
            'title': '200 символов максимум',
            'slug': '200 символов максимум',
            'description': 'Тематика постов',
        }
        post_help_text = {
            'text': 'Семь раз отмерь, один раз напиши',
        }
        test_scheme = {
            test_group: group_help_text,
            test_post: post_help_text,
        }
        PostModelTest.run_test_scheme(self, test_scheme, check_attribute)
