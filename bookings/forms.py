from django import forms
from .models import WorkArea

class WorkAreaForm(forms.ModelForm):
    class Meta:
        model = WorkArea
        fields = ['name', 'description', 'capacity', 'image']
        labels = {
            'name': 'Nombre del Área',
            'description': 'Descripción',
            'capacity': 'Capacidad (personas)',
            'image': 'Imagen'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción detallada...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Ej. Sala de Reuniones A'})
        }
