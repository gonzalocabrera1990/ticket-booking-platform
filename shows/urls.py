from django.urls import path
from . import views

urlpatterns = [
    # Ruta dinámica que acepta el ID numérico del lugar
    path('<int:event_id>/', views.shows_view, name='shows'), # detalles del evento para elegir fecha
    path('<int:show_id>/mapa/', views.vista_del_mapa, name='ver_mapa'), # mostrar el mapa del estadio para fecha
    path('buscar/', views.buscar_shows, name='buscar_shows'), # vista de busqueda
    path('control-accesos/panel/', views.panel_control_accesos_view, name='panel_control_accesos'),
    path('control-accesos/api/validar/', views.validar_ticket_api, name='validar_ticket_api'),
]
