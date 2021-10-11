from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# allows  us to make test  requests to our application
from django.test import Client


class AdminSiteTests(TestCase):

    def setUp(self):  # run s before other test
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@softdev.com",
            password="password123"
        )
        # uses the client to login in a user using django authentication
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@adminusercreate.com',
            password='password123',
            name='Admin provided full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # generates a url for our list userpage
        url = reverse('admin:core_user_changelist')
        # uses the client to perfom  a httRequest for the matched url
        res = self.client.get(url)

        # assertContains checks if res has something
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """"Test that the edit page works"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        # /admin/core/user/1
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)  # test page renders Ok.

    def test_create_user_page(self):
        """Test that the create page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
