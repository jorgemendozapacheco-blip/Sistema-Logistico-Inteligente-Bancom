from django import forms
from .models import Pedido, ProyeccionVenta , Item


#Recien agregado
class ProyeccionVentaForm(forms.ModelForm):
    class Meta:
        model = ProyeccionVenta
        fields = ['fecha', 'item', 'venta_proyectada', 'venta_real']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # --- lo de las opciones del item, igual que antes ---
        items = Item.objects.exclude(nombre__isnull=True).exclude(nombre="").order_by('nombre')
        nombres_agregados = set()
        choices = []
        for item in items:
            if item.nombre not in nombres_agregados:
                choices.append((item.pk, item.nombre))
                nombres_agregados.add(item.nombre)
        self.fields['item'].choices = [('', 'Seleccione un producto')] + choices