# Sistema de Gestión de Coworking Django

Este proyecto es una aplicación web desarrollada en Python y Django para la gestión de reservas de espacios de coworking. Permite a los usuarios registrarse, visualizar disponibilidad y realizar reservas, y a los administradores gestionar usuarios y reservas con seguridad reforzada (2FA).

## 📂 Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```text
c:\Proyecto Coworking
├── coworking_project/      # Configuración principal del proyecto (Settings, URLs, WSGI)
├── core/                   # Aplicación principal: Vistas generales (Home, Dashboard), autenticación
├── users/                  # Gestión de usuarios personalizados (DNI, Privilegios)
├── bookings/               # Lógica de reservas (Calendario, Slots, Email)
├── templates/              # Plantillas HTML globales y por aplicación
├── static/                 # Archivos estáticos (CSS, JS, Imágenes)
├── manage.py               # Script de gestión de Django
├── db.sqlite3              # Base de datos SQLite (por defecto)
└── requirements.txt        # Dependencias del proyecto
```

## 🚀 Logica del Negocio y Funcionalidades

### 1. Usuarios y Roles

- **Usuarios Finales**:
  - Registro con validación de DNI/NIE/NIF español.
  - Login estándar.
  - Panel de control (`Dashboard`) para ver y cancelar sus reservas.
- **Administradores**:
  - Login específico (`/admin-login/`) protegido con Autenticación de Doble Factor (2FA/TOTP).
  - Panel de administración (`/admin-dashboard/`) para gestionar usuarios y ver todas las reservas.
  - Capacidad de filtrar y buscar usuarios.

### 2. Reservas (Bookings)

- **Áreas de Trabajo**: Espacios configurables (ej. "Sala A", "Escritorio Compartido") con capacidad definida e imagen.
- **Calendario**: Visualización de disponibilidad para los próximos 14 días.
- **Slots**: Franjas horarias fijas de 1 hora (de 9:00 a 18:00).
- **Proceso de Reserva**:
  1. Selección de día.
  2. Selección de hora y área disponible.
  3. Confirmación y envío automático de correo electrónico con enlace de cancelación.

### 3. Seguridad

- Validación estricta de formatos de identificación (DNI).
- Decoradores de permisos (`@login_required`, `@user_passes_test`).
- Integración de `django-otp` para seguridad extra en cuentas de staff.

## 🌐 Vistas y Rutas Principales

| Ruta | Nombre | Descripción |
|------|--------|-------------|
| `/` | `home` | Página de inicio pública. |
| `/register/` | `register` | Registro de nuevos usuarios. |
| `/login/` | `login` | Inicio de sesión para usuarios estándar. |
| `/admin-login/` | `admin_login` | Inicio de sesión con 2FA para administradores. |
| `/dashboard/` | `user_dashboard` | Panel del usuario (mis reservas). |
| `/bookings/calendar/` | `booking_calendar` | Selección de fecha para reserva. |
| `/bookings/slots/<date>/` | `booking_slots` | Selección de hora y área. |
| `/admin-dashboard/` | `admin_dashboard` | Panel principal del administrador. |
| `/admin-users/` | `admin_users` | Gestión y búsqueda de usuarios. |

## 🛠️ Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Prerrequisitos

- Python 3.10 o superior instalado.
- Pip (gestor de paquetes de Python).

### 2. Configuración del Entorno Virtual e Instalación de Dependencias

Es recomendable usar un entorno virtual para aislar las librerías del proyecto.

1. **Crear el entorno virtual**:

   ```bash
   # En Windows
   python -m venv venv
   # O si tienes problemas, intenta con:
   py -m venv venv

   # En Linux/Mac
   python3 -m venv venv
   ```

2. **Activar el entorno virtual**:

   ```bash
   # En Windows
   .\venv\Scripts\activate

   # En Linux/Mac
   source venv/bin/activate
   ```

   *Verás que tu prompt cambia indicando `(venv)`.*

3. **Instalar dependencias**:
   Una vez activado el entorno, ejecuta:

   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuración de la Base de Datos

Aplica las migraciones para crear las tablas necesarias:

```bash
python manage.py migrate
```

### 4. Creación de un Superusuario (Administrador)

Para acceder al panel de administración y dashboard de admin:

```bash
python manage.py createsuperuser
```

*Sigue las instrucciones en pantalla para definir usuario, email y contraseña.*

> **Nota sobre 2FA:** Para el login de administrador (`/admin-login/`), el usuario debe tener un dispositivo 2FA configurado. Puedes configurarlo entrando primero a `/admin/` (admin de Django) > OTP TOTP > Add Device, o desactivar temporalmente el requisito en el código si es solo para pruebas rápidas.

### 5. Configuración de Áreas de Trabajo

Antes de poder reservar, necesitas crear al menos un "Area de Trabajo".

1. Ejecuta el servidor.
2. Ve a `/admin/` (login con tu superusuario).
3. Busca "Bookings" > "Areas de Trabajo" y añade algunas (ej. "Mesa 1", Capacidad: 1).

### 6. Ejecutar el Servidor

Inicia el servidor de desarrollo:

```bash
python manage.py runserver
```

Accede a la aplicación en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📦 Despliegue (Producción)

Para un entorno de producción (no local):

1. Cambiar `DEBUG = True` a `False` en `settings.py`.
2. Configurar `ALLOWED_HOSTS` con el dominio del sitio.
3. Usar un servidor WSGI como Gunicorn.
4. Servir archivos estáticos usando Nginx o WhiteNoise.
5. Configurar un backend de email real (SMTP) en lugar de la consola.
