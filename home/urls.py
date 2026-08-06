from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('api/cargar-mas-eventos/', views.cargar_mas_eventos_view, name='cargar_mas_eventos'),
]