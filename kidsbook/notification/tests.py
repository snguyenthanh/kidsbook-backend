from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import *
from kidsbook.serializers import *
from kidsbook.user.views import generate_token

User = get_user_model()
url_prefix = '/api/v1'

import json
from uuid import UUID
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class TestGroup(APITestCase):
    def setUp(self):
        self.url = url_prefix + '/notifications/'
        username = "john"
        email = "john@snow.com"
        password = "you_know_nothing"
        self.superuser = User.objects.create_superuser(username=username, email_address=email, password=password)
        self.creator_token = self.get_token(self.superuser)

        # Create a member
        username = "not_hey"
        email = "not_kid@s.sss"
        password = "want_some_cookies?"
        self.member = User.objects.create_user(username=username, email_address=email, password=password)
        self.member_token = self.get_token(self.member)

        # Create another member
        username = "mcdo"
        email = "incense@s.sss"
        password = "and_iron"
        self.another_member = User.objects.create_user(username=username, email_address=email, password=password)
        self.another_member_token = self.get_token(self.another_member)

        # Create a member not receiving any notifications
        username = "queen"
        email = "bulk@s.sss"
        password = "and_iron"
        self.dummy_member = User.objects.create_user(username=username, email_address=email, password=password)
        self.dummy_member_token = self.get_token(self.dummy_member)

        # Create a group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group_id = response.data.get('data', {}).get('id', '')
        self.group = Group.objects.get(id=self.group_id)
        self.group.add_member(self.member)
        self.group.add_member(self.another_member)
        self.group.add_member(self.dummy_member)

        # Create a post
        response = self.client.post("{}/group/{}/posts/".format(url_prefix, self.group_id),
                            {"content": "testing content", "link": "http://ogp.me"}, HTTP_AUTHORIZATION=self.member_token)
        self.post = Post.objects.get(id=response.data.get('data', {}).get('id', ''))
        self.assertEqual(202, response.status_code)

    def get_token(self, user):
        token = generate_token(user)
        return 'Bearer {0}'.format(token.decode('utf-8'))

    def reset_notifications_count_for_all(self):
        # Reset notification count
        response = self.client.post(url_prefix + "/notifications/", HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        response = self.client.post(url_prefix + "/notifications/", HTTP_AUTHORIZATION=self.member_token)
        self.assertEqual(202, response.status_code)
        response = self.client.post(url_prefix + "/notifications/", HTTP_AUTHORIZATION=self.another_member_token)
        self.assertEqual(202, response.status_code)

    def test_notification_when_a_new_post_is_created(self):
        self.assertTrue(
            Notification.objects.filter(
                user_id=self.another_member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.member
            )) == 3
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.superuser.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.another_member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.member
            ).content == "{} created a new post in group {}".format(self.member.username, self.group.name)
        )

    def test_notification_when_a_user_post_is_liked(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.another_member_token)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).content == "{} {} your post".format(self.another_member.username, 'likes')
        )

    def test_notification_when_a_user_post_is_disliked(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        self.client.post(url, {"like_or_dislike": False}, HTTP_AUTHORIZATION=self.another_member_token)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                action_user=self.another_member
            ).content == "{} {} your post".format(self.another_member.username, 'dislikes')
        )

    def test_notiication_create_a_comment(self):
        self.reset_notifications_count_for_all()

        # Create a comment
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        comment_id = self.client.post(url, {"content": "another comment"}, HTTP_AUTHORIZATION=self.another_member_token).data.get('data', {}).get('id', '')
        comment = Comment.objects.get(id=comment_id)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).content == "{} commented on your post".format(self.another_member.username)
        )

    def test_notiication_create_another_comment(self):
        self.reset_notifications_count_for_all()

        # Create a comment
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        self.client.post(url, {"content": "first comment"}, HTTP_AUTHORIZATION=self.creator_token).data.get('data', {}).get('id', '')

        # Create another comment
        comment_id = self.client.post(url, {"content": "another comment"}, HTTP_AUTHORIZATION=self.another_member_token).data.get('data', {}).get('id', '')
        comment = Comment.objects.get(id=comment_id)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                user_id=self.dummy_member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 2
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.superuser.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).content == "{} commented on your post".format(self.another_member.username)
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).content == "{} commented on a post that you also commented".format(self.another_member.username)
        )

    def test_notification_like_a_comment(self):
        # Create a comment
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        comment_id = self.client.post(url, {"content": "testing comment"}, HTTP_AUTHORIZATION=self.member_token).data.get('data', {}).get('id', '')
        comment = Comment.objects.get(id=comment_id)

        self.reset_notifications_count_for_all()

        self.client.post("{}/comment/{}/likes/".format(url_prefix, comment.id),
            {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.another_member_token)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).content == "{} {} your comment".format(self.another_member.username, 'likes')
        )

    def test_notification_dislike_a_comment(self):
        # Create a comment
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        comment_id = self.client.post(url, {"content": "testing comment"}, HTTP_AUTHORIZATION=self.member_token).data.get('data', {}).get('id', '')
        comment = Comment.objects.get(id=comment_id)

        self.reset_notifications_count_for_all()

        self.client.post("{}/comment/{}/likes/".format(url_prefix, comment.id),
            {"like_or_dislike": False}, HTTP_AUTHORIZATION=self.another_member_token)

        self.assertTrue(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.member.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=self.member,
                group_id=self.group_id,
                post_id=self.post.id,
                comment_id=comment.id,
                action_user=self.another_member
            ).content == "{} {} your comment".format(self.another_member.username, 'dislikes')
        )

    def test_notification_add_to_group(self):
        self.reset_notifications_count_for_all()

        # Create a member
        username = "powerwolf"
        email = "man@of.war"
        password = "sa_ba_ton?"
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)

        url = "{}/group/{}/user/{}/".format(url_prefix, self.group.id, user.id)
        response = self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        self.assertTrue(
            Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=user.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.superuser.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).content == 'You have been added to group {}'.format(self.group.name)
        )

    def test_notification_remove_from_group(self):
        self.reset_notifications_count_for_all()

        # Create a member
        username = "powerwolf"
        email = "man@of.war"
        password = "sa_ba_ton?"
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)
        self.group.add_member(user)

        url = "{}/group/{}/user/{}/".format(url_prefix, self.group.id, user.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        self.assertTrue(
            Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                user_id=self.superuser,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                user_id=self.member.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            )) == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=user.id,
            ).number_of_unseen == 1
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.superuser.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=self.another_member.id,
            ).number_of_unseen == 0
        )

        self.assertTrue(
            Notification.objects.get(
                user_id=user.id,
                group_id=self.group_id,
                post_id__isnull=True,
                comment_id__isnull=True,
                action_user__isnull=True
            ).content == 'You have been removed from group {}'.format(self.group.name)
        )

    def test_get_all_notifications(self):
        self.reset_notifications_count_for_all()

        # Create a member
        username = "powerwolf"
        email = "man@of.war"
        password = "sa_ba_ton?"
        user = User.objects.create_user(username=username, email_address=email, password=password)
        token = self.get_token(user)

        # Add the user to group
        self.client.post("{}/group/{}/user/{}/".format(url_prefix, self.group.id, user.id), HTTP_AUTHORIZATION=self.creator_token)

        # The user create a post
        response = self.client.post("{}/group/{}/posts/".format(url_prefix, self.group_id),
                            {"content": "testing 2 content", "link": "http://ogp.me"}, HTTP_AUTHORIZATION=token)
        post = Post.objects.get(id=response.data.get('data', {}).get('id', ''))

        # A member like the user's post
        url = "{}/post/{}/likes/".format(url_prefix, post.id)
        self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.member_token)

        # Another member comment in the post
        url = "{}/post/{}/comments/".format(url_prefix, post.id)
        comment_id = self.client.post(url, {"content": "another comment"}, HTTP_AUTHORIZATION=self.another_member_token).data.get('data', {}).get('id', '')
        comment = Comment.objects.get(id=comment_id)

        response = self.client.get(url_prefix + '/notifications/', HTTP_AUTHORIZATION=token)
        self.assertEqual(200, response.status_code)

        self.assertTrue(
            Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id
            ).exists()
        )

        self.assertTrue(
            len(Notification.objects.filter(
                user_id=user.id,
                group_id=self.group_id
            )) == 3
        )

        self.assertTrue(
            NotificationUser.objects.get(
                user_id=user.id,
            ).number_of_unseen == 3
        )
