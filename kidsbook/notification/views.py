from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics

from kidsbook.serializers import *
from kidsbook.models import *
from kidsbook.permissions import *


User = get_user_model()

def get_notifications(request):
    """
    Notifications are created when:
    - A group that the user is in has new posts.
    - The post of  the user has 1 more like/dislike.
    - The comment of  the user has 1 more like/dislike.
    - Another user comments on the user's post.
    - Another user comments on a post that the user comments.
    - The user is added to a group.
    - The user is removed from a group.
    """

    try:
        requester_id = request.user.id
        notifications = Notification.objects.filter(user_id=requester_id).order_by('-created_at')
        if len(notifications) > 50:
            notifications = notifications[:50]

        number_of_unseen = NotificationUser.objects.get(user_id=requester_id).number_of_unseen
    except Exception as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = NotificationSerializer(notifications, many=True)
    return Response({'data': serializer.data, 'unseen': number_of_unseen})

def reset_unseen_notification_count(request):
    """Reset number_of_unseen notifications to 0."""

    try:
        noti_user = NotificationUser.objects.get(user_id=request.user.id)
        noti_user.number_of_unseen = 0
        noti_user.save()
    except Exception as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = NotificationUserSerializer(noti_user)
    return Response({'data': serializer.data}, status=status.HTTP_202_ACCEPTED)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsTokenValid))
def notification(request):
    """Return the last 50 notifications of the user or reset number_of_unseen notifications."""

    function_mappings = {
        'GET': get_notifications,
        'POST': reset_unseen_notification_count
    }
    if request.method in function_mappings:
        return function_mappings[request.method](request)
    return Response({'error': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)
