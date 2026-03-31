from django.core.management.base import BaseCommand
from users.models import User, Privilege
from bookings.models import WorkArea
from django_otp.plugins.otp_totp.models import TOTPDevice
import os

class Command(BaseCommand):
    help = 'Seeds database with initial data'

    def handle(self, *args, **options):
        # Crear áreas de trabajo
        areas = [
            {'name': 'Open Space', 'capacity': 20, 'description': 'Shared desk in open area'},
            {'name': 'Meeting Room A', 'capacity': 1, 'description': 'Private room for up to 6 people'},
            {'name': 'Private Office', 'capacity': 1, 'description': 'Private office for 1 person'},
        ]
        
        for a in areas:
            WorkArea.objects.get_or_create(name=a['name'], defaults=a)
            self.stdout.write(f"Created WorkArea: {a['name']}")

        # Crear administrador
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.dni = '00000000T' # Dummy valid DNI
            admin.save()
            
            # Configurar dispositivo 2FA
            device = TOTPDevice.objects.create(user=admin, name='default', confirmed=True)
            self.stdout.write(f"Created Admin user 'admin' with password 'adminpass'")
            self.stdout.write(f"2FA TOTP Device created.")
            
            # Token estático para pruebas fáciles
            from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
            static_device = StaticDevice.objects.create(user=admin, name='backup')
            token = StaticToken.objects.create(device=static_device, token='123456')
            self.stdout.write(f"Static 2FA Token created: '123456'")
        else:
            self.stdout.write("Admin user already exists")
            
        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))
