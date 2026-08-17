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

from purchase.models import Ticket # Asegurate de que este sea el nombre de tu modelo de entradas
from django.views.decorators.csrf import csrf_exempt
from .models import LoginCode
from signup.models import User
from signup.decorators import (
    unauthenticated_user
)
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

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


@csrf_exempt # Desactivamos CSRF para la app móvil porque usará Tokens de autorización
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_staff: # Solo permitimos el ingreso a usuarios administradores/staff
                    # Crea o recupera el token de la base de datos de este usuario
                    token, created = Token.objects.get_or_create(user=user)
                    return JsonResponse({
                        'status': 'success',
                        'token': token.key,
                        'username': user.username
                    })
                else:
                    return JsonResponse({'error': 'No tenés permisos de Staff para controlar accesos'}, status=403)
            else:
                return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def api_validar_qr(request):
    if request.method == 'POST':
        # 1. Validar Token en Headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return JsonResponse({'error': 'No autorizado. Falta el Token.'}, status=401)
        
        token_key = auth_header.split(' ')[1]
        try:
            Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token inválido o expirado'}, status=403)
        
        # 2. Procesar el QR basado en tus modelos reales
        try:
            data = json.loads(request.body)
            qr_string = data.get('uuid') 
            
            # 🔄 Capturamos el modo enviado por la App (por defecto es 'check_in' si no viene nada)
            modo = data.get('modo', 'check_in') 
            
            # Buscamos por tu campo real único 'ticket_code'
            ticket = Ticket.objects.get(ticket_code=qr_string)
            
            # 🛑 SI EL MODO ES "CHECK_IN" (Validar y quemar), aplicamos los filtros estrictos
            if modo == 'check_in':
                if ticket.is_used:
                    hora_ingreso = ticket.used_at.strftime("%H:%M") if ticket.used_at else "Desconocida"
                    return JsonResponse({
                        'status': 'error',
                        'message': f'¡ALERTA! Ticket YA UTILIZADO a las {hora_ingreso}hs.'
                    }, status=400)
                
                # Si pasa el filtro, lo quemamos en PostgreSQL de forma definitiva
                ticket.is_used = True
                ticket.used_at = timezone.now()
                ticket.save()
            
            # 🔍 SI EL MODO ES "READ_ONLY" (Solo validar)
            # Nos saltamos el 'if ticket.is_used' y NO ejecutamos ticket.save().
            # Así, aunque el ticket ya haya ingresado por la puerta principal, el filtro da "Acceso Permitido".
            
            # Buscamos el nombre del show navegando por tus relaciones
            nombre_show = "Evento"
            if ticket.order and ticket.order.show:
                nombre_show = str(ticket.order.show)
            elif ticket.show_sector and hasattr(ticket.show_sector, 'show'):
                nombre_show = str(ticket.show_sector.show)

            # Buscamos el nombre del asistente
            nombre_asistente = ticket.attendee_name
            if not nombre_asistente and ticket.order and ticket.order.user:
                nombre_asistente = ticket.order.user.username

            # Armamos un mensaje personalizado para que el Staff sepa qué pasó en su pantalla
            mensaje_exito = '¡Acceso Permitido!' if modo == 'check_in' else '¡Ticket Válido! (Solo Lectura)'

            return JsonResponse({
                'status': 'success',
                'message': mensaje_exito,
                'datos': {
                    'evento': nombre_show, 
                    'usuario': nombre_asistente if nombre_asistente else 'Invitado',
                    'ya_usado_antes': ticket.is_used # Le avisa a la app si este ticket ya pasó por el check-in previo
                }
            })
            
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ticket falso o inexistente.'}, status=404)
        except Exception as e:
            print(f"❌ ERROR EN LA API: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)