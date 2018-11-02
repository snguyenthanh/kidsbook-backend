import json
import os
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from kidsbook.models import Post, Group, Comment, UserLikePost, UserSharePost, UserFlagPost, UserLikeComment
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
        self.user = User.objects.create_user(username=self.username, email_address=self.email, password=self.password)
        token = generate_token(self.user)
        self.user_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Member
        username = "not_hey"
        email = "not_kid@s.sss"
        password = "want_some_cookies?"
        member = User.objects.create_user(username=username, email_address=email, password=password)
        token = generate_token(member)
        self.member_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Create a Group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group_id = response.data.get('data', {}).get('id', '')
        Group.objects.get(id=self.group_id).add_member(member)

        #self.url = "{}/group/{}/".format(url_prefix, self.group_id)

        # Create a post
        self.post = Post.objects.create_post(
            content='Need someone to eat lunch at pgp?',
            creator=self.creator,
            group=Group.objects.get(id=self.group_id)
        )

        self.post2 = Post.objects.create_post(
            content='Another post',
            creator=self.creator,
            group=Group.objects.get(id=self.group_id)
        )

        # Create a comment
        self.comment = Comment.objects.create_comment(
            content='OKAY',
            post=self.post,
            creator=self.creator
        )

        # Create another comment
        self.another_comment = Comment.objects.create_comment(
            content='not okay at all',
            post=self.post,
            creator=self.creator
        )


    def changes_reflect_in_response(self, request_changes, previous_state, current_state):
        difference = { k : current_state[k] for k in set(current_state) - set(previous_state) }

        for key, prev_val in iter(previous_state.items()):
            # If the un-modified value changes
            if key not in request_changes and current_state.get(key, '') != prev_val:
                return False

            # If the un-modified value doesnt match
            if key in request_changes and isinstance(request_changes[key], str) and request_changes[key] != current_state.get(key, ''):
                return False
        return True

    def test_create_post_in_group(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            response = self.client.post(url, {"content": "testing content", "link": "http://ogp.me",
                "picture": pic}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertTrue(202, response.status_code)

        post_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            Post.objects.filter(id=post_id).exists()
        )

    def test_create_post_in_group_by_non_member(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            response = self.client.post(url, {"content": "testing content", "link": "http://ogp.me",
                "picture": pic}, HTTP_AUTHORIZATION=self.user_token)
        self.assertTrue(403, response.status_code)

    def test_create_post_in_group_without_token(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            response = self.client.post(url, {"content": "testing content", "link": "http://ogp.me",
                "picture": pic}, HTTP_AUTHORIZATION=self.user_token)
        self.assertTrue(401, response.status_code)

    def test_get_all_posts_in_group(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 2
        )

    def test_get_all_posts_in_group_include_deleted_with_all(self):
        # Delete a post
        url = "{}/post/{}/".format(url_prefix, self.post2.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/group/{}/posts/?all=true".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 2
        )

    def test_get_all_posts_in_group_include_deleted_with_all_by_non_superuser(self):
        # Delete a post
        url = "{}/post/{}/".format(url_prefix, self.post2.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/group/{}/posts/?all=true".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_get_posts_in_group_exclude_deleted_comments_in_top_3(self):
        # Delete a comment
        url = "{}/comment/{}/".format(url_prefix, self.another_comment.id)
        self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 2
        )
        
        second_post = response.data.get('data', [])[1]
        comments = second_post.get('comments', [])
        self.assertTrue(
            len(comments) == 1
        )
        self.assertTrue(
            comments[0].get('content') == 'OKAY'
        )

    def test_get_all_posts_in_group_exclude_deleted_with_all(self):
        # Delete a post
        url = "{}/post/{}/".format(url_prefix, self.post2.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/group/{}/posts/?all=false".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_get_all_posts_in_group_exclude_deleted(self):
        # Delete a post
        url = "{}/post/{}/".format(url_prefix, self.post2.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_get_all_post_in_group_by_non_member(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_post_in_group_without_token(self):
        url = "{}/group/{}/posts/".format(url_prefix, self.group_id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_get_post_detail_with_id(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_update_post_detail_with_id(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        prev_state = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token).data.get('data', {})

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../backend/media/picture.png'), 'rb') as pic:
            request_changes = {"content": "Changed content", "link": "http://ogp.me", "picture": pic}
            response = self.client.post(url, request_changes, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(202, response.status_code)

        # Check if the changes reflect in the `Post`
        new_state = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token).data.get('data', {})
        self.assertTrue(
            self.changes_reflect_in_response(request_changes, prev_state, new_state)
        )

    def test_update_post_by_non_creator(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.post(url,{"content": "Changed content"}, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_update_post_without_token(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.post(url,{"content": "Changed content"})
        self.assertEqual(401, response.status_code)

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
        self.assertTrue(
            len(response.data.get('data', [])) == 2
        )

    def test_get_all_comments_include_deleted(self):
        # Delete a comment
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/post/{}/comments/?all=TRUE".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

        self.assertTrue(
            len(response.data.get('data', [])) == 2
        )

    def test_get_all_comments_include_deleted_by_non_superuser(self):
        # Delete a comment
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/post/{}/comments/?all=TRUE".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_get_all_comments_of_post_exclude_deleted(self):
        # Delete a comment
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)


        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_get_all_comments_of_post_exclude_deleted_by_member_non_superuser(self):
        # Delete a comment
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)

        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)

        self.assertTrue(
            len(response.data.get('data', [])) == 1
        )

    def test_create_comment_of_post(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"content": "testing comment"}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        comment_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            Comment.objects.filter(id=comment_id).exists()
        )

    def test_create_comment_of_post_by_non_member(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"content": "Comment"}, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_create_comment_of_post_without_token(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"content": "Comment"})
        self.assertEqual(401, response.status_code)

    def test_get_all_comments_of_post_by_non_member(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_likes_of_post(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_likes_of_post_by_non_member(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_likes_of_post_without_token(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_like_post(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        like_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            UserLikePost.objects.filter(id=like_id).exists()
        )

    def test_like_post_by_non_member(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_like_post_without_token(self):
        url = "{}/post/{}/likes/".format(url_prefix, self.post.id)
        response = self.client.post(url, {"like_or_dislike": True})
        self.assertEqual(401, response.status_code)

    def test_get_all_shares_of_post(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_shares_of_post_by_non_member(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_shares_of_post_without_token(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_share_post(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.post(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        share_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            UserSharePost.objects.filter(id=share_id).exists()
        )

    def test_share_post_by_non_member(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.post(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_share_post_without_token(self):
        url = "{}/post/{}/shares/".format(url_prefix, self.post.id)
        response = self.client.post(url)
        self.assertEqual(401, response.status_code)

    def test_get_all_flags_of_post(self):
        url = "{}/post/{}/flags/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_flags_of_post_by_non_member(self):
        url = "{}/post/{}/flags/".format(url_prefix, self.post.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_flags_of_post_without_token(self):
        url = "{}/post/{}/flags/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_flag_post(self):
        url = "{}/post/{}/flags/".format(url_prefix, self.post.id)
        flag_status = "UNDER APPROVAL"
        response = self.client.post(url, {"status": flag_status}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        flag_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            UserFlagPost.objects.filter(id=flag_id).exists()
            and str(UserFlagPost.objects.get(id=flag_id).status) == flag_status
        )

    def test_get_all_comments_of_post_without_token(self):
        url = "{}/post/{}/comments/".format(url_prefix, self.post.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_get_all_likes_of_comment(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_likes_of_comment_by_non_member(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_likes_of_comment_without_token(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_like_comment(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        like_id = response.data.get('data', {}).get('id', '')
        self.assertTrue(
            UserLikeComment.objects.filter(id=like_id).exists()
        )

    def test_like_comment_by_non_member(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.post(url, {"like_or_dislike": True}, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_like_comment_by_non_member(self):
        url = "{}/comment/{}/likes/".format(url_prefix, self.comment.id)
        response = self.client.post(url, {"like_or_dislike": True})
        self.assertEqual(401, response.status_code)


    def test_get_all_flags_of_comment(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_all_flags_of_comment_by_non_member(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_all_flags_of_comment_without_token(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_flag_comment(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        flag_status = "UNDER APPROVAL"
        response = self.client.post(url, {"status": flag_status}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)
        flag_id = response.data.get('data', {}).get('id', '')

        self.assertTrue(
            UserFlagPost.objects.filter(id=flag_id).exists()
            and (UserFlagPost.objects.get(id=flag_id).status) == flag_status
        )

    def test_flag_2_comments_and_post(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        flag_status = "IN_PROGRESS"
        response = self.client.post(url, {"status": flag_status}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        url = "{}/comment/{}/flags/".format(url_prefix, self.another_comment.id)
        flag_status = "IN_PROGRESS"
        response = self.client.post(url, {"status": flag_status}, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        url = "{}/post/{}/flags/".format(url_prefix, self.post.id)
        flag_status = "IN_PROGRESS"
        response = self.client.post(url, {"status": flag_status}, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(202, response.status_code)


    def test_flag_comment_by_non_member(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        response = self.client.post(url, {"status": "UNDER APPROVAL"}, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_flag_comment_without_token(self):
        url = "{}/comment/{}/flags/".format(url_prefix, self.comment.id)
        response = self.client.post(url, {"status": "UNDER APPROVAL"})
        self.assertEqual(401, response.status_code)

    def test_get_comment_by_id(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_deleted_comment_by_superuser(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token)

        self.assertEqual(200, response.status_code)

    def test_get_deleted_comment_by_member_non_superuser(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(405, response.status_code)

    def test_update_comment_by_id(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        prev_state = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token).data.get('data', {})
        requested_changes = {"content": "Changed content"}
        response = self.client.post(url, requested_changes, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        cur_state = self.client.get(url, HTTP_AUTHORIZATION=self.creator_token).data.get('data', {})
        self.assertTrue(
            self.changes_reflect_in_response(requested_changes, prev_state, cur_state)
        )

    def test_update_comment_by_non_member(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        requested_changes = {"content": "Changed content"}
        response = self.client.post(url, requested_changes, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_update_comment_without_token(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        requested_changes = {"content": "Changed content"}
        response = self.client.post(url, requested_changes)
        self.assertEqual(401, response.status_code)

    def test_get_comment_by_id_by_non_member(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_get_comment_by_id_without_token(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.get(url)
        self.assertEqual(401, response.status_code)

    def test_delete_comment_by_id(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        # Delete is just to set the flag `is_deleted` to True
        self.assertTrue(
            Comment.objects.filter(id=self.comment.id).exists()
        )
        self.assertTrue(
            Comment.objects.get(id=self.comment.id).is_deleted
        )

    def test_delete_comment_by_non_member(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_delete_comment_without_token(self):
        url = "{}/comment/{}/".format(url_prefix, self.comment.id)
        response = self.client.delete(url)
        self.assertEqual(401, response.status_code)

    def test_delete_post_detail_by_id(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.creator_token)
        self.assertEqual(202, response.status_code)

        # Delete is just to set the flag `is_deleted` of the post to True
        self.assertTrue(
            Post.objects.filter(id=self.post.id).exists()
        )
        self.assertTrue(
            Post.objects.get(id=self.post.id).is_deleted
        )

    def test_delete_post_by_non_creator(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(403, response.status_code)

    def test_delete_post_without_token(self):
        url = "{}/post/{}/".format(url_prefix, self.post.id)
        response = self.client.delete(url)
        self.assertEqual(401, response.status_code)

class TestCensorship(APITestCase):
    def setUp(self):
        # Create a superuser
        username = "not_hey"
        email = "not_kid@s.sss"
        password = "want_some_cookies?"
        self.creator = User.objects.create_superuser(username=username, email_address=email, password=password)
        token = generate_token(self.creator)
        self.creator_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Create a member
        username = "bohemian"
        email = "snake@in_my.boot"
        password = "want_some_cookies?"
        self.member = User.objects.create_user(username=username, email_address=email, password=password)
        token = generate_token(self.member)
        self.member_token = 'Bearer {0}'.format(token.decode('utf-8'))

        # Create a Group
        response = self.client.post(url_prefix + '/group/', {"name": "testing group"}, HTTP_AUTHORIZATION=self.creator_token)
        self.group_id = response.data.get('data', {}).get('id', '')
        self.group = Group.objects.get(id=self.group_id)
        self.group.add_member(self.member)
        #self.url = "{}/group/{}/".format(url_prefix, self.group_id)

        # Create a post
        self.post = Post.objects.create_post(
            content='Stop talking shit, nigga',
            creator=self.creator,
            group=self.group
        )

        # Create a comment
        self.comment = Comment.objects.create_comment(
            content='Fuck you slut',
            post=self.post,
            creator=self.creator
        )

    def test_censor_post_from_superuser(self):
        response = self.client.get("{}/post/{}/".format(url_prefix, self.post.id), HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'Stop talking ****, *****',
            response.data.get('data', {}).get('content', '')
        )

    def test_censor_comment_from_superuser(self):
        response = self.client.get("{}/comment/{}/".format(url_prefix, self.comment.id), HTTP_AUTHORIZATION=self.member_token)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            '**** you ****',
            response.data.get('data', {}).get('content', '')
        )
