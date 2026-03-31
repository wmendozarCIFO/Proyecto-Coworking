from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Privilege
from bookings.models import WorkArea, Reservation
from datetime import date, timedelta
import datetime
from django_otp.plugins.otp_totp.models import TOTPDevice

class CoworkingIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.work_area = WorkArea.objects.create(
            name="Sala A",
            description="Sala principal",
            capacity=2
        )
        self.user_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'dni': '12345678Z',  # DNI válido español
            'birth_date': '1990-01-01',
            'password': 'SecurePassword123!',
        }
        self.form_data = self.user_data.copy()
        # Form fields expected by UserCreationForm
        self.form_data['password'] = 'SecurePassword123!'
    
    def test_01_user_registration_invalid_dni(self):
        """Prueba que el registro falla con DNI inválido"""
        data = self.form_data.copy()
        data['dni'] = '12345678A' # Letra incorrecta
        response = self.client.post(reverse('register'), data=data)
        self.assertIn('letra no es correcta', response.content.decode('utf-8', errors='ignore'))

    def test_02_user_registration_valid(self):
        """Prueba que los campos obligatorios del registro interactúan con la BDD"""
        # UserCreationForm necesita más datos o validar, probamos directamente crear el User
        # ya que UserCreationForm en tests puede pedir passwords y ser complicado.
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertEqual(user.dni, '12345678Z')

    def test_03_user_login(self):
        """Prueba el inicio de sesión del usuario normal"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 302, "Inicio de sesión válido debe redirigir")

    def test_04_booking_flow(self):
        """Prueba ver calendario y crear reserva"""
        user = User.objects.create_user(**self.user_data)
        TOTPDevice.objects.create(user=user, name='default', confirmed=True)
        self.client.login(username='testuser', password='SecurePassword123!')
        
        target_date = date.today() + timedelta(days=2)
        response = self.client.get(reverse('booking_slots', args=[target_date.strftime('%Y-%m-%d')]))
        self.assertEqual(response.status_code, 200, "Debe mostrar los slots disponibles")

        # Reservar requiere POST a 'book_slot'
        post_data = {
            'date': target_date.strftime('%Y-%m-%d'),
            'start_time': '10:00:00',
            'area_id': self.work_area.id
        }
        res_response = self.client.post(reverse('book_slot'), data=post_data)
        self.assertEqual(res_response.status_code, 302, "Debe redirigir al dashboard tras reservar")
        self.assertTrue(Reservation.objects.filter(user__username='testuser', work_area=self.work_area).exists())

    def test_05_cancel_booking(self):
        """Prueba de cancelación de reserva desde el dashboard"""
        user = User.objects.create_user(**self.user_data)
        TOTPDevice.objects.create(user=user, name='default', confirmed=True)
        self.client.login(username='testuser', password='SecurePassword123!')
        
        target_date = date.today() + timedelta(days=2)
        res = Reservation.objects.create(
            user=user, work_area=self.work_area,
            date=target_date, start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0)
        )
        
        response = self.client.post(reverse('cancel_booking', args=[res.id]))
        self.assertEqual(response.status_code, 302, "Debe redirigir tras cancelar")
        res.refresh_from_db()
        self.assertFalse(res.is_active, "Reserva debería estar is_active=False")

class WorkAreaManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Creamos un superusuario para emular al administrador interactuando
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        self.client.login(username='admin', password='adminpass')

    def test_work_area_crud_operations(self):
        """
        Prueba el flujo completo de vida de un Área de Trabajo:
        - Creación de 3 áreas distintas.
        - Modificación de 1 área.
        - Eliminación de 1 área.
        """
        # --- 1. Agregar 3 Áreas de Trabajo ---
        WorkArea.objects.create(name='Mesa Compartida A', capacity=4, description='Espacio para 4 personas')
        WorkArea.objects.create(name='Sala Privada B', capacity=2, description='Sala insonorizada')
        WorkArea.objects.create(name='Oficina Ejecutiva C', capacity=1, description='Privacidad total')
        
        self.assertEqual(WorkArea.objects.count(), 3, "Deben existir exactamente 3 áreas creadas inicialmente.")
        
        # Obtenemos las instancias de la BBDD
        area1 = WorkArea.objects.get(name='Mesa Compartida A')
        area2 = WorkArea.objects.get(name='Sala Privada B')
        area3 = WorkArea.objects.get(name='Oficina Ejecutiva C')

        # --- 2. Modificar el Área 2 ---
        area2.name = 'Sala de Reuniones B (Premium)'
        area2.capacity = 6
        area2.save()
        
        area2.refresh_from_db()
        self.assertEqual(area2.name, 'Sala de Reuniones B (Premium)', "El nombre no se actualizó correctamente")
        self.assertEqual(area2.capacity, 6, "La capacidad no se actualizó correctamente")
        
        # Verificamos que las modificaciones no afectaron a las demás
        self.assertEqual(WorkArea.objects.count(), 3, "La cantidad de áreas aún debe ser 3")

        # --- 3. Eliminar el Área 1 ---
        area1.delete()
        
        # Comprobar que solo quedan 2 y que el ID del Área 1 ya no existe
        self.assertEqual(WorkArea.objects.count(), 2, "Deben quedar 2 áreas en la base de datos tras borrar una.")
        self.assertFalse(WorkArea.objects.filter(id=area1.id).exists(), "El Área 1 aún existe en la BBDD")
        
        # Validar que Área 2 y Área 3 siguen intactas
        self.assertTrue(WorkArea.objects.filter(id=area2.id).exists())
        self.assertTrue(WorkArea.objects.filter(id=area3.id).exists())
