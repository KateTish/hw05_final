from django.test import TestCase

from posts.models import Group, Post, User


class GeneralModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(),
            group=cls.group
        )

    def test_group_verbose_name(self):
        group = GeneralModelTest.group
        field_verboses = {
            'title': 'Название группы:',
            'slug': 'Адрес страницы:',
            'description': 'Описание группы:'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_verbose_name(self):
        post = GeneralModelTest.post
        field_verboses = {
            'text': 'Текст:',
            'group': 'Группа:',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        group = GeneralModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите адрес странницы',
            'description': 'Введите описание группы'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post_help_text(self):
        post = GeneralModelTest.post
        field_help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу (необязательно)'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str_group(self):
        group = GeneralModelTest.group
        expected_str = group.title
        self.assertEquals(expected_str, str(group))

    def test_str_post(self):
        post = GeneralModelTest.post
        expected_str = post.text[:15]
        self.assertEquals(expected_str, str(post))
