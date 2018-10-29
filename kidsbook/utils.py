from django.conf import settings
import requests

def clean_data(data, *args):
    for field in args:
        data.pop(field, None)
    return data

def clean_data_iterative(data, *args):
    for row in data:
        for field in args:
            row.pop(field, None)
    return data

def push_notification(**kargs):
    kargs['secretKey'] = getattr(settings, "NOTIFICATION_SECRET_KEY", None)
    url = getattr(settings, "NOTIFICATION_ENDPOINT", None)

    response = requests.post(url, data=kargs)
    
