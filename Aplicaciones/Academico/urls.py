# urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'academico'

urlpatterns = [
    # Login/Logout
    path('login/',
            auth_views.LoginView.as_view(template_name='academico/login.html'),name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Inventario (importación + listado)
    path('inventario/', views.inventario, name='inventario'),
    path('inventario/clear/', views.clear_inventario, name='clear_inventario'),


    # Módulo 1 y resto de rutas
    path('', views.home, name='home'),
    path('modulo1/', views.modulo1, name='modulo1'),
    path('registrarEquipamiento/', views.registrarEquipamiento, name='registrarEquipamiento'),
    path('editarEquipamiento/', views.editarEquipamiento, name='editarEquipamiento'),
    path('eliminarEquipamiento/<str:codigo>/', views.eliminarEquipamiento, name='eliminarEquipamiento'),



    # Dashboard y datos JSON
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/loc-prod-data/',  views.loc_prod_data,  name='loc_prod_data'),
    path('dashboard/prod-data/', views.prod_data, name='prod_data'),
    path('api/estado-prod-donut/', views.estado_prod_donut_data, name='estado_prod_donut_data'),

    path('items-reservados/', views.items_reservados, name='items_reservados'),
    path('items-reservados/agregar/', views.agregar_pedido_items_reservados, name='agregar_pedido_items_reservados'),



path('pedidos-cambio-reservado-aplicado/', views.pedidos_cambio_reservado_a_aplicado, name='pedidos_cambio_reservado_a_aplicado'),

path('api/item-por-codigo/', views.obtener_item_por_codigo, name='item_por_codigo'),
        path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
path(
    'marcar-pedido-aplicado/<int:pedido_id>/',
    views.marcar_pedido_aplicado,
    name='marcar_pedido_aplicado'
),
path('marcar_pedido_aplicado/<int:pedido_id>/', views.marcar_pedido_aplicado, name='marcar_pedido_aplicado'),
    path('api/pedidos-a-tiempo/', views.pedidos_a_tiempo_data, name='pedidos_a_tiempo_data'),





    # MAPE y Proyecciones
    path('proyeccion/calcular/', views.calcular_mape_manual, name='calcular_mape'),
    path('proyeccion/mape/', views.ver_mape, name='ver_mape'),
    path('proyeccion/mape/borrar/', views.borrar_mape, name='borrar_mape'),
    path('proyeccion/historial/', views.historial_mape, name='historial_mape'),
    path('proyeccion/historial/limpiar/', views.limpiar_historial_mape, name='limpiar_historial_mape'),

    # NUEVA ruta para eliminar solo proyecciones
    path('limpiar-proyecciones/', views.limpiar_proyecciones, name='limpiar_proyecciones'),
    #CHATBOT
    path('chatbot/', views.chatbot_faq, name='chatbot_faq'),
    path('informacion/', views.informacion, name='informacion'),

]
