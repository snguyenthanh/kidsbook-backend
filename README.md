# Backend API Documentation
[![Build Status](https://travis-ci.org/Ang-YC/kidsbook-backend.svg?branch=master)](https://travis-ci.org/Ang-YC/kidsbook-backend)

Please update this document when there are any updates.

# Notes

## 1. URLs
The prefix for all requests is */api/v1/*.
All requests must end with a slash `/`.

Any endpoints having empty description indicates either not implemented or currently being developed.

## 2. Authentication

The format of the authentication token is `Bearer <token>`, where `token` is returned from [/user/login/](#1-user).

## 3. Response
Unsuccessful responses will have a key `error` containing the error message.
Successful responses will have a key `data` containing the requested info.

## 4. Common HTTP status codes

Status Code | Method | Description
--- | --- | --- |
200 | `GET` | For ALL successful `GET` requests.
202 | `POST` | For ALL successful `POST` requests.
301 | `GET`, `POST`, `DELETE` | Missing a suffix slash `/`.
400 | `GET`, `POST`, `DELETE` | Caused by an internal error. The error message is returned in `response.data.data`.
401 | `GET`, `POST`, `DELETE` | Caused by missing an authentication token.
403 | `GET`, `POST`, `DELETE` | The sender does not has permissions to perform this action. Handled by permission checks.
404 | `GET`, `POST`, `DELETE` | URL not found.
405 | `GET`, `POST`, `DELETE` | The sender does not has permissions to perform this action. Handled by custom logic.

# Web API References

Column `Arguments` refers to the keyword arguments in the requests' body.

## 1. User

`*` in column `Arguments` refers the fields of [User model](./kidsbook/models.py#L97-L125).

Method | Endpoint | Arguments | Description | Permissions | Return
--- | --- | --- | --- | --- | --- |
`GET` | /user/<user_id>/ | | Get the user's information. | IsAuthenticated | User: *dict*
`GET` | /user/<user_id>/groups/ | | Get all the groups the user is in. | IsAuthenticated | User: *list*
`GET` | /user/posts/ | | Get all posts created by the current user. | IsAuthenticated | User: *list*
`POST` | /user/login/ | email_address, password | Return an authentication token for the user. | AllowAny | {data: {name: '', token: ''}}
`POST` | /user/login_as_virtual/ | email_address | Return an authentication for the `virtual` user. | IsAuthenticated, IsSuperUser | {data: {name: '', token: ''}}
`POST` | /user/register/ | * | Create an user using the given arguments. | IsAuthenticated, IsSuperUser | User: *dict*
`GET` | /user/virtual_users/ | | Get all `virtual` users created by the requester. | IsAuthenticated, IsSuperUser | User: *list*
`POST` | /user/logout/ | | Disable the requester's token. | IsAuthenticated | {}
`POST` | /user/update/<user_id/ | * | Update an user using the given arguments. | IsAuthenticated. The requester must be either the creator of the user or the user himself. | User: *dict*

## 2. Post
`*` in column `Arguments` refers the fields of [the return model](./kidsbook/models.py).

Method | Endpoint | Arguments | Description | Permissions | Return
--- | --- | --- | --- | --- | --- |
`GET` | /group/<group_id>/posts/ | | Get all posts in the group. | IsAuthenticated, IsInGroup | Post: *list*
`POST` | /group/<group_id>/posts/ | * | Create a post in the group. | IsAuthenticated, IsInGroup | Post: *dict*
`GET` | /post/<post_id>/ | | Get post's details by ID. | IsAuthenticated, HasAccessToPost | Post: *dict*
`POST` | /post/<post_id>/ | * | Update the post. | IsAuthenticated, HasAccessToPost | Post: *dict*
`DELETE` | /post/<post_id>/ | * | Delete the post. | IsAuthenticated, HasAccessToPost | {}
`GET` | /post/<post_id>/likes/ | | Get all likes/dislikes of the post. | IsAuthenticated, HasAccessToPost | UserLikePost: *list*
`POST` | /post/<post_id>/likes/ | like_or_dislike: *bool* | Like/dislike the post. | IsAuthenticated, HasAccessToPost | UserLikePost: *dict*
`GET` | /post/<post_id>/shares/ | | Get all shares of the post. | IsAuthenticated, HasAccessToPost | UserSharePost: *list*
`POST` | /post/<post_id>/shares/ | | User `shares` the post.  | IsAuthenticated, HasAccessToPost | UserSharePost: *dict*
`GET` | /post/<post_id>/comments/ | | Get all comments of the post. | IsAuthenticated, HasAccessToPost | Comment: *list*
`POST` | /post/<post_id>/comments/ | content:*str* | Create a comment for the post. | IsAuthenticated, HasAccessToPost | Comment: *dict*
`GET` | /post/<post_id>/flags/ | | Get all flags of the post. | IsAuthenticated, HasAccessToPost | UserFlagPost: *list*
`POST` | /post/<post_id>/flags/ | status:*str* | Create a flag for the post. | IsAuthenticated, HasAccessToPost | UserFlagPost: *dict*
`GET` | /comment/<comment_id>/ | | Get comment's details by ID. | IsAuthenticated, HasAccessToComment | Comment: *dict*
`POST` | /comment/<comment_id>/ | content:*str* | Update the comment. | IsAuthenticated, HasAccessToComment | Comment: *dict*
`DELETE` | /comment/<comment_id>/ | | Delete the comment. | IsAuthenticated, HasAccessToComment | {}
`GET` | /comment/<comment_id>/likes/ | | Get the likes/dislikes of the comment. | IsAuthenticated, HasAccessToComment | UserLikeComment: *list*
`POST` | /comment/<comment_id>/likes/ | like_or_dislike:*bool* | User likes/dislikes a comment. | IsAuthenticated, HasAccessToComment | UserLikeComment: *dict*
`GET` | /comment/<comment_id>/flags/ | | Get the flags of the comment. | IsAuthenticated, HasAccessToComment | UserFlagPost: *list*
`POST` | /comment/<comment_id>/flags/ | status:*str* | Create a flag for the comment. | IsAuthenticated, HasAccessToComment | UserFlagPost: *dict*

## 3. Group
`*` in column `Arguments` refers the fields of [Group model](./kidsbook/models.py#L165-L173).

Method | Endpoint | Arguments | Description | Permissions | Return
--- | --- | --- | --- | --- | --- |
`GET` | /group/ | | Get all groups. | IsAuthenticated, IsSuperUser | Group: *list*
`POST` | /group/ | * | Create a group. | IsAuthenticated, IsSuperUser | Group: *dict*
`GET` | /group/<group_id>/ | | Get the group's details. | IsAuthenticated, IsInGroup | Group: *dict*
`GET` | /group/<group_id>/users/ | | Get all members in the group. | IsAuthenticated, IsInGroup | User:*list*
`POST` | /group/<group_id>/user/<user_id>/ | | Add the user to the group. | IsAuthenticated, IsGroupCreator | {}
`DELETE` | /group/<group_id>/user/<user_id>/ | | Remove the user to the group. | IsAuthenticated, IsGroupCreator | {}
`DELETE` | /group/<group_id>/delete/ | | Remove the group. | IsAuthenticated, IsGroupCreator| {}

## 4. Batch
A keyword argument `file_name` is required by [FileUploadParser](https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser).

A header row is required for the `.csv` files. Empty `is_superuser` and `gender` will default to 0.

An example `.csv` file:
```
username,email_address,password,realname,gender,is_superuser
chris,chris@email.com,password_for_kris,Christiana Messi,0,
james,james@email.com,password_for_kris,Christiana Messi,1,1
ama,ama@email.com,ama_pwd,Ama Johnson,1,0
```

Method | Endpoint | Arguments | Description | Permissions | Return
--- | --- | --- | --- | --- | --- |
`POST` | /batch/create/user/<file_name>/ | file | Create users from the uploaded file. | IsAuthenticated, IsSuperUser | {}
