from django.conf import settings
import requests
import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

def clean_data(data, *args):
    for field in args:
        data.pop(field, None)
    return data

def clean_data_iterative(data, *args):
    for row in data:
        for field in args:
            row.pop(field, None)
    return data

def push_notification(send_data: dict):
    send_data['secretKey'] = getattr(settings, "NOTIFICATION_SECRET_KEY", None)
    url = getattr(settings, "NOTIFICATION_ENDPOINT", None)
    headers = {
        'application/json',
        'Connection': 'close'
    }
    
    try:
        response = requests.post(
                        url,
                        data=json.dumps(send_data, cls=UUIDEncoder),
                        headers=headers,
                        timeout=2       # 2 seconds
                    )
    except Exception:
        pass
