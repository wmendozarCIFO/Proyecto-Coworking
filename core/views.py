from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q

from users.forms import UserRegistrationForm, UserUpdateForm
from django_otp.forms import OTPAuthenticationForm
from django_otp import match_token
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def home(request):
    return render(request, 'core/home.html')

def register(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenido {user.first_name}! Registro completado.')
            if next_url:
                return redirect(next_url)
            return redirect('user_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form, 'next': next_url})

class CustomOTPAuthenticationForm(OTPAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminamos por completo los campos innecesarios del formulario (Petición del usuario)
        if 'otp_device' in self.fields:
            del self.fields['otp_device']
        if 'otp_challenge' in self.fields:
            del self.fields['otp_challenge']

@login_required
def user_dashboard(request):
    reservations = request.user.reservations.all().order_by('-date')
    guest_attendances = request.user.guest_attendances.all().order_by('-reservation__date')
    return render(request, 'core/dashboard.html', {
        'reservations': reservations,
        'guest_attendances': guest_attendances
    })

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')

@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    User = get_user_model()
    query = request.GET.get('q')
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(dni__icontains=query) |
            Q(email__icontains=query)
        )
            
    return render(request, 'core/admin_users.html', {'users': users, 'query': query})

@user_passes_test(lambda u: u.is_staff)
def admin_user_delete(request, user_id):
    User = get_user_model()
    try:
        user_to_delete = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'El usuario que intentas administrar no existe o ya ha sido eliminado.')
        return redirect('admin_users')
    
    # Medida de seguridad: un administrador no puede borrarse a sí mismo
    if user_to_delete.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
        return redirect('admin_users')
        
    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, f'El usuario {user_to_delete.username} ha sido eliminado con éxito del sistema.')
        return redirect('admin_users')
        
    return render(request, 'core/admin_user_delete.html', {'user_to_delete': user_to_delete})

@user_passes_test(lambda u: u.is_staff)
def admin_user_create(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado con éxito.')
            return redirect('admin_users')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/admin_user_form.html', {'form': form, 'action': 'Crear'})

@user_passes_test(lambda u: u.is_staff)
def admin_user_edit(request, user_id):
    User = get_user_model()
    try:
        user_to_edit = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'El usuario que intentas editar no existe.')
        return redirect('admin_users')
        
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user_to_edit.username} actualizado con éxito.')
            return redirect('admin_users')
    else:
        form = UserUpdateForm(instance=user_to_edit)
    return render(request, 'core/admin_user_form.html', {'form': form, 'action': 'Editar', 'user_to_edit': user_to_edit})

@login_required
def profile_verify_2fa(request):
    """
    Pide el token 2FA al usuario antes de permitirle entrar a su perfil.
    """
    if request.method == 'POST':
        token = request.POST.get('token')
        device = match_token(request.user, token)
        if device:
            # Marcamos en la sesión que ya verificó el 2FA para el perfil
            request.session['2fa_verified_for_profile'] = True
            return redirect('profile_edit')
        else:
            messages.error(request, 'El código 2FA ingresado es incorrecto.')
            
    return render(request, 'core/profile_verify_2fa.html')

@login_required
def profile_edit(request):
    """
    Permite al usuario cambiar su correo y contraseña.
    Requiere haber validado el 2FA en esta sesión (a través de profile_verify_2fa).
    """
    if not request.session.get('2fa_verified_for_profile'):
        messages.info(request, 'Por seguridad, debes verificar tu código 2FA antes de acceder al perfil.')
        return redirect('profile_verify_2fa')
        
    if request.method == 'POST':
        if 'update_email' in request.POST:
            email = request.POST.get('email')
            if email:
                request.user.email = email
                request.user.save()
                messages.success(request, 'Dirección de correo actualizada correctamente.')
            else:
                messages.error(request, 'El campo de correo no puede estar vacío.')
            return redirect('profile_edit')
            
        elif 'update_password' in request.POST:
            pwd_form = PasswordChangeForm(request.user, request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)  # Mantiene al usuario con la sesión iniciada
                messages.success(request, 'Contraseña actualizada correctamente.')
                # Invalida el acceso al perfil si cambia la contraseña (opcional de seguridad)
                # request.session['2fa_verified_for_profile'] = False 
                return redirect('profile_edit')
            else:
                for field_errors in pwd_form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
    else:
        pwd_form = PasswordChangeForm(request.user)
        
    return render(request, 'core/profile_edit.html', {
        'pwd_form': pwd_form,
    })

