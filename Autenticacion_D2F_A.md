# Autenticación de Doble Factor (2FA) para Administradores

Este proyecto implementa un sistema de seguridad robusto para proteger el acceso a las funciones administrativas. Utilizamos **Autenticación de Doble Factor (2FA)** basada en el estándar TOTP (Time-based One-Time Password).

## ¿Cómo funciona?

El sistema de login para administradores (`/admin-login/`) requiere tres credenciales en lugar de las dos tradicionales:

1. **Nombre de usuario**.
2. **Contraseña**.
3. **Token de seguridad**: Un código numérico de 6 dígitos que cambia cada 30 segundos, generado por una aplicación en tu dispositivo móvil.

Esto asegura que incluso si un atacante roba tu contraseña, no podrá acceder al panel de administración sin tu dispositivo físico (móvil).

---

## Guía Paso a Paso

### 1. Requisitos Previos

Necesitas tener instalada una aplicación de autenticación en tu teléfono móvil. Las más comunes son:

- **Google Authenticator** (Android / iOS)
- **Microsoft Authenticator**
- **Authy**

### 2. Configuración Inicial (Primera vez)

Como la seguridad es estricta, un administrador no puede loguearse en el panel especial sin antes vincular un dispositivo. Esto se hace desde el panel de administración estándar de Django (que sirve como "puerta trasera" segura para la configuración inicial).

1. Asegúrate de tener un superusuario creado (`python manage.py createsuperuser`).
2. Inicia sesión en el panel estándar de Django: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
3. Busca la sección **OTP TOTP** y haz clic en **TOTP devices**.
4. Haz clic en el botón **Add OT P device** (o "Añadir dispositivo TOTP").
5. Selecciona tu usuario (User).
6. (Opcional) Pon un nombre al dispositivo (ej: "Móvil de Juan").
7. Guarda los cambios.
8. Al guardar, verás una columna o enlace para ver el **QR Code**. Deberás escanear este código con tu App de Autenticación en el móvil.
    - *Nota: Si no ves el QR directamente en la lista, haz clic en el dispositivo creado para ver sus detalles o el enlace al QR.*

### 3. Iniciar Sesión como Administrador

Una vez configurado, ya no usarás `/admin/` para tus tareas diarias, sino el login personalizado y seguro del proyecto.

1. Ve a la ruta de acceso admin: [http://127.0.0.1:8000/admin-login/](http://127.0.0.1:8000/admin-login/)
2. Introduce tu **Usuario**.
3. Introduce tu **Contraseña**.
4. Abre tu app en el móvil y mira el código actual (ej: `123456`).
5. Introdúcelo en el campo **Token OTP**.
6. Haz clic en "Entrar".

Si los datos son correctos, serás redirigido al **Dashboard de Administración**.

---

## Detalles Técnicos (Para Desarrolladores)

La implementación se basa en la librería `django-otp`.

### Lógica del Login (`core/views.py`)

La vista `admin_login` utiliza el formulario `OTPAuthenticationForm`:

```python
from django_otp.forms import OTPAuthenticationForm

def admin_login(request):
    if request.method == 'POST':
        # Este formulario valida Usuario + Pass + Token automáticamente
        form = OTPAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            # Verificación extra: ¿Es realmente staff?
            if not form.get_user().is_staff:
                messages.error(request, 'No tienes privilegios.')
                return redirect('home')
            return redirect('admin_dashboard')
```

### Middleware y Protección

Aunque un usuario se loguee correctamente, las vistas protegidas verifican que el usuario sea `is_staff`. Además, el middleware de `django-otp` se asegura de que la sesión esté verificada como "segura" (con dispositivo confirmado) antes de permitir acciones sensibles si así se configura en las políticas de seguridad globales.
