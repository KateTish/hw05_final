import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()
        cls.user = User.objects.create(username='TestUser')
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст',
            'group': Group.objects.get(pk=1).pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=Group.objects.get(pk=1).pk,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': Group.objects.get(pk=1).pk
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post', kwargs={
                'username': self.post.author.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(Post.objects.count(), posts_count == posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Отредактированный тестовый текст',
                group=Group.objects.get(pk=1).pk,
            ).exists()
        )
