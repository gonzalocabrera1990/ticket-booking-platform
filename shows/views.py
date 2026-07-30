from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.db.models import Q
from .models import Show, ShowSector, MapLayoutObject, Event

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
    # print("show_sectores[0].price", show_sectores[0].price)
    # print("show_sectores[0].available", show_sectores[0].available)
    # print("show_sectores[0].id", show_sectores[0].id)
    return render(request, 'shows/detalle_show.html', {
        'show': show,
        'place': estadio,
        'show_sectors': show_sectores,
        'layout_objects': layout_objects,
        'fecha_formateada': fecha_formateada
    })
