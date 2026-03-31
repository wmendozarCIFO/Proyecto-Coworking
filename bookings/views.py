from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Reservation, WorkArea
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
import datetime

@login_required
def booking_calendar(request):
    # Mostrar los próximos 14 días
    today = timezone.localdate()
    dates = [today + datetime.timedelta(days=i) for i in range(14)]
    return render(request, 'bookings/calendar.html', {'dates': dates})

@login_required
def booking_slots(request, date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Definir horario de trabajo 9:00 a 18:00
    start_hour = 9
    end_hour = 18
    slots = []
    
    # Asumiendo franjas horarias de una hora
    for h in range(start_hour, end_hour):
        start_time = datetime.time(h, 0)
        end_time = datetime.time(h + 1, 0)
        
        # Verificar disponibilidad para cada área de trabajo
        areas = WorkArea.objects.all()
        area_slots = []
        for area in areas:
            # Contar reservas
            count = Reservation.objects.filter(
                date=date,
                start_time=start_time,
                work_area=area,
                is_active=True
            ).count()
            
            if count < area.capacity:
                area_slots.append({
                    'area': area,
                    'available': True
                })
        
        if area_slots:
            slots.append({
                'start': start_time,
                'end': end_time,
                'areas': area_slots
            })

    return render(request, 'bookings/slots.html', {'date': date, 'slots': slots})

@login_required
def book_slot(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        area_id = request.POST.get('area_id')
        
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S').time()
        # la hora de fin es inicio + 1 hora según la lógica
        end_time = (datetime.datetime.combine(date, start_time) + datetime.timedelta(hours=1)).time()
        
        area = get_object_or_404(WorkArea, id=area_id)
        
        # Verificar capacidad nuevamente
        count = Reservation.objects.filter(
            date=date,
            start_time=start_time,
            work_area=area,
            is_active=True
        ).count()
        
        if count >= area.capacity:
            messages.error(request, 'Lo sentimos, este cupo acaba de ocuparse.')
            return redirect('booking_calendar')
            
        reservation = Reservation.objects.create(
            user=request.user,
            work_area=area,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        
        # Enviar correo electrónico
        cancel_url = request.build_absolute_uri(reverse('cancel_booking', args=[reservation.id]))
        send_mail(
            'Confirmación de Reserva - Coworking',
            f'Hola {request.user.first_name},\n\nTu reserva para el {date} de {start_time} a {end_time} en {area.name} está confirmada.\n\nPara cancelar: {cancel_url}',
            'noreply@coworking.com',
            [request.user.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Reserva confirmada. Se ha enviado un correo con los detalles.')
        return redirect('user_dashboard')
        
    return redirect('booking_calendar')

@login_required
def cancel_booking(request, booking_id):
    reservation = get_object_or_404(Reservation, id=booking_id)
    
    # Permitir cancelar al administrador o al propietario
    if request.user == reservation.user or request.user.is_staff:
        reservation.is_active = False
        reservation.save()
        
        # Enviar correo de cancelación
        send_mail(
            'Cancelación de Reserva - Coworking',
            f'Hola {reservation.user.first_name},\n\nTe confirmamos que tu reserva para el {reservation.date} de {reservation.start_time} a {reservation.end_time} en {reservation.work_area.name} ha sido cancelada correctamente.\n\nSaludos.',
            'noreply@coworking.com',
            [reservation.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Reserva cancelada correctamente.')
        if request.user.is_staff:
            return redirect('admin_bookings')
        else:
            return redirect('user_dashboard')
    else:
        messages.error(request, 'No tienes permiso para cancelar esta reserva.')
        
    return redirect('user_dashboard')

from .forms import WorkAreaForm

@user_passes_test(lambda u: u.is_staff)
def admin_bookings(request):
    reservations = Reservation.objects.all().order_by('-date')
    return render(request, 'bookings/admin_list.html', {'reservations': reservations})

@user_passes_test(lambda u: u.is_staff)
def admin_work_areas(request):
    areas = WorkArea.objects.all()
    return render(request, 'bookings/admin_work_areas.html', {'areas': areas})

@user_passes_test(lambda u: u.is_staff)
def admin_work_area_add(request):
    if request.method == 'POST':
        form = WorkAreaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área de trabajo creada con éxito.')
            return redirect('admin_work_areas')
    else:
        form = WorkAreaForm()
    return render(request, 'bookings/admin_work_area_form.html', {'form': form, 'action': 'Crear'})

@user_passes_test(lambda u: u.is_staff)
def admin_work_area_edit(request, area_id):
    area = get_object_or_404(WorkArea, id=area_id)
    if request.method == 'POST':
        form = WorkAreaForm(request.POST, request.FILES, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área de trabajo actualizada con éxito.')
            return redirect('admin_work_areas')
    else:
        form = WorkAreaForm(instance=area)
    return render(request, 'bookings/admin_work_area_form.html', {'form': form, 'action': 'Editar'})

@user_passes_test(lambda u: u.is_staff)
def admin_work_area_delete(request, area_id):
    area = get_object_or_404(WorkArea, id=area_id)
    if request.method == 'POST':
        area.delete()
        messages.success(request, 'Área de trabajo eliminada.')
        return redirect('admin_work_areas')
    return render(request, 'bookings/admin_work_area_confirm_delete.html', {'area': area})
