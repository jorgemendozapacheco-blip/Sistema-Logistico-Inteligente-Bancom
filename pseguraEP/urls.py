# pseguraEP/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login
    path('login/', include('Aplicaciones.loginps.urls')),

    # Academico: todas sus rutas estarán en /<path> y con namespace "academico"
    path(
        '',
        include(
            ('Aplicaciones.Academico.urls', 'academico'),
            namespace='academico'
        )
    ),
]
