import random

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.mail import EmailMessage  # for sending verification using e-mail
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render


def display_index(request):
    return render(request, 'main/index.html')


def display_form(request):
    return render(request, 'main/form.html')
