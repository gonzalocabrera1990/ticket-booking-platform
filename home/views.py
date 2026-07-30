from django.shortcuts import render, redirect
from django.db import connection
from shows.models import Show, Category, Event
from django.contrib.auth.decorators import login_required

def index_view(request):
    # Traemos los eventos que sí tienen shows asociados
    dashboard = Event.objects.select_related('category').filter(
        shows__isnull=False
    ).distinct()[:4]
    
    all_dashboard = Event.objects.select_related('category').filter(
        shows__isnull=False
    ).distinct()[:8]
    
    categorias = Category.objects.all()
    
    
    db_name = connection.settings_dict.get('NAME', 'N/A')
    db_user = connection.settings_dict.get('USER', 'N/A')

    context = {
        'dashboard': dashboard,  # Enviamos el QuerySet limpio (puede ir vacío si no hay shows)
        'all_dashboard': all_dashboard,
        'categorias': categorias,
        'url_name': 'Ruta Raíz (/)',
        'current_url': '/',
        'db_name': db_name,
        'db_user': db_user
    }
    return render(request, 'home/home.html', context)


def cargar_mas_eventos_view(request):
    offset = int(request.GET.get('offset', 0))
    limite = 8  # Cuántos eventos traer en cada bloque extra
    
    # Query base idéntica a tu index_view
    query_base = Event.objects.select_related('category').filter(shows__isnull=False).distinct()
    
    # Traemos el siguiente bloque usando el offset enviado por JS
    siguientes_eventos = query_base[offset:offset + limite]
    
    # Contamos si quedan más eventos por cargar a futuro
    quedan_mas = query_base.count() > (offset + limite)
    
    return render(request, 'partials/events_grid_items.html', {
        'all_dashboard': siguientes_eventos,
        'quedan_mas': quedan_mas
    })

