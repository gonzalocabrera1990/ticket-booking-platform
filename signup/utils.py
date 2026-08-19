from django.template.loader import (
    render_to_string
)

from django.urls import reverse

from django.utils.http import (
    urlsafe_base64_encode
)

from django.utils.encoding import (
    force_bytes
)

from django.contrib.auth.tokens import (
    default_token_generator
)

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    activation_link = request.build_absolute_uri(
        reverse(
            'activate-account',
            kwargs={
                'uidb64': uid,
                'token': token
            }
        )
    )

    contexto = {
        'user': user,
        'activation_link': activation_link
    }

    # 1. Renderizamos el cuerpo en HTML y creamos la versión en texto plano para compatibilidad
    html_content = render_to_string('signup/activation_email.html', contexto)
    text_content = strip_tags(html_content)

    # 2. Creamos el objeto de correo
    subject = "Activá tu cuenta | EventLive"
    from_email = None  # Toma automáticamente DEFAULT_FROM_EMAIL de tu settings.py (Gmail)
    to_email = [user.email]
    # 💡 Imprime la URL limpia en consola para poder hacer Ctrl+Clic cómodamente en desarrollo:
    print(f"\n[DEV LINK] ---> {activation_link}\n")
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to_email
    )
    msg.attach_alternative(html_content, "text/html")

    # 3. Lo enviamos por la red vía SMTP
    msg.send()
