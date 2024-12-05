from django import forms
from .models import Comentario, EntradaBlog

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario aquí...'
            }),
        }

class EntradaBlogForm(forms.ModelForm):
    class Meta:
        model = EntradaBlog
        fields = ['nombre', 'tipo', 'descripcion', 'resumen', 'imagen', 'habitat']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'habitat': forms.Select(attrs={'class': 'form-control'}),
        } 