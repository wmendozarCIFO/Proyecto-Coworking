"""
URL configuration for coworking_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from core import views as core_views
from django.contrib.auth import views as auth_views
from two_factor.urls import urlpatterns as tf_urls

# Aplicamos nuestra regla de formulario limpio al Administrador por defecto de Django
admin.site.login_form = core_views.CustomOTPAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('register/', core_views.register, name='register'),
    path('login/', RedirectView.as_view(pattern_name='two_factor:login'), name='login'),
    path('', include(tf_urls)),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('dashboard/', core_views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', core_views.admin_users, name='admin_users'),
    path('admin-users/create/', core_views.admin_user_create, name='admin_user_create'),
    path('admin-users/edit/<int:user_id>/', core_views.admin_user_edit, name='admin_user_edit'),
    path('admin-users/delete/<int:user_id>/', core_views.admin_user_delete, name='admin_user_delete'),
    
    path('profile/', core_views.profile_edit, name='profile_edit'),
    path('profile/verify-2fa/', core_views.profile_verify_2fa, name='profile_verify_2fa'),
    
    path('bookings/', include('bookings.urls')),
]
