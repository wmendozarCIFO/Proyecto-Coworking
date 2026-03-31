import re
from django.core.exceptions import ValidationError

def validate_spanish_id(value):
    """
    Validates Spanish DNI, NIE, or NIF.
    """
    value = value.upper()
    
    # Verificación rápida de formato
    if not re.match(r'^[XYZ0-9][0-9]{7}[A-Z]$', value):
        raise ValidationError('Formato inválido. Debe ser DNI (8 números + letra) o NIE (X/Y/Z + 7 números + letra).')

    nie_prefix = {'X': '0', 'Y': '1', 'Z': '2'}
    
    # Verificar si es un NIE (empieza con X, Y, Z)
    if value[0] in nie_prefix:
        numeric_part = nie_prefix[value[0]] + value[1:8]
    else:
        # Es un DNI o NIF (el NIF estándar generalmente coincide con el formato DNI para individuos)
        numeric_part = value[0:8]

    try:
        number = int(numeric_part)
    except ValueError:
        raise ValidationError('La parte numérica no es válida.')

    letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    calculated_letter = letters[number % 23]
    
    if value[-1] != calculated_letter:
        raise ValidationError(f'La letra no es correcta. Debería ser {calculated_letter}.')
