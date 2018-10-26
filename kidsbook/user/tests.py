import os
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Group, Post
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

    def test_login_with_wrong_password(self):
        url = self.url + 'login/'
        response = self.client.post(url, data={'email_address': self.email, 'password': 'hieu_dep_trai'})
        self.assertEqual(403, response.status_code)

    def test_login(self):
        url = self.url + 'login/'
        response = self.client.post(url, data={'email_address': self.email, 'password': self.password})
        self.assertEqual(200, response.status_code)

    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': self.password})
        token = token_response.data.get('data', {}).get('token', b'')
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
        password = self.password
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

    def test_get_only_virtual_users(self):
        token = self.get_token(self.user)

        # Create virtual user
        username = "hey3"
        email = "kid3@s.sss"
        password = "want_some_cookies?"
        User.objects.create_virtual_user(username=username, email_address=email, password=password, teacher=self.user)

        username = "jkz"
        email = "mka@s.sss"
        password = "want_some_cookies?"
        User.objects.create_user(username=username, email_address=email, password=password, teacher=self.user)

        response = self.client.get(self.url + 'virtual_users/', HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_register_superuser(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'SUPERUSER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': self.password
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

        created_user_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            User.objects.filter(id=created_user_id).exists()
        )

    def test_register_user(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': self.password,
                'teacher': self.user.id
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)
        created_user_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            User.objects.filter(id=created_user_id).exists()
        )

    def test_register_user_without_teacher(self):
        token = self.get_token(self.user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': self.password
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_register_user_by_non_superuser(self):
        username = "hey3"
        email = "kid3@s.sss"
        password = self.password
        user = User.objects.create_user(username=username, email_address=email, password=password, teacher=self.user)
        token = self.get_token(user)

        payload = {
                'type': 'USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': self.password,
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
                'password': self.password,
                'teacher': self.user.id
        }
        response = self.client.post(self.url + 'register/', payload, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_login_virtual_as_correct_teacher(self):
        token = self.get_token(self.user)
        username = "hey3"
        email = "kid3@s.sss"
        password = self.password
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
        password = self.password
        teacher = User.objects.create_superuser(username=username, email_address=email, password=password)

        username = "hey3"
        email = "kid3@s.sss"
        password = self.password
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
            response.data.setdefault('data', {}).get('id', '')
        )

        response = self.client.post(url_prefix + '/group/', {"name": "testing group2"}, HTTP_AUTHORIZATION=token)
        group_ids.append(
            response.data.setdefault('data', {}).get('id', '')
        )

        response = self.client.post(url_prefix + '/group/', {"name": "testing group3"}, HTTP_AUTHORIZATION=token)
        group_ids.append(
            response.data.setdefault('data', {}).get('id', '')
        )

        # Create a member
        username = "Du"
        email = "Du@has.t"
        password = self.password
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
        self.password = "you_know_nothing"
        self.creator = User.objects.create_superuser(username=username, email_address=email, password=self.password)

        # A user to modify
        username = "Doggo"
        self.email = "Mc"
        password = self.password
        description = 'Chihuahua'
        gender = True
        self.modify_user = User.objects.create_user(username=username,
                                            email_address=self.email,
                                            password=password,
                                            description=description,
                                            gender=gender,
                                            teacher=self.creator)
        self.update_url = "{}update/{}/".format(self.url, self.modify_user.id)

    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': self.password})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token

    def changes_reflect_in_response(self, request_changes, previous_state, current_state):
        difference = { k : current_state[k] for k in set(current_state) - set(previous_state) }

        for key, prev_val in iter(previous_state.items()):
            if key in {'id', 'password', 'num_comment', 'num_like_received', 'num_like_given'}:
                continue

            # If the un-modified value changes
            if key not in request_changes and current_state.get(key, '') != prev_val:
                return False

            # If the un-modified value doesnt match
            if key in request_changes and isinstance(request_changes[key], str) and request_changes[key] != current_state.get(key, ''):
                return False
        return True

    def test_update_password_correct_oldPassword(self):
        token = self.get_token(self.modify_user)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        data = {
            'password': 'hieu_dep_trai',
            'oldPassword': self.password,
            'email': self.email,
        }

        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_update_password_incorrect_oldPassword(self):
        token = self.get_token(self.modify_user)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        data = {
            'password': 'hieu_dep_trai',
            'oldPassword': 'wrong_password',
            'email': self.email,
        }

        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_update_by_creator(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            request_changes = {
                'username': 'Not_doggo',
                'description': 'Corki',
                "profile_photo": pic}
            response = self.client.post(self.update_url, request_changes, HTTP_AUTHORIZATION=token)
            self.assertEqual(202, response.status_code)

        cur_state = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})
        self.assertTrue(
            self.changes_reflect_in_response(request_changes, previous_state_of_user, cur_state)
        )

    def test_update_username_to_existing(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.modify_user.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        user = User.objects.create_user(username=username, email_address=email, password=password)

        data = {
            'username': username,
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)
        self.assertFalse(
            self.changes_reflect_in_response(data, previous_state_of_user, response.data.get('data', {}))
        )

    def test_update_by_non_superuser(self):
        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_update_superuser_by_non_superuser(self):
        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'description': 'Corki'
        }
        response = self.client.post("{}update/{}/".format(self.url, self.creator.id), data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_update_in_no_groups_by_non_creator(self):
        # Create a random user
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        user = User.objects.create_superuser(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(202, response.status_code)

    def test_update_in_a_diff_group_by_non_creator(self):
        # Create a group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group by a random stranger"}, HTTP_AUTHORIZATION=self.get_token(self.creator))
        group = Group.objects.get(id=response.data.get('data', {}).get('id', ''))
        group.add_member(self.modify_user)

        # Create a random superuser
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        user = User.objects.create_superuser(username=username, email_address=email, password=password)
        token = self.get_token(user)

        data = {
            'username': 'Not_doggo',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=token)
        self.assertEqual(405, response.status_code)

    def test_update_superuser_by_himself(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.creator.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            request_changes = {
                'username': 'Not_doggo',
                'description': 'Corki',
                "profile_photo": pic}
            response = self.client.post("{}update/{}/".format(self.url, self.creator.id), request_changes, HTTP_AUTHORIZATION=token)
            self.assertEqual(202, response.status_code)

        cur_state = self.client.get("{}{}/".format(self.url, self.creator.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        self.assertTrue(
            self.changes_reflect_in_response(request_changes, previous_state_of_user, cur_state)
        )

    def test_update_superuser_password_by_himself(self):
        token = self.get_token(self.creator)
        previous_state_of_user = self.client.get("{}{}/".format(self.url, self.creator.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            request_changes = {
                'username': 'Not_doggo',
                'description': 'Corki',
                "profile_photo": pic,
                'password': 'new_pass',
                'oldPassword': self.password}
            response = self.client.post("{}update/{}/".format(self.url, self.creator.id), request_changes, HTTP_AUTHORIZATION=token)
            self.assertEqual(202, response.status_code)

        cur_state = self.client.get("{}{}/".format(self.url, self.creator.id), HTTP_AUTHORIZATION=token).data.get('data', {})

        self.assertTrue(
            self.changes_reflect_in_response(request_changes, previous_state_of_user, cur_state)
        )

    def test_update_superuser_password_without_oldpassword_by_himself(self):
        token = self.get_token(self.creator)
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            request_changes = {
                'username': 'Not_doggo',
                'description': 'Corki',
                "profile_photo": pic,
                'password': 'new_pass'}
            response = self.client.post("{}update/{}/".format(self.url, self.creator.id), request_changes, HTTP_AUTHORIZATION=token)
            self.assertEqual(405, response.status_code)


class TestUpdateVirtualUser(APITestCase):
    def setUp(self):
        # Superuser
        self.url = url_prefix + '/user/'

        username = "john"
        email = "john@snow.com"
        self.password = "you_know_nothing"
        self.creator = User.objects.create_superuser(username=username, email_address=email, password=self.password)
        self.creator_token = self.get_token(self.creator)

        # A user to modify
        username = "Doggo"
        self.email = "Mc"
        password = self.password
        description = 'Chihuahua'
        gender = True
        self.modify_user = User.objects.create_user(username=username,
                                            email_address=self.email,
                                            password=password,
                                            description=description,
                                            gender=gender,
                                            teacher=self.creator)
        self.update_url = "{}update/{}/".format(self.url, self.modify_user.id)

        # Create a group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group by a random stranger"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group = Group.objects.get(id=response.data.get('data', {}).get('id', ''))

        # Create a random superuser
        username = "chris"
        email = "chris@snow.com"
        password = self.password
        self.superuser = User.objects.create_superuser(username=username, email_address=email, password=password)
        self.superuser_token = self.get_token(self.superuser)

    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': self.password})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token

    def test_update_non_created_virtual_user_in_same_group(self):
        # Create a virtual user
        payload = {
                'type': 'VIRTUAL_USER',
                'email_address': 'kids4@gmial.cpm',
                'realname': 'HIAFALJ',
                'username': 'asasbn',
                'password': self.password,
                'teacher': self.creator.id
        }
        response = self.client.post(url_prefix + '/user/register/', payload, HTTP_AUTHORIZATION=self.creator_token)
        virtual_user = User.objects.get(id=response.data.get('data', {}).get('id', ''))
        self.group.add_member(virtual_user)

        data = {
            'username': 'Not_doggo',
            'description': 'Corki'
        }
        response = self.client.post(self.update_url, data=data, HTTP_AUTHORIZATION=self.superuser_token)
        self.assertEqual(202, response.status_code)



def TestUserPost(self):
    def setUp(self):
        self.url = url_prefix + '/user/'
        self.username = "john"
        self.email = "john@snow.com"
        self.password = self.password
        self.creator = User.objects.create_superuser(username=self.username, email_address=self.email, password=self.password)

        # Create a member
        username = "kido"
        email = "knis@snow.com"
        password = self.password
        self.user = User.objects.create_superuser(username=username, email_address=email, password=password)

        # Create a group
        self.group = Group.objects.create_group({
            'name': 'testing group'
        })
        self.group.add_member(self.user)

        self.post = Post.objects.create_post(
            content='Need someone to eat lunch at pgp?',
            creator=self.user,
            group=self.group
        )


    def get_token(self, user):
        token_response = self.client.post(self.url + 'login/', data={'email_address': user.email_address, 'password': self.password})
        token = token_response.data.setdefault('data', {}).get('token', b'')
        token = 'Bearer {0}'.format(token.decode('utf-8'))
        return token

    def test_get_all_posts_of_user(self):
        token = self.get_token(self.user)

        response = self.client.get("{}/posts/".format(self.url, self.user.id), HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

    def test_get_all_posts_of_user_without_token(self):
        response = self.client.get("{}/posts/".format(self.url, self.user.id))
        self.assertEqual(401, response.status_code)
