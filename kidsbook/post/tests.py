import json
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Post, Group, Comment
from kidsbook.serializers import PostSerializer
from kidsbook.user.views import generate_token

User = get_user_model()

url_prefix = '/api/v1'

class TestPost(APITestCase):
    def setUp(self):
        # Creator
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.creator = User.objects.create_superuser(username=self.username, email_address=self.email, password=self.password)
        token = generate_token(self.creator)
        self.creator_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # User
        self.username = "hey"
        self.email = "kid@s.sss"
        self.password = "want_some_cookies?"
        self.member = User.objects.create_user(username=self.username, email_address=self.email, password=self.password)
        token = generate_token(self.member)
        self.user_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Create a Group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group_id = response.data.setdefault('data', {}).get('id', '')

        #self.url = "{}/group/{}/".format(url_prefix, self.group_id)

        # Create a post
        self.post = Post.objects.create_post(
            content='Need someone to eat lunch at pgp?',
            creator=self.creator,
            group=Group.objects.get(id=self.group_id)
        )

        # Create a comment
        self.comment = Comment.objects.create_comment(
            content='OKAY',
            post=self.post,
            creator=self.creator
        )

    def test_get_all_post_in_group(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_post_in_group_by_non_member(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_post_in_group_without_token(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_get_post_detail_by_id(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)

        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(200, response.status_code)

    def test_get_post_detail_by_id_by_non_member(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_post_detail_by_id_without_token(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)


    def test_get_all_comments_of_post(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(200, response.status_code)

    def test_get_all_comments_of_post_by_non_member(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_comments_of_post_without_token(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_get_comment_by_id(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)

        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(200, response.status_code)

    def test_get_comment_by_id_by_non_member(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_comment_by_id_without_token(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)
