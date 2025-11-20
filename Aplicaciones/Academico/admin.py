from django.contrib import admin
from.models import Item,Equipamiento,PedidoItem,Pedido,ProyeccionVenta
# Register your models here.
admin.site.register(Item)

admin.site.register(Equipamiento)

admin.site.register(PedidoItem)

admin.site.register(Pedido)


admin.site.register(ProyeccionVenta) #Recien agregado del model
