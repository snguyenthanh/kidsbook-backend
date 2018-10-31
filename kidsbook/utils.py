from kidsbook.models import *

def clean_data(data, *args):
  for field in args:
    data.pop(field, None)
  return data

def clean_data_iterative(data, *args):
  for row in data:
    for field in args:
      row.pop(field, None)
  return data

def usage_time(user):
  arr = []
  for i in range(7):
    day = (datetime.datetime.now() - datetime.timedelta(days=i)).date()
    if(ScreenTime.objects.filter(user=user, date=day)):
      time = ScreenTime.objects.get(user=user, date=day).total_time
    else:
      time = 0
    arr.append(time)
  return arr