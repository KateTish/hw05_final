from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        super().setUpClass()
        self.guest_client = Client()

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_client(self):
        urls = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200
        }
        for url, expected_status in urls.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status)
