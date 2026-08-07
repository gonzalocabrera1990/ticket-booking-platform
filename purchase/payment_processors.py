from abc import ABC, abstractmethod
from .models import Order
from django.urls import reverse

from django.conf import settings
from django.utils.module_loading import import_string


class BasePaymentProcessor(ABC):
    """
    Interfaz base (Estrategia) para todos los procesadores de pago.
    Cualquier pasarela nueva debe heredar de acá e implementar estos métodos.
    """

    @abstractmethod
    def generate_payment_link(self, order: Order, return_url: str) -> str:
        """
        Genera el link de pago (Checkout) hacia la pasarela externa
        donde el usuario pondrá su tarjeta.
        """
        pass

    @abstractmethod
    def verify_webhook(self, request) -> dict:
        """
        Recibe la notificación del servidor de la pasarela (Webhook)
        y valida si el pago fue exitoso, rechazado o está pendiente.
        """
        pass

class MockPaymentProcessor(BasePaymentProcessor):
    """
    Procesador de desarrollo (Mock) para simular pagos localmente
    sin pegarle a APIs externas.
    """

    def generate_payment_link(self, order: Order, return_url: str) -> str:
        # Generamos una URL interna de nuestra web que simula ser la pasarela
        # Le pasamos el ID de la orden y la URL a la que debe volver el usuario después
        checkout_url = reverse('purchase:mock_checkout', kwargs={'order_id': order.id})
        return f"{checkout_url}?return_url={return_url}"

    def verify_webhook(self, request) -> dict:
        # En el simulador, el resultado nos va a llegar directamente por POST o GET
        status = request.POST.get('status') or request.GET.get('status')
        order_id = request.POST.get('order_id') or request.GET.get('order_id')
        
        return {
            'order_id': order_id,
            'success': status == 'PAID',
            'status': status  # Puede ser 'PAID' o 'REJECTED'
        }

def get_payment_processor() -> BasePaymentProcessor:
    """Instancia dinámicamente el procesador configurado en settings.py"""
    processor_class = import_string(settings.PAYMENT_PROCESSOR)
    return processor_class()
