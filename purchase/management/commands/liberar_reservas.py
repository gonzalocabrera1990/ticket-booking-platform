from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from purchase.models import Order

class Command(BaseCommand):
    help = 'Libera los asientos de las órdenes pendientes que superaron los 10 minutos de gracia.'

    def handle(self, *args, **options):
        # 1. Calcular la hora límite (Hace 10 minutos)
        tiempo_limite = timezone.now() - timedelta(minutes=10)
        
        # 2. Buscar las órdenes afectadas
        ordenes_vencidas = Order.objects.filter(
            status='PENDING',
            created_at__lt=tiempo_limite
        )
        
        cantidad_ordenes = ordenes_vencidas.count()
        
        if cantidad_ordenes == 0:
            self.stdout.write(self.style.SUCCESS('No hay órdenes vencidas para liberar.'))
            return

        # 3. Abrir bloque atómico para operar de forma segura
        try:
            with transaction.atomic():
                for orden in ordenes_vencidas:
                    # Al no tocar el 'sector.available', evitamos el AttributeError.
                    # Simplemente cambiamos el estado de la orden.
                    orden.status = 'EXPIRED'
                    orden.save()
                    
                    self.stdout.write(f'Orden #{orden.id} expirada de forma segura.')
            
            self.stdout.write(self.style.SUCCESS(f'Proceso completado con éxito. Se limpiaron {cantidad_ordenes} órdenes.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error al liberar las reservas: {str(e)}'))