from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# ==========================================
# 1. ENTORNO FÍSICO / INFRAESTRUCTURA
# ==========================================

class ShowPlace(models.Model):
    """El Estadio / Teatro (Infraestructura fija)"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Lugar")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad Total del Lugar")
    viewbox = models.CharField(
        max_length=50, 
        default="0 0 1000 1000", 
        help_text="Dimensiones originales del lienzo SVG para el escalado dinámico."
    )
    class Meta:
        verbose_name = "Estadio / Recinto"
        verbose_name_plural = "🏢 Estadios y Recintos" # Le podés sumar un emoji para que resalte en el menú lateral
    def __str__(self):
        return self.name


class Address(models.Model):
    """Dirección física unívoca de un lugar"""
    place = models.OneToOneField(ShowPlace, on_delete=models.CASCADE, related_name="address")
    street = models.CharField(max_length=255, verbose_name="Calle y Número")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Provincia/Estado")
    country = models.CharField(max_length=100, verbose_name="País", default="Argentina")
    zip_code = models.CharField(max_length=20, verbose_name="Código Postal", blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}"


class Sector(models.Model):
    """El sector físico de cemento dentro de un estadio (Infraestructura fija)"""
    place = models.ForeignKey(ShowPlace, on_delete=models.CASCADE, related_name="sectors", verbose_name="Lugar")
    name = models.CharField(max_length=100, verbose_name="Nombre del Sector")
    slug = models.SlugField(max_length=100, help_text="Identificador único para el ID del SVG.")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad Máxima Física del Sector")
    polygon_geometry = models.JSONField(
        verbose_name="Medidas del Polígono (JSON)",
        help_text="Diccionario con el tipo de forma de SVG y sus puntos/coordenadas correspondientes."
    )

    def __str__(self):
        return f"{self.place.name} - {self.name}"


class MapLayoutObject(models.Model):
    """Elementos decorativos fijos del mapa SVG"""
    place = models.ForeignKey(ShowPlace, on_delete=models.CASCADE, related_name='layout_objects')
    name = models.CharField(max_length=100)
    object_type = models.CharField(max_length=20, default='INFRA') 
    geometry = models.JSONField()

    def __str__(self):
        return f"{self.place.name} - {self.name} ({self.object_type})"


# ==========================================
# 2. ENTORNO COMERCIAL / MARKETING
# ==========================================

class Category(models.Model):
    """Categorías de los espectáculos"""
    name = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug / Identificador URL")
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="Clase de FontAwesome o Bootstrap Icons.")
    color_hex = models.CharField(max_length=7, default="#007bff", help_text="Color en formato HEX para las etiquetas.")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Event(models.Model):
    """El Artista / La Gira (Contenido estático de Marketing)"""
    title = models.CharField(max_length=200, verbose_name="Nombre del Evento / Banda")
    description = models.TextField(verbose_name="Descripción del Evento")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de la Imagen")

    # NUEVO CAMPO: El dueño corporativo de este evento
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- Esto resuelve el Error E301
        on_delete=models.PROTECT, 
        related_name="eventos_creados", 
        null=True, 
        blank=True,
        verbose_name="Organizador / Productora"
    )

    def __str__(self):
        return self.title


class Show(models.Model):
    """La Función específica (Día, hora y lugar de una fecha real)"""
    # Cambiamos el orden: Event ya existe arriba, permitiendo la relación nativa limpia
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="shows")
    place = models.ForeignKey(ShowPlace, on_delete=models.PROTECT, related_name="shows")
    date = models.DateTimeField(verbose_name="Fecha y hora de la función")
    
    # Lo mantenemos útil como "Precio Base Mínimo promocional" para la cartelera
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Precio mínimo estimado para marketing")

    def __str__(self):
        return f"{self.event.title} - {self.date.strftime('%d/%m/%Y %H:%M')} hs"


class ShowSector(models.Model):
    """El inventario comercial e ingresos de una función/noche determinada"""
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="show_sectors")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="show_sectors")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio para este Show")
    
    sold = models.PositiveIntegerField(default=0, verbose_name="Entradas Vendidas")
    reserved = models.PositiveIntegerField(default=0, verbose_name="Entradas Reservadas")

    class Meta:
        unique_together = ('show', 'sector')

    @property
    def available(self):
        # 1. Contamos los asientos comprometidos en las órdenes de la app sales
        asientos_reservados = self.orders.filter(
            status__in=['PENDING', 'PAID']
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

        # 2. Buscamos la capacidad en el modelo Sector vinculado
        # Cambiá 'capacity' por el nombre real que tenga en ese modelo
        return self.sector.capacity - asientos_reservados
 
    def __str__(self):
        return f"{self.show.event.title} ({self.show.date.strftime('%d/%m')}) - {self.sector.name} (${self.price})"
