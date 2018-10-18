import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group
from kidsbook.serializers import GroupSerializer
from kidsbook.user.views import generate_token

User = get_user_model()

url_prefix = '/api/v1'

class TestGroup(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/group/'
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        token = generate_token(self.user)
        self.token = 'Bearer {0}'.format(token.decode('utf-8'))
        self.api_authentication(self.token)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

    def test_create_group(self):
        response = self.client.post(self.url, {"name": "testing group"})
        self.assertEqual(201, response.status_code)

    def test_create_existing_group(self):
        self.client.post(self.url, {"name": "testing group"})
        response = self.client.post(self.url, {"name": "testing group"})
        self.assertEqual(400, response.status_code)

    def test_get_all_groups(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class TestGroupMember(APITestCase):
    def setUp(self):
        # Creator
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.creator = User.objects.create_user(self.username, self.email, self.password)
        token = generate_token(self.creator)
        self.creator_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # User
        self.username = "hey"
        self.email = "kid@s.sss"
        self.password = "want_some_cookies?"
        self.member = User.objects.create_user(self.username, self.email, self.password)
        token = generate_token(self.member)
        self.member_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group_id = response.data.get('created_group_id', '')

        self.url = "{}/group/{}/".format(url_prefix, self.group_id)


    def test_add_new_group_member(self):
        response = self.client.post("{}user/{}/".format(self.url, str(self.member.id)), HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

    def test_add_new_group_member_by_non_creator(self):
        self.client.post("{}user/{}/".format(self.url,str(self.member.id)), HTTP_AUTHORIZATION=self.creator_token)

        username = "Another"
        email = "one@b.ites"
        password = "the_dust"
        user = User.objects.create_user(username, email, password)

        # Add the user to be a member
        url = "{}user/{}/".format(self.url, str(user.id))
        response = self.client.post(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(403, response.status_code)

    def test_add_duplicated_group_member(self):
        url = self.url + 'user/' + str(self.member.id) + '/'
        self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)
        response = self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(400, response.status_code)

    def test_delete_group_member(self):
        url = self.url + 'user/' + str(self.member.id) + '/'
        self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

    def test_delete_group_member_by_non_creator(self):
        self.client.post(self.url + 'user/' + str(self.member.id) + '/', HTTP_AUTHORIZATION=self.creator_token)

        username = "Another"
        email = "one@b.ites"
        password = "the_dust"
        user = User.objects.create_user(username, email, password)

        # Add the user to be a member
        url = self.url + 'user/' + str(user.id) + '/'
        self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)

        response = self.client.delete(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(403, response.status_code)


    def test_delete_not_joined_group_member(self):
        username = "Another"
        email = "one@b.ites"
        password = "the_dust"
        user = User.objects.create_user(username, email, password)

        url = self.url + 'user/' + str(user.id) + '/'
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(400, response.status_code)

    def test_delete_group_creator(self):
        url = self.url + 'user/' + str(self.creator.id) + '/'
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(400, response.status_code)


class TestGroupManage(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/group/'

        # Creator
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.creator = User.objects.create_user(self.username, self.email, self.password)
        token = generate_token(self.creator)
        self.creator_token = 'Bearer {0}'.format(token.decode('utf-8'))

    def test_delete_group(self):
        response = self.client.post(self.url, {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        with open('output.txt', 'w') as out_f:
            out_f.write(str(response.data))

        group_id = str(response.data.get('created_group_id', ''))
        url = "{}{}/".format(self.url, group_id)

        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

    def test_delete_group_by_non_creator(self):
        # Create a group
        group_response = self.client.post(self.url, {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        group_id = str(group_response.data.get('created_group_id', ''))
        url = self.url + group_id + '/'

        # Creat a non-creator
        username = "james"
        email = "james@yong.com"
        password = "testing_ppp"
        user = User.objects.create_user(username, email, password)
        token = 'Bearer {0}'.format(generate_token(user).decode('utf-8'))

        response = self.client.delete(url, HTTP_AUTHORIZATION=token)
        self.assertEqual(403, response.status_code)
