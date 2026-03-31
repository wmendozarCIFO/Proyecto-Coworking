from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice

# Esto obtendrá automáticamente tu modelo 'users.User'
User = get_user_model()

# Busca tu usuario
usuario=input("Ingrese su usuario: ")
user = User.objects.get(username=usuario)

# Borra el dispositivo 2FA para que te pida el QR de nuevo
TOTPDevice.objects.filter(user=user).delete()

print("Dispositivo eliminado con éxito. Ya puedes cerrar la consola.")
exit()