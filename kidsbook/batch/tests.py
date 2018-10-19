import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group
from kidsbook.serializers import GroupSerializer
from kidsbook.user.views import generate_token
import inspect


User = get_user_model()

url_prefix = '/api/v1'

class TestBatch(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/batch/'
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_superuser(username=self.username, email_address=self.email, password=self.password)
        token = generate_token(self.user)
        self.token = 'Bearer {0}'.format(token.decode('utf-8'))
        self.api_authentication(self.token)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=self.token)

    def test_batch_create(self):
        body = {
            'file': (
                'test_dataset.csv',
                """username,email_address,password,realname,gender,is_superuser
                chris,chris@email.com,password_for_kris,Christiana Messi,0,
                james,james@email.com,password_for_kris,Christiana Messi,1,1
                ama,ama@email.com,ama_pwd,Ama Johnson,1,0"""
            )
        }

        headers = {
            'Content-Disposition': 'attachment; filename=testing.csv'
        }

        response = self.client.post(self.url + 'create/user/test_dataset.csv/', data=body)

        self.assertEqual(202, response.status_code)
