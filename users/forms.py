from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from .models import User
from bookings.models import WorkArea

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellidos", max_length=150)
    dni = forms.CharField(label="DNI/NIE/NIF", max_length=20, help_text="Formato válido español (ej. 12345678Z)")
    birth_date = forms.DateField(label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date'}))
    work_area = forms.ModelChoiceField(queryset=WorkArea.objects.all(), required=False, label="Área de Trabajo Preferida")
    email = forms.EmailField(label="Correo Electrónico", required=True)
    
    terms_accepted = forms.BooleanField(
        required=True,
        label=mark_safe('He leído y acepto la <a href="/politica-privacidad/" target="_blank">Política de Privacidad</a> y los <a href="/terminos-condiciones/" target="_blank">Términos y Condiciones</a>.'),
        error_messages={'required': 'Debes aceptar la política de privacidad y los términos para registrarte.'}
    )
    news_accepted = forms.BooleanField(
        required=False,
        label="Deseo recibir comunicaciones comerciales y novedades."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'dni', 'first_name', 'last_name', 'birth_date', 'work_area')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'dni', 'birth_date', 'email', 'work_area']

