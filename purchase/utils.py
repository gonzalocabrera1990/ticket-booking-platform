from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order
def enviar_correo_confirmacion(orden):
    """
    Genera un correo basado en un template HTML con los detalles de la compra,
    incluyendo los QR en Base64, y lo despacha usando el send_mail original.
    """
    # CORRECCIÓN: Volvemos a usar .title que es tu campo real en el modelo Event
    asunto = f"🎟️ ¡Tu compra para {orden.show.event.title} fue confirmada! - Orden #{orden.id}"
    
    # Traemos los tickets asociados con sus relaciones optimizadas
    tickets = orden.tickets.select_related('show_sector__sector').all()

    contexto = {
        'orden': orden,
        'tickets': tickets,
    }
    
    # Tu ruta exacta original
    html_message = render_to_string('purchase/emails/confirmacion_compra.html', contexto)
    plain_message = strip_tags(html_message)
    
    # Despachamos el email usando tu configuración nativa
    send_mail(
        subject=asunto,
        message=plain_message,
        from_email=None,  # Usa el DEFAULT_FROM_EMAIL de settings
        recipient_list=[orden.user.email],
        html_message=html_message,
        fail_silently=False,
    )
