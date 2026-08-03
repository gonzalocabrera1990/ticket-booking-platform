from django.db import models
from cities_light.models import City
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

# MANAGER PERSONALIZADO PARA MANEJAR EN ADMIN
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        
        email = self.normalize_email(email)
        
        # 🛡️ LA SOLUCIÓN CRÍTICA: Sacamos 'username' del diccionario si existe
        # para que no viaje en el **extra_fields hacia el constructor User()
        extra_fields.pop('username', None) 
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        # Por seguridad, también lo removemos aquí antes de delegar a create_user
        extra_fields.pop('username', None)

        return self.create_user(email, password, **extra_fields)

# MODELO DE USUARIO ACTUALIZADO PARA USAR EN EL ADMIN
class User(AbstractUser):
    username = None  # Eliminamos el campo username definitivamente
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth = models.DateField()
    email = models.EmailField(unique=True)
    dni = models.CharField(max_length=20, unique=True)
    img = models.ImageField(upload_to='users/', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth', 'dni'] # Campos que te va a pedir la consola al crear el superusuario

    # ASOCIAMOS EL MANAGER PERSONALIZADO
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    label = models.CharField(
        max_length=50
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
    street = models.CharField(
        max_length=255
    )
    street_number = models.CharField(
        max_length=20
    )
    floor = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    apartment = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        max_length=20
    )
    is_default = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "📍 Direcciones de Envío"
    
    def __str__(self):

        return f'{self.label} - {self.user.email}'
