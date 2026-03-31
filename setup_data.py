import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coworking_project.settings')
django.setup()
from bookings.models import WorkArea
if not WorkArea.objects.filter(name='Mesa Principal').exists():
    WorkArea.objects.create(name='Mesa Principal', capacity=5)
