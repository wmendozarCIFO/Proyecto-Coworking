from django.shortcuts import redirect
from django.urls import reverse
from django_otp import user_has_device

class Force2FAMiddleware:
    """
    Middleware que intercepta las peticiones de los usuarios autenticados
    que aún no han configurado un dispositivo de autenticación de dos factores (2FA).
    Si no tienen uno, se les redirigirá forzosamente a la pantalla de configuración.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Comprueba si el usuario tiene al menos un dispositivo (TOTP, Email, SMS, etc.)
            if not user_has_device(request.user):
                
                # Lista de rutas que sí están permitidas aunque no tenga 2FA
                # (Para que pueda configurarlo o cerrar su sesión sin crear un bucle infinito)
                allowed_paths = [
                    reverse('two_factor:setup'),
                    reverse('two_factor:setup_complete'),
                    reverse('two_factor:qr'),
                    reverse('logout'),
                ]
                
                # Si la petición actual no es hacia una ruta permitida, y tampoco a archivos estáticos/media,
                # lo redirigimos a la página de Setup del 2FA.
                if request.path not in allowed_paths and \
                   not request.path.startswith('/static/') and \
                   not request.path.startswith('/media/'):
                    return redirect('two_factor:setup')

        response = self.get_response(request)
        return response
