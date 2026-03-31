from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.booking_calendar, name='booking_calendar'),
    path('slots/<str:date_str>/', views.booking_slots, name='booking_slots'),
    path('book/', views.book_slot, name='book_slot'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('cancel_attendance/<int:attendance_id>/', views.cancel_attendance, name='cancel_attendance'),
    path('join/<uuid:token>/', views.join_reservation, name='join_reservation'),
    path('admin/list/', views.admin_bookings, name='admin_bookings'),

    # Rutas CRUD de Areas de trabajo para administradores
    path('admin/areas/', views.admin_work_areas, name='admin_work_areas'),
    path('admin/areas/add/', views.admin_work_area_add, name='admin_work_area_add'),
    path('admin/areas/edit/<int:area_id>/', views.admin_work_area_edit, name='admin_work_area_edit'),
    path('admin/areas/delete/<int:area_id>/', views.admin_work_area_delete, name='admin_work_area_delete'),
]
