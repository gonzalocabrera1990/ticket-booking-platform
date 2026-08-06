from django.shortcuts import (
    render,
    redirect
)

import random
from django.contrib import messages
from signup.utils import (
    send_activation_email
)

from django.contrib.auth import (
    login,
    logout
)
from django.views.decorators.http import (
    require_POST
)

from django.core.mail import (
    EmailMessage
)

from .models import LoginCode
from signup.models import User
from signup.decorators import (
    unauthenticated_user
)

import json
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta


@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        # Detectamos si viene por Fetch (JavaScript)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if is_ajax:
            # Si viene por JS, los datos viajan en el cuerpo (body) en formato JSON
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        else:
            # Por si acaso entra un POST tradicional
            email = request.POST.get('email')
            password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            if not user.is_active:
                request.session['inactive_user_id'] = user.id
                
                if is_ajax:
                    return JsonResponse({'success': True, 'redirect_url': 'account-not-verified/'}) # O el nombre de tu ruta
                return redirect('account-not-verified')

            # GENERAR CODIGO
            code = str(random.randint(100000, 999999))

            # BORRAR CODIGOS VIEJOS
            LoginCode.objects.filter(user=user).delete()

            # GUARDAR NUEVO CODIGO
            LoginCode.objects.create(user=user, code=code)

            # ENVIAR EMAIL
            email_message = EmailMessage(
                'Código de acceso',
                f'Tu código es: {code}',
                to=[user.email]
            )
            email_message.send()

            # SESSION TEMPORAL
            request.session['login_user_id'] = user.id

            if is_ajax:
                # Éxito: Le decimos a JS a dónde mandar al usuario a poner el código
                return JsonResponse({'success': True, 'redirect_url': 'verify-login/'}) # Asegura que apunte a tu URL real
            return redirect('verify-login')
            
        else:
            # CREDENCIALES INVÁLIDAS
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Credenciales inválidas. Por favor, intentá de nuevo.'})
            return render(request, 'login/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'login/login.html')

def account_not_verified_view(request):
    user_id = request.session.get(
        'inactive_user_id'
    )

    if not user_id:
        return redirect('login')

    user = User.objects.get(
        id=user_id
    )
    return render(
        request,
        'login/account_not_verified.html',
        {
            'user': user
        }
    )


def resend_activation_email_view(request):
    user_id = request.session.get(
        'inactive_user_id'
    )

    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'redirect_url': '/login/'})
        return redirect('login')

    user = User.objects.get(
        id=user_id
    )

    send_activation_email(
        request,
        user
    )
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Te reenviamos el email de activación. Revisá tu casilla de correo.'
        })

    messages.success(
        request,
        'Te reenviamos el email de activación.'
    )
    return redirect(
        'account-not-verified'
    )


@unauthenticated_user
def verify_login_code_view(request):
    user_id = request.session.get('login_user_id')

    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'redirect_url': '/login/'})
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        # Detectamos si viene por JavaScript (Asíncrono)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if is_ajax:
            data = json.loads(request.body)
            code = data.get('code')
        else:
            code = request.POST.get('code')

        # Buscamos el código en la base de datos
        login_code = LoginCode.objects.filter(user=user, code=code).first()

        if login_code:
            ahora = timezone.now()
            tiempo_limite = login_code.created_at + timedelta(minutes=5)

            if ahora <= tiempo_limite:
                # ... tu lógica de éxito se mantiene igual ...
                login_code.delete()
                request.session.pop('login_user_id', None)
                login(request, user)
                if is_ajax:
                    return JsonResponse({'success': True, 'redirect_url': '/'})
                return redirect('/')
            else:
                # CÓDIGO EXPIRADO: Agregamos la razón del fallo en el JSON
                if is_ajax:
                    return JsonResponse({
                        'success': False, 
                        'reason': 'expired', # <-- CLAVE PARA JAVASCRIPT
                        'message': 'El código ha expirado. Por seguridad, por favor volvé a iniciar sesión.'
                    })
                return render(request, 'login/verify_login.html', {'error': 'El código ha expirado...'})
        
        else:
            # CÓDIGO INCORRECTO (Mal tipeado)
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'reason': 'invalid', # <-- CLAVE PARA JAVASCRIPT
                    'message': 'Código inválido. Verificá los números.'
                })
            return render(request, 'login/verify_login.html', {'error': 'Código inválido'})
    return render(request, 'login/verify_login.html')

@require_POST
def logout_view(request):
    logout(request)
    return redirect('/')
