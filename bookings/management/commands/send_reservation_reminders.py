from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Reservation, NotificationLog

class Command(BaseCommand):
    help = 'Envía notificaciones SMS a anfitriones e invitados 24h, 12h y 1h antes de la reunión.'

    def send_sms(self, user, message):
        """
        Función simulada para enviar SMS. 
        En producción, integrar con Twilio, AWS SNS, etc.
        """
        if not user.phone_number:
            return False
        
        full_number = f"{user.country_code}{user.phone_number}"
        
        # --- AQUÍ IRÍA LA LÓGICA REAL DE ENVÍO ---
        self.stdout.write(self.style.SUCCESS(f"[SIMULACRO SMS] Enviando a {full_number}: {message}"))
        return True

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Filtramos reservas activas cuya fecha es mayor o igual a hoy
        reservations = Reservation.objects.filter(is_active=True, date__gte=now.date())
        
        for res in reservations:
            # Construir el datetime exacto de inicio de la reserva
            # Res.date es DateField, Res.start_time es TimeField
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(res.date, res.start_time)
            )
            
            time_until = start_datetime - now
            hours_until = time_until.total_seconds() / 3600.0
            
            # Chequeamos si la reserva ya pasó
            if hours_until <= 0:
                continue
                
            notification_type = None
            
            if 23.5 <= hours_until <= 24.5:
                notification_type = '24H'
            elif 11.5 <= hours_until <= 12.5:
                notification_type = '12H'
            elif 0.5 <= hours_until <= 1.5:
                notification_type = '1H'
                
            if notification_type:
                # Recopilar todos a los que hay que avisar (Anfitrión + Invitados Confirmados)
                users_to_notify = [res.user]
                for attendance in res.attendances.all():
                    users_to_notify.append(attendance.user)
                
                for user in users_to_notify:
                    # Chequear si ya se envió este tipo de notificación
                    already_sent = NotificationLog.objects.filter(
                        reservation=res,
                        user=user,
                        notification_type=notification_type
                    ).exists()
                    
                    if not already_sent:
                        message = f"Recordatorio: Tienes una reunión en {res.work_area.name} el {res.date} a las {res.start_time}. Faltan {notification_type.replace('H', ' horas')}."
                        if notification_type == '1H':
                            message = f"Recordatorio: Tu reunión en {res.work_area.name} es en 1 hora."
                            
                        # Intentar enviar
                        if self.send_sms(user, message):
                            NotificationLog.objects.create(
                                reservation=res,
                                user=user,
                                notification_type=notification_type
                            )
                            self.stdout.write(f"Log guardado: {notification_type} para {user.username}")
