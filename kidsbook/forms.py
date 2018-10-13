from django import forms
from main.models import (
    User
)


class LoginForm(forms.ModelForm):
    class Meta:
      model = User
      fields = ['email_address', 'password']

    def validate_unique(self):
      pass  