from django.urls import path
from . import views

app_name = 'purchase'
urlpatterns = [
    #path('ticket/', views.ticket_view, name='ticket'),
    # Ruta que simula la pasarela de pago externa
    path('checkout/mock/<int:order_id>/', views.mock_checkout_view, name='mock_checkout'),
    
    # Ruta de retorno (A donde vuelve el usuario después de pagar)
    path('checkout/feedback/', views.payment_feedback_view, name='payment_feedback'),
    path('orden/iniciar/', views.iniciar_pago_view, name='iniciar_pago'),
    path('my-tickets/', views.my_tickets_view, name='my-tickets'),
]
