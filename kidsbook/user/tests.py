import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group
from kidsbook.serializers import UserSerializer
from kidsbook.user.views import generate_token

User = get_user_model()

url_prefix = '/api/v1'

class TestUser(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/user/'
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_superuser(username=self.username, email_address=self.email, password=self.password)


    def test_login(self):
        url = self.url + 'login/'
        response = self.client.post(url, data={'email_address': self.email, 'password': self.password})
        self.assertEqual(200, response.status_code)

    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': user.password})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token


    def test_get_self_user_profile_with_token(self):
        token = self.get_token(self.user)
        user_id = self.user.id
        response = self.client.get("{}{}/".format(self.url, user_id), HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

    def test_get_self_user_profile_without_token(self):
        user_id = self.user.id
        response = self.client.get("{}{}/".format(self.url, user_id))
        self.assertEqual(401, response.status_code)

    def test_get_user_info(self):
        token = self.get_token(self.user)

        # Create an user
        username = "hey"
        email = "kid@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_user(username=username, email_address=email, password=password)

        response = self.client.get("{}{}/".format(self.url, user.id), HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

    def test_get_user_info_without_token(self):
        # Create an user
        username = "hey"
        email = "kid@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_user(username=username, email_address=email, password=password)

        response = self.client.get("{}{}/".format(self.url, user.id))
        self.assertEqual(401, response.status_code)

    def test_get_virtual_users(self):
        token = self.get_token(self.user)

        # Create virtual user
        username = "hey3"
        email = "kid3@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_virtual_user(username=username, email_address=email, password=password, teacher=self.user)

        response = self.client.get(self.url + 'virtual_users/', HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

    def test_register_superuser(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'SUPERUSER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': 'a'
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_register_user(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': 'a',
                'teacher': self.user.id
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_register_user_without_teacher(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': 'a'
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_register_user_by_non_superuser(self):
        username = "hey3"
        email = "kid3@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_user(username=username, email_address=email, password=password, teacher=self.user)
        token = self.get_token(user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': 'a',
                'teacher': user.id
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(403, response.status_code)

    def test_register_virtual_user(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'VIRTUAL_USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': 'a',
                'teacher': self.user.id
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_login_virtual_as_correct_teacher(self):
        token = self.get_token(self.user)
        username = "hey3"
        email = "kid3@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_virtual_user(username=username, email_address=email, password=password, teacher=self.user)

        payload = {
            'email_address': 'kid3@s.sss'
        }
        response = self.client.post(self.url + 'login_as_virtual/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

    def test_login_virtual_as_incorrect_teacher(self):
        token = self.get_token(self.user)

        username = "heyasgafsg3"
        email = "kidasfgfs3@s.sss"
        password = "want_some_cookies?"
        teacher = User.objects.create_superuser(username=username, email_address=email, password=password)

        username = "hey3"
        email = "kid3@s.sss"
        password = "want_some_cookies?"
        user = User.objects.create_virtual_user(username=username, email_address=email, password=password, teacher=teacher)

        payload = {
            'email_address': 'kid3@s.sss'
        }
        response = self.client.post(self.url + 'login_as_virtual/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_get_groups_of_user(self):
        token = self.get_token(self.user)
        # Create many groups
        group_ids = []
        response = self.client.post(url_prefix + '/group/', {"name": "testing group1"}, HTTP_AUTHORIZATION=token)
        group_ids.append(
            response.data.setdefault('data', {}).get('created_group_id', '')
        )

        response = self.client.post(url_prefix + '/group/', {"name": "testing group2"}, HTTP_AUTHORIZATION=token)
        group_ids.append(
            response.data.setdefault('data', {}).get('created_group_id', '')
        )

        response = self.client.post(url_prefix + '/group/', {"name": "testing group3"}, HTTP_AUTHORIZATION=token)
        group_ids.append(
            response.data.setdefault('data', {}).get('created_group_id', '')
        )

        # Create a member
        username = "Du"
        email = "Du@has.t"
        password = "du_hast_mich"
        user = User.objects.create_user(username=username, email_address=email, password=password)
        normal_token = self.get_token(user)

        # Add the member to all groups
        for group_id in iter(group_ids):
            Group.objects.get(id=group_id).add_member(user)

        response = self.client.get("{}{}/groups/".format(self.url, user.id), HTTP_AUTHORIZATION=normal_token)

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.data.get('data', [])))

class TestUserUpdate(APITestCase):
    def setUp(self):
        # Superuser
        self.url = url_prefix + '/user/'

        username = "john"
        email = "john@snow.com"
        password = "you_know_nothing"
        self.creator = User.objects.create_superuser(username=username, email_address=email, password=password)

        # A user to modify
        username = "Doggo"
        email = "Mc@Dog.Face"
        password = "the_goodest_boi"
        description = 'Chihuahua'
        gender = True
        self.modify_user = User.objects.create_user(username=username,
                                            email_address=email,
                                            password=password,
                                            description=description,
                                            gender=gender,
                                            teacher=self.creator)
        self.update_url = "{}update/{}/".format(self.url, self.modify_user.id)

    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': user.password})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token

    def changes_reflect_in_response(self, request_changes, previous_state, current_state):

        difference = { k : current_state[k] for k in set(current_state) - set(previous_state) }

        for key, prev_val in iter(previous_state.items()):
            if key == 'id' or key == 'password':
                continue

            # If the un-modified value changes
            if key not in request_changes and current_state.get(key, '') != prev_val:
                return False

            # If the un-modified value doesnt match
            if key in request_changes and request_changes[key] != current_state.get(key, ''):
                return False
        return True

    def test_update_by_creator(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        data = {
            'username': 'Not_doggo',
            'password': 'yea',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)

        self.assertTrue(
            self.changes_reflect_in_response(data, previous_state_of_user, response.data.get('data', {}))
        )

    def test_update_username_to_existing(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = "you_know_nothing"
        user = User.objects.create_user(username=username, email_address=email, password=password)

        data = {
            'username': username,
            'password': 'yea',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)

        self.assertFalse(
            self.changes_reflect_in_response(data, previous_state_of_user, response.data.get('data', {}))
        )

    def test_update_by_non_superuser(self):
        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = "you_know_nothing"
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'password': 'yea',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_update_by_non_creator(self):
        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = "you_know_nothing"
        user = User.objects.create_superuser(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'password': 'yea',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)
