from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from .models import Ticket, Order
from .payment_processors import get_payment_processor
from shows.models import ShowSector, Show

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

import uuid

from .utils import enviar_correo_confirmacion

from django.db.models import Sum

@login_required
def iniciar_reserva(request):
    if request.method == "POST":
        sector_id = request.POST.get('show_sector_id')
        
        try:
            cantidad = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Cantidad inválida.'}, status=400)
        
        # Regla de negocio: Límite estricto de 6 entradas por operación
        if cantidad > 6:
            return JsonResponse({
                'status': 'error', 
                'message': 'No podés adquirir más de 6 entradas por operación.'
            }, status=400)
            
        if cantidad < 1:
            return JsonResponse({
                'status': 'error', 
                'message': 'La cantidad mínima es 1 entrada.'
            }, status=400)
        
        try:
            # Abrimos el bloque atómico seguro
            with transaction.atomic():
                # select_for_update() bloquea la fila del ShowSector para que nadie altere las órdenes en paralelo
                show_sector = ShowSector.objects.select_for_update().get(id=sector_id)
                
                # Validamos el stock disponible usando tu propiedad dinámica
                if show_sector.available < cantidad:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Ya no quedan asientos suficientes. Disponibles: {show_sector.available}'
                    }, status=400)
                
                # Calculamos el total monetario
                total = show_sector.price * cantidad
                
                # Creamos la orden en modo PENDING. 
                # AL HACER ESTO, el método @property 'available' del sector leerá esta orden 
                # en la próxima consulta y el stock se considerará "restado" automáticamente.
                nueva_orden = Order.objects.create(
                    user=request.user,
                    show=show_sector.show,
                    show_sector=show_sector,
                    quantity=cantidad,
                    total_price=total,
                    status='PENDING'
                )
                
            # Al salir del bloque transaction.atomic(), Django libera el bloqueo en PostgreSQL
            return JsonResponse({
                'status': 'success',
                'message': 'Reserva temporal exitosa. Tienes 10 minutos para pagar.',
                'order_id': nueva_orden.id
            })
            
        except ShowSector.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sector no encontrado.'}, status=404)
            
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


def mock_checkout_view(request, order_id):
    """Muestra la pantalla simulada de la pasarela de pagos"""
    orden = get_object_or_404(Order, id=order_id, status='PENDING')
    return_url = request.GET.get('return_url', '/')
    
    context = {
        'orden': orden,
        'return_url': return_url
    }
    return render(request, 'purchase/mock_checkout.html', context)


def payment_feedback_view(request):
    """
    Recibe la respuesta de la pasarela (simulando un Webhook/Redirect).
    Modifica la base de datos según el resultado del pago.
    """
    procesador = get_payment_processor()
    
    # El procesador analiza el request y nos devuelve un diccionario estandarizado
    resultado = procesador.verify_webhook(request)
    
    order_id = resultado.get('order_id')
    if not order_id:
        return HttpResponseBadRequest("Falta el ID de la orden.")
        
    orden = get_object_or_404(Order, id=order_id)

    if resultado['success']:
    #     # ¡El pago fue exitoso! Confirmamos la orden
    #     orden.status = 'PAID'
    #     orden.save()
        
    #     # Opcional: Acá es donde en el futuro generarás los Tickets físicos
    #     mensaje = f"¡Pago aprobado con éxito! Tu orden #{orden.id} está confirmada."
    #     clase_alerta = "success"
    # Usamos una transacción atómica para asegurarnos de que se guarde la orden
        # Y se creen TODOS los tickets correspondientes. Si uno falla, no se guarda nada.
        try:
            with transaction.atomic():
                # 1. Cambiamos el estado de la orden
                orden.status = 'PAID'
                orden.save()
                
                # 2. Generamos los tickets físicos según la cantidad comprada
                tickets_creados = []
                for _ in range(orden.quantity):
                    ticket = Ticket.objects.create(
                        order=orden,
                        show_sector=orden.show_sector  # <-- Agregamos esto para cumplir con tu modelo
                    )
                    tickets_creados.append(ticket)

                    # with transaction.atomic():
                    #     # ... (guardado de orden y creación de tickets)
                    #     pass
                    
                    # Fuera del bloque atómico pero dentro del if success, gatillamos el email
            print("Gatillando función de email...") # Meté este print de control
            enviar_correo_confirmacion(orden)
            print("¡Función de email ejecutada con éxito!")        
            mensaje = f"¡Pago aprobado con éxito! Tu orden #{orden.id} está confirmada. Se han generado {len(tickets_creados)} tickets y se envió un mail de confirmación."
            clase_alerta = "success"
            
        except Exception as e:
            # IMPRESCINDIBLE: Esto nos va a decir en la consola qué está fallando por dentro
            print("\n❌ ❌ ❌ ¡¡¡EL PROCESO DE EMAIL ACABA DE FALLAR!!! ❌ ❌ ❌")
            print(f"Error real detectado: {str(e)}")
            import traceback
            traceback.print_exc() # Esto te pinta el número de línea exacto del error
            print("❌ ❌ ❌ ------------------------------------------- ❌ ❌ ❌\n")
            
            mensaje = f"El pago fue aprobado, pero ocurrió un error al generar tus tickets: {str(e)}. Por favor, contacta a soporte."
            clase_alerta = "warning"
    else:
        # El pago falló o fue cancelado. Expiramos/Cancelamos la orden
        orden.status = 'EXPIRED'  # O 'REFUNDED' / 'REJECTED' según prefieras
        orden.save()
        mensaje = f"El pago de la orden #{orden.id} fue rechazado o cancelado. Los asientos fueron liberados."
        clase_alerta = "danger"
        
    return render(request, 'purchase/payment_feedback.html', {
        'mensaje': mensaje,
        'clase_alerta': clase_alerta,
        'orden': orden
    })

