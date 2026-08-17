"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt # 🚨 1. IMPORTA ESTO AQUÍ
from login import views as login_views
from home.views import error_404_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('shows/', include('shows.urls')),
    path('signup/', include('signup.urls')),
    path('login/', include('login.urls')),
    path('purchase/', include('purchase.urls')),

    # REACT NATIVE QR ACCESS
    path('api/login/', csrf_exempt(login_views.api_login), name='api_login'),
    path('api/validar-qr/', csrf_exempt(login_views.api_validar_qr), name='api_validar_qr'),
]

# si la url no se encuentra en el proyecto se redirecciona a "/"
# funciona con DEBUG = False
handler404 = error_404_redirect_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
