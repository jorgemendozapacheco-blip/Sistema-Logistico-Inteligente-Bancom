from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'username',
            # No placeholder
        }),
        error_messages={'required': 'Por favor, ingrese su usuario.'}
    )
    password = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
            # No placeholder
        }),
        error_messages={'required': 'Por favor, ingrese su contraseña.'}
    )
