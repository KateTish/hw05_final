from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class GeneralURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='TestUser')
        cls.user2 = User.objects.create(username='TestUser2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user2,
            group=cls.group
        )

    def test_urls_guest_client(self):
        urls = {
            reverse('index'): 200,
            reverse('group', kwargs={'slug': 'test_slug'}): 200,
            reverse('new_post'): 302,
            reverse('profile', kwargs={'username': self.user.username}): 200,
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }): 302,
            'nonexistent': 404
        }
        for url, expected_status in urls.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_authorized_client(self):
        urls = {
            reverse('index'): 200,
            reverse('group', kwargs={'slug': 'test_slug'}): 200,
            reverse('new_post'): 200,
            reverse('profile', kwargs={'username': self.user.username}): 200,
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }): 200,
            'nonexistent': 404
        }
        for url, expected_status in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_authorized_client_author(self):
        urls = {
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }): 200
        }
        for url, expected_status in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_authorized_client_not_author_redirect(self):
        urls = {
            reverse('post_edit', kwargs={
                'username': self.user2.username,
                'post_id': self.post2.id
            }): 302
        }
        for url, expected_status in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_use_correct_template(self):
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))
        self.assertTemplateUsed(response, 'new_post.html')
