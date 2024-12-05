from django import forms
from .models import Comentario, EntradaBlog, Monster, Element, Ailment, Game, MonsterType

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
    elements = forms.ModelMultipleChoiceField(
        queryset=Element.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona los elementos del monstruo"
    )
    
    ailments = forms.ModelMultipleChoiceField(
        queryset=Ailment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona los estados que puede causar"
    )
    
    weaknesses = forms.ModelMultipleChoiceField(
        queryset=Element.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona las debilidades del monstruo"
    )
    
    game = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Selecciona el juego donde aparece el monstruo"
    )
    
    danger_level = forms.IntegerField(
        min_value=1,
        max_value=9,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Nivel de peligro (1-9 estrellas)"
    )

    class Meta:
        model = EntradaBlog
        fields = [
            'nombre', 
            'tipo', 
            'descripcion', 
            'resumen', 
            'imagen',
            'game',
            'elements',
            'ailments',
            'weaknesses',
            'danger_level'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del monstruo'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descripción detallada del monstruo'
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Breve resumen para las listas'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            })
        } 