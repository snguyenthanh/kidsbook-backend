from profanity import profanity
profanity.set_censor_characters("*")

def clean_data(data, *args):
  for field in args:
    data.pop(field, None)
  return data

def clean_data_iterative(data, *args):
  for row in data:
    for field in args:
      row.pop(field, None)
  return data

def censor(text: str):
    return profanity.censor(text)
