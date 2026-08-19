from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order

import io
import qrcode
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

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

def enviar_ticket_por_email(ticket):
    asunto = f"🎟️ Tu entrada para {ticket.order.show}"
    email_destino = ticket.order.user.email
    
    # 1. Preparamos el contexto para el HTML
    contexto = {
        'ticket': ticket,
        'asistente': ticket.attendee_name or ticket.order.user.get_full_name() or ticket.order.user.username,
        'show': ticket.order.show,
        'sector': ticket.show_sector.sector.name,
    }
    
    html_content = render_to_string('emails/ticket_email.html', contexto)
    
    # 2. Armamos el mensaje
    msg = EmailMultiAlternatives(
        subject=asunto,
        body=f"Hola, adjuntamos tu ticket {ticket.ticket_code} para {ticket.order.show}.",
        from_email=None,  # Toma DEFAULT_FROM_EMAIL de settings.py
        to=[email_destino]
    )
    msg.attach_alternative(html_content, "text/html")
    
    # 3. Generamos los bytes del QR en memoria para el adjunto CID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(ticket.ticket_code))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    
    # 4. Creamos la imagen MIME y le asignamos el id "qr_code_image"
    mime_image = MIMEImage(buffer.getvalue())
    mime_image.add_header('Content-ID', '<qr_code_image>')
    mime_image.add_header('Content-Disposition', 'inline', filename="qr.png")
    msg.attach(mime_image)
            
    # 5. Enviamos el mail
    msg.send()