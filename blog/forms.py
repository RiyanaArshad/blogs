from django import forms
from django.contrib.auth.models import User
from .models import BlogAuthor

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = BlogAuthor
        fields = ['bio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({'class': 'form-control'}) 