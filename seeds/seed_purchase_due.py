from purchase.models import Order
from shows.models import ShowSector
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# 1. Traemos al usuario y al sector VIP de Coldplay
User = get_user_model()
usuario = User.objects.first()
sector_vip = ShowSector.objects.get(id=123)

# 2. En lugar de restar stock (que da error), creamos la orden directamente.
# Al crearse la orden, tu @property 'available' debería detectar automáticamente
# que hay 100 entradas menos (porque ahora pertenecen a una orden activa).
orden_vieja = Order.objects.create(
    user=usuario,
    show=sector_vip.show,
    show_sector=sector_vip,
    quantity=100,
    total_price=sector_vip.price * 100,
    status='PENDING'
)

# 3. Hackeamos el reloj para decirle a Django que esta orden se creó hace 25 minutos
Order.objects.filter(id=orden_vieja.id).update(created_at=timezone.now() - timedelta(minutes=25))

print(f"\n✅ [SIMULACIÓN ACTIVA] Se creó la Orden #{orden_vieja.id} pendiente de pago.")
print("Vérificá en tu servidor web si el mapa ahora muestra 100 asientos menos.")
exit()