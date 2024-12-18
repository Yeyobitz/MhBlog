from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    role = forms.CharField(widget=forms.HiddenInput(), required=False, initial='normal')
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.cleaned_data.get('role') == 'moderador':
                user.profile.role = 'moderador'
                user.profile.save()
        return user 