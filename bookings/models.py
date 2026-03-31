from django.db import models
from django.conf import settings

class WorkArea(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='work_areas/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Area de Trabajo'
        verbose_name_plural = 'Areas de Trabajo'

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE, related_name='reservations')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Estado simple para manejar la cancelación
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.work_area} - {self.date}"

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'
        ordering = ['-date', '-start_time']