@login_required
@require_POST
def iniciar_pago_view(request):
    """
    Recibe la selección del mapa interactivo, crea la orden PENDING
    y redirige al usuario a la pasarela de pago correspondiente.
    """
    show_sector_id = request.POST.get('show_sector_id')
    cantidad = int(request.POST.get('quantity', 1))
    
    # 1. Traemos el sector del show
    show_sector = get_object_or_404(ShowSector, id=show_sector_id)
    
    # 2. Validamos que haya stock suficiente antes de hacer nada
    if show_sector.available < cantidad:
        return render(request, 'purchase/payment_feedback.html', {
            'mensaje': "Lo sentimos, ya no quedan suficientes asientos disponibles en este sector.",
            'clase_alerta': "danger"
        })
        
    # 3. Creamos la orden en estado PENDING
    # Nota: Como tu @property 'available' ahora resta las órdenes PENDING,
    # al ejecutarse esta línea, el stock baja automáticamente para el resto del mundo.
    orden = Order.objects.create(
        user=request.user,
        show=show_sector.show,
        show_sector=show_sector,
        quantity=cantidad,
        total_price=show_sector.price * cantidad,
        status='PENDING'
    )
    
    # 4. Usamos nuestro Patrón Strategy para obtener el procesador activo
    procesador = get_payment_processor()
    
    # Definimos a dónde tiene que volver el usuario de forma absoluta tras el pago
    url_retorno = request.build_absolute_uri(reverse('purchase:payment_feedback'))
    
    # 5. Generamos el link de pago (que en este caso irá a nuestro Mock Checkout)
    link_de_pago = procesador.generate_payment_link(orden, return_url=url_retorno)
    
    # ¡Redirigimos al usuario a la pasarela!
    return redirect(link_de_pago)


@login_required(login_url='login') # <-- Protegemos la vista
def my_tickets_view(request):
    # Tu query excelente se mantiene idéntica
    ordenes = Order.objects.filter(
        user=request.user, 
        status='PAID'
    ).select_related(
        'show__event', 
        'show__place', 
        'show_sector__sector'
    ).prefetch_related('tickets').order_by('-id')
    
    return render(request, 'purchase/my-tickets.html', {'ordenes': ordenes})


# dashboard para que el organizador revise los datos del Evento
@login_required
def dashboard_organizador(request):
    # Seguridad Enterprise: Solo permitimos el acceso si el usuario es Staff/Organizador
    if not request.user.is_staff:
        return redirect('index') # O la URL de tu home pública
    

    # 1. Traemos los shows que le pertenecen a este organizador logueado
    # Buscamos shows cuyo EVENTO tenga como organizador al usuario actual
    shows = Show.objects.filter(event__organizador=request.user).select_related('event', 'place')
    
    # 2. Construimos el paquete de métricas para el template
    panel_datos = []
    
    total_recaudado_global = 0
    total_tickets_global = 0

    for show in shows:
        # Sumamos las cantidades y dinero de órdenes aprobadas (PAID) para este show específico
        metricas_ventas = Order.objects.filter(show=show, status='PAID').aggregate(
            total_dinero=Sum('total_price'),
            total_entradas=Sum('quantity')
        )
        
        recaudado = metricas_ventas['total_dinero'] or 0
        entradas_vendidas = metricas_ventas['total_entradas'] or 0
        
        # Calculamos la capacidad total sumando todos los sectores físicos del estadio asignado
        capacidad_estadio = show.place.sectors.aggregate(Sum('capacity'))['capacity__sum'] or 0
        
        # Porcentaje de ocupación para la barra de progreso
        porcentaje_ocupacion = 0
        if capacidad_estadio > 0:
            porcentaje_ocupacion = int((entradas_vendidas / capacidad_estadio) * 100)
            
        # Acumuladores globales para las tarjetas de arriba
        total_recaudado_global += recaudado
        total_tickets_global += entradas_vendidas
        
        panel_datos.append({
            'show': show,
            'recaudado': recaudado,
            'vendidas': entradas_vendidas,
            'capacidad': capacidad_estadio,
            'ocupacion_porcentaje': porcentaje_ocupacion
        })
        
    context = {
        'panel_datos': panel_datos,
        'total_recaudado_global': total_recaudado_global,
        'total_tickets_global': total_tickets_global,
        'cantidad_shows': shows.count()
    }
    
    return render(request, 'purchase/dashboard_organizador.html', context)