from django import forms
from django.contrib.auth.models import User

class AddContactForm(forms.Form):
    username_or_email = forms.CharField(max_length=150, label="Username or Email")

    def clean_username_or_email(self):
        data = self.cleaned_data['username_or_email']
        try:
            user = User.objects.get(username=data)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=data)
            except User.DoesNotExist:
                raise forms.ValidationError("User not found")
        return user