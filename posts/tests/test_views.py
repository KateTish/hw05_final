import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class GeneralModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
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
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_slug'})
        )
        self.assertEqual(
            response.context['group'].title, 'Тестовое название'
        )
        self.assertEqual(
            response.context['group'].slug, 'test_slug'
        )
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание'
        )
        self.assertEqual(
            response.context['post'].image, 'posts/small.gif'
        )

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(
            response.context['author'], self.user
        )
        self.assertEqual(
            response.context['page'][0], self.post
        )
        self.assertEqual(
            response.context['post'].image, 'posts/small.gif'
        )

    def test_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        context = {
            response.context['post'].text: 'Тестовый текст',
            response.context['post'].author.username: self.user.username,
            response.context['post'].image: 'posts/small.gif'
        }
        for key, value in context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)

    def test_post_on_index(self):
        response = self.authorized_client.get(reverse('index'))
        precount = len(response.context['page'])
        test_post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(reverse('index'))
        postcount = len(response.context['page'])
        new_post = response.context['page'].object_list[0]
        self.assertEqual(precount + 1, postcount)
        self.assertEqual(test_post, new_post)

    def test_post_on_group(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_slug'})
        )
        test_post = response.context['page'].object_list[0]
        self.assertEqual(self.post, test_post)

    def test_post_not_on_another_group(self):
        another_group = Group.objects.create(
            title='Тестовое название 2',
            slug='test_slug_2',
            description='Тестовое описание'
        )
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': another_group.slug})
        )
        another_posts = response.context['page']
        self.assertNotIn(self.post, another_posts)

    def test_follow(self):
        precount = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', kwargs={
                'username': self.user2.username
            })
        )
        postcount = Follow.objects.all().count()
        self.assertEqual(precount + 1, postcount)

    def test_unfollow(self):
        self.authorized_client.get(
            reverse('profile_follow', kwargs={
                'username': self.user2.username
            })
        )
        precount = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={
                'username': self.user2.username
            })
        )
        postcount = Follow.objects.all().count()
        self.assertEqual(precount - 1, postcount)

    def test_show_post_to_follow(self):
        self.user3 = User.objects.create(username='TestUser3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user3)
        Follow.objects.create(user=self.user3, author=self.user)
        response = self.authorized_client.get(reverse('follow_index'))
        test_post = response.context['page'][0]
        self.assertEqual(self.post, test_post)

    def test_not_show_post_to_unfollow(self):
        self.user3 = User.objects.create(username='TestUser3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user3)
        response = self.authorized_client.get(reverse('follow_index'))
        test_post = self.post
        response_post = response.context['page']
        self.assertNotEqual(test_post, response_post)

    def test_authorized_client_comment(self):
        count = Comment.objects.count()
        comment = {'text': 'Тестовый комментарий'}
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            data=comment,
            follow=True
        )
        self.assertEqual(count + 1, Comment.objects.count())

    def test_guest_client_comment(self):
        count = Comment.objects.count()
        comment = {'text': 'Тестовый комментарий'}
        self.guest_client.post(
            reverse('add_comment', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            data=comment,
            follow=True
        )
        self.assertEqual(count, Comment.objects.count())

    def test_index_page_cache(self):
        response = self.authorized_client.get(reverse('index'))
        content_first = response.content
        Post.objects.create(
            text='Тестовый текст 2',
            author=self.user
        )
        response = self.authorized_client.get(reverse('index'))
        content_second = response.content
        self.assertEqual(content_first, content_second)
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        content_third = response.content
        self.assertNotEqual(content_second, content_third)
