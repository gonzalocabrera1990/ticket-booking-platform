from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.db.models import Q
from .models import ShowPlace, Show, ShowSector, MapLayoutObject, Category, Event

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from purchase.models import Ticket
from django.utils import timezone

def shows_view(request, event_id):
    # Traemos el evento o tiramos 404
    evento = get_object_or_404(Event, id=event_id)

    # Obtenemos todos los shows asociados a este evento ordenados por fecha
    shows = Show.objects.filter(event=evento).order_by('date')
    
    # Buscamos el precio mínimo sugerido para mostrar un "Desde $X"
    precio_minimo = None
    if shows.exists():
        precio_minimo = min([show.price for show in shows])

    return render(request, 'shows/shows.html', {
        'evento': evento,
        'shows': shows,
        'precio_minimo': precio_minimo
    })

def buscar_shows(request):
    """Vista exclusiva para procesar y renderizar los resultados de búsqueda"""
    categorias = Category.objects.all()
    
    # Capturamos los parámetros del formulario GET
    query_texto = request.GET.get('q', '').strip()
    query_categoria = request.GET.get('category', '').strip()
    
    # IMPORTANTE: Eliminamos 'place' del select_related porque no existe en Show.
    # Usamos distinct() al final para evitar que si un show tiene 5 sectores, 
    # aparezca 5 veces repetido en los resultados de búsqueda.
    #resultados = Show.objects.select_related('category').order_by('date').distinct()
    resultados = Event.objects.select_related('category').filter(shows__isnull=False).distinct()
    # Aplicamos filtros si el usuario ingresó datos
    if query_texto:
        resultados = resultados.filter(
            Q(title__icontains=query_texto) |
            Q(description__icontains=query_texto) |
            # Buscamos de forma segura si el nombre del estadio coincide con alguna de sus funciones
            Q(shows__place__name__icontains=query_texto) |
            Q(shows__place__address__city__icontains=query_texto)
        ).distinct()
        
    if query_categoria:
        resultados = resultados.filter(category__slug=query_categoria)

    return render(request, 'shows/resultados_busqueda.html', {
        'events': resultados,
        'categorias': categorias,
        'query_texto': query_texto,
        'query_categoria': query_categoria,
    })

# CÓMO DEBERÍA VERSE TU VISTA DEL MAPA
def vista_del_mapa(request, show_id):
    # 1. Buscamos la función específica por su ID único
    show = get_object_or_404(Show, id=show_id)
    # show = get_object_or_404(Show.objects.select_related('event', 'place'), id=show_id)
    
    # # 2. El lugar (estadio) ahora viene directo del modelo Show, ¡mucho más limpio!
    # place = show.place
    # 2. A partir de ESA función, extraemos el estadio correcto y sus sectores
    estadio = show.place 
    sectores_del_estadio = estadio.sectors.all()
    
    # 3. Traemos los precios y disponibilidad reales de ESA noche
    # show_sectores = show.showsector_set.all() # O ShowSector.objects.filter(show=show)
    # show_sectores = show.show_sectors.all()
    show_sectores = ShowSector.objects.filter(show=show)
    layout_objects = MapLayoutObject.objects.filter(place=estadio)
    fecha_formateada = show.date.strftime("%Y-%m-%d %H:%M")

    return render(request, 'shows/detalle_show.html', {
        'show': show,
        'place': estadio,
        'show_sectors': show_sectores,
        'layout_objects': layout_objects,
        'fecha_formateada': fecha_formateada
    })

@csrf_exempt  # Desactivamos CSRF temporalmente para facilitar que aplicaciones externas le peguen al endpoint
@require_POST
def validar_ticket_api(request):
    """
    Endpoint de API para los molinetes del estadio.
    Recibe el UUID del ticket, valida su estado y registra el ingreso.
    """
    import json
    
    try:
        data = json.loads(request.body)
        ticket_code = data.get('ticket_code')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido.'}, status=400)
        
    if not ticket_code:
        return JsonResponse({'status': 'error', 'message': 'Falta el código del ticket.'}, status=400)
        
    try:
        # Buscamos el ticket por su UUID único
        #ticket = Ticket.objects.get(ticket_code=ticket_code)

        # Mejorames el .get. Buscamos el ticket y pre-cargamos de un solo golpe toda la cadena de relaciones
        ticket = Ticket.objects.select_related(
            'show_sector__show__event',  # Junta Ticket -> ShowSector -> Show -> Event
            'show_sector__sector',      # Junta Ticket -> ShowSector -> Sector (para el nombre del sector)
            'order__user'               # Junta Ticket -> Order -> User (para el nombre del comprador)
        ).get(ticket_code=ticket_code)
                
        # Caso 1: El ticket ya fue escaneado antes (¡ALERTA DE FRAUDE!)
        if ticket.is_used:
            return JsonResponse({
                'status': 'RECHAZADO',
                'message': f'¡ALERTA! Este ticket ya ingresó el {ticket.used_at.strftime("%d/%m/%Y a las %H:%M")} hs.',
                'evento': ticket.show_sector.show.event.title,
                'sector': ticket.show_sector.sector.name
            }, status=409) # Conflict
            
        # Caso 2: El ticket es válido y está listo para usar
        ticket.is_used = True
        ticket.used_at = timezone.now()
        ticket.save()
        
        return JsonResponse({
            'status': 'OK',
            'message': '¡ACCESO CONCEDIDO! Bienvenido al estadio.',
            'evento': ticket.show_sector.show.event.title,
            'sector': ticket.show_sector.sector.name,
            'comprador': ticket.order.user.get_full_name() or ticket.order.user.username
        }, status=200)
        
    except Ticket.DoesNotExist:
        # Caso 3: El código es inventado o falso
        return JsonResponse({
            'status': 'RECHAZADO',
            'message': 'ERROR: El ticket no existe en el sistema. Código falso.'
        }, status=404)

def panel_control_accesos_view(request):
    """Muestra la interfaz web interactiva para simular el escáner del staff"""
    return render(request, 'shows/scanner_simulador.html')
