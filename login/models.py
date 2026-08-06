from django.db import models
from signup.models import User

class LoginLog(models.Model):
    username = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.timestamp} (Success: {self.success})"

class LoginCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    code = models.CharField(
        max_length=6
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ESTO APORTA LA OPTIMIZACIÓN A POSTGRESQL
    class Meta:
        # 1. Creamos un índice compuesto para optimizar la verificación de código
        indexes = [
            models.Index(fields=['user', 'code'], name='login_user_code_idx'),
        ]
        # 2. Ordenamos la tabla para que los códigos más nuevos se lean primero por defecto
        ordering = ['-created_at']
    
    def __str__(self):

        return f"{self.user.email} - {self.code}"