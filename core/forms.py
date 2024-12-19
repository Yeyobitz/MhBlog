from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegistroForm(UserCreationForm):
    is_moderator = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Asignar al grupo de moderadores si se activó el código Konami
            if self.cleaned_data.get('is_moderator'):
                moderators_group = Group.objects.get(name='Moderators')
                user.groups.add(moderators_group)
            else:
                usuarios_group = Group.objects.get(name='Usuarios')
                user.groups.add(usuarios_group)
        return user 

class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu nombre'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu correo electrónico'
    }))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Tu mensaje',
        'rows': 5
    }))