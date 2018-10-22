from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group, GroupMember
from kidsbook.user.views import generate_token


User = get_user_model()
url_prefix = '/api/v1'

class TestUsers(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/users/'

        # Creator
        username = "john"
        email = "john@snow.com"
        password = "you_know_nothing"
        self.creator = User.objects.create_superuser(username=username, email_address=email, password=password)
        self.creator_token = self.get_token(self.creator)

        # User
        username = "hey"
        email = "kid@s.sss"
        password = "want_some_cookies?"
        self.user = User.objects.create_user(username=username, email_address=email, password=password)
        self.user_token = self.get_token(self.user)

        # Group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        group_id = response.data.setdefault('data', {}).get('id', '')
        self.group = Group.objects.get(id=group_id)

        # Member
        username = "123"
        email = "lets@go.ooo"
        password = "razer_synapse"
        self.member = User.objects.create_user(username=username, email_address=email, password=password)
        self.member_token = self.get_token(self.member)
        self.group.add_member(self.member)


    def get_token(self, user):
        token = generate_token(user)
        return 'Bearer {0}'.format(token.decode('utf-8'))

    def test_get_all_users_non_in_group(self):
        url = self.url + 'non_group/'

        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertTrue(200, response.status_code)
        self.assertTrue(len(response.data.get('data', [])) == 1)
        self.assertTrue(
            str(response.data.get('data', [])[0].get('id', '')) == str(self.user.id)
        )

    def test_get_all_users_non_in_group_by_non_superuser(self):
        url = self.url + 'non_group/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)
        self.assertTrue(403, response.status_code)

    def test_get_all_users_non_in_group_by_non_member(self):
        url = self.url + 'non_group/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertTrue(403, response.status_code)

    def test_get_all_users_non_in_group_without_token(self):
        url = self.url + 'non_group/'
        response = self.client.get(url)
        self.assertTrue(401, response.status_code)
