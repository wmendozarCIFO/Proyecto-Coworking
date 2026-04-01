from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_spanish_id

class Privilege(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Privilegio'
        verbose_name_plural = 'Privilegios'

class User(AbstractUser):
    dni = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[validate_spanish_id],
        help_text="DNI, NIE o NIF válido"
    )
    birth_date = models.DateField(null=True, blank=True)
    
    country_code = models.CharField(max_length=5, default='+34', help_text="Indicativo de país (ej. +34)")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Número de teléfono móvil")
    
    # Usamos una referencia de cadena para evitar importaciones circulares si WorkArea está en otra aplicación
    # Idealmente, si WorkArea es un concepto central, debería pertenecer aquí o en una aplicación 'core'.
    # Por ahora, permitiré que sea nulo.
    work_area = models.ForeignKey(
        'bookings.WorkArea', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    privilege = models.ForeignKey(
        Privilege,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Jerarquía de usuario"
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
