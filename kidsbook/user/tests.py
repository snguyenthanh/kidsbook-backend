import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group
from kidsbook.serializers import GroupSerializer
from kidsbook.user.views import generate_token

User = get_user_model()

url_prefix = '/api/v1'

class TestUser(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/user/'
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_user(username=self.username, email_address=self.email, password=self.password)


    def test_login(self):
        url = self.url + 'login/'
        response = self.client.post(url, data={'email_address': self.email})
        self.assertEqual(200, response.status_code)

    def get_token(self):
        token_response = self.client.post(self.url + 'login/', data={'email_address': self.email})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token

    def test_get_self_user_profile_with_token(self):
        token = self.get_token()
        response = self.client.get(self.url + 'profile/', HTTP_AUTHORIZATION=token)

        self.assertEqual(200, response.status_code)

    def test_get_self_user_profile_without_token(self):
        response = self.client.get(self.url + 'profile/')
        self.assertEqual(401, response.status_code)

    def test_get_user_info(self):
        token = self.get_token()

        # Create an user
        username = "hey"
        email = "kid@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_user(username=username, email_address=email, password=password)

        response = self.client.get("{}{}/profile/".format(self.url, str(user.id)), HTTP_AUTHORIZATION=token)
        ('output.txt', 'w') as out_f:
            out_f.write(str(response.data))
        self.assertEqual(200, response.status_code)

    def test_get_user_info_without_token(self):
        # Create an user
        username = "hey"
        email = "kid@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_user(username=username, email_address=email, password=password)

        response = self.client.get("{}{}/profile/".format(self.url, str(user.id)))
        self.assertEqual(401, response.status_code)
