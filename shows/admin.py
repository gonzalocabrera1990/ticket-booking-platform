from django.contrib import admin
from django.db import models
from .models import Address, ShowPlace, Sector, MapLayoutObject, Category, Event, Show, ShowSector
from decimal import Decimal
# =====================================================================
# 1. INLINES DE INFRAESTRUCTURA (Carga secundaria dentro de un Estadio)
# =====================================================================

class SectorInline(admin.TabularInline):
    model = Sector
    extra = 1  
    fields = ('name', 'capacity', 'polygon_geometry')
    # Ajustamos el tamaño visual del cuadro de texto para pegar los Paths SVG cómodamente
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 2, 'cols': 50})},
    }

class MapLayoutObjectInline(admin.TabularInline):
    model = MapLayoutObject
    extra = 1
    fields = ('name', 'object_type', 'geometry')
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 2, 'cols': 50})},
    }


# =====================================================================
# 2. CONFIGURACIÓN COMPLETA DE MODELOS (Vistas e Interfaces)
# =====================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_hex')
    prepopulated_fields = {"slug": ("name",)} 


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organizador')
    list_filter = ('category', 'organizador')
    search_fields = ('title',)

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1         # Te muestra el formulario listo para rellenar
    max_num = 1       # 🛡️ Restringe la interfaz para que no puedan agregar más de una dirección por estadio
    can_delete = False # Evita que borren la dirección sin querer si el estadio existe
    
    # Si querés que se vea más ordenado, podés agrupar los campos de la dirección
    fieldsets = (
        ('Ubicación Física del Recinto', {
            'fields': (('street', 'zip_code'), ('city', 'state', 'country')), # Pone los campos en parejas horizontales
        }),
    )

@admin.register(ShowPlace)
class ShowPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'viewbox')
    search_fields = ('name',)
    
    # Inyectamos los bloques de Sectores y Escenarios dentro del mismo formulario del Estadio
    inlines = [AddressInline, SectorInline, MapLayoutObjectInline]
    
    fieldsets = (
        ('Configuración Geométrica del Canvas SVG', {
            'fields': ('name', 'capacity', 'viewbox'),
            'description': 'Establezca las dimensiones de la etiqueta viewBox para la correcta escala del mapa interactivo.'
        }),
    )


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('event', 'place', 'date', 'price')
    list_filter = ('place', 'date')
    
    fieldsets = (
        ('Datos Operativos', {
            'fields': ('event', 'place', 'date'),
        }),
        ('Estrategia Comercial Base', {
            'fields': ('price',),
            'description': 'El precio base determinará el algoritmo de costos automáticos para las tribunas.'
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Intercepta el clic en 'Guardar' y autogenera la cascada 
        de ShowSectors calculando tarifas como lo hacía tu seed.
        """
        # 1. Guardamos el Show en la Base de Datos
        super().save_model(request, obj, form, change)

        # 2. Si es una función NUEVA, automatizamos el inventario comercial
        if not change:
            precio_base_mkt = obj.price
            estadio_destino = obj.place

            # Buscamos cuántas funciones ya existen de este evento para detectar alta demanda
            funciones_previas = Show.objects.filter(event=obj.event).count()
            for sector in estadio_destino.sectors.all():
                # 👈 2. CONVERTIR LOS FLOTANTES A DECIMAL
                if "VIP" in sector.name or "Frontal" in sector.name or "Centro" in sector.name:
                    tarifa = precio_base_mkt * Decimal('2')
                elif "Alta" in sector.name or "Trasero" in sector.name:
                    tarifa = precio_base_mkt * Decimal('0.7')
                else:
                    tarifa = precio_base_mkt * Decimal('1.2')

                if funciones_previas > 1:
                    tarifa += Decimal('5000.00')

                ShowSector.objects.get_or_create(
                    show=obj,
                    sector=sector,
                    defaults={
                        'price': tarifa,
                        'sold': 0,
                        'reserved': 0
                    }
                )


@admin.register(ShowSector)
class ShowSectorAdmin(admin.ModelAdmin):
    list_display = ('show', 'sector', 'price', 'sold', 'reserved')
    list_filter = ('show__event', 'sector')
    # Permite editar los precios rápido desde la grilla general sin entrar al formulario individual
    list_editable = ('price',) 

# Registros residuales que no tienen interfaz compleja (para que no queden sueltos)
admin.site.register(Sector)
admin.site.register(MapLayoutObject)