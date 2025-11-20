from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.utils.timezone import now
import uuid
import datetime
class Item(models.Model):
    codigo = models.CharField(max_length=50, primary_key=True)
    etiqueta = models.CharField(max_length=100, null=True, blank=True)
    numerodeserie = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    motivo_estado = models.CharField(max_length=200, null=True, blank=True)
    nombre = models.CharField(max_length=200, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)
    marca = models.CharField(max_length=100, null=True, blank=True)
    proveedor = models.CharField(max_length=150, null=True, blank=True)
    localidad = models.CharField(max_length=100, null=True, blank=True)
    oficina = models.CharField(max_length=100, null=True, blank=True)
    piso = models.CharField(max_length=50, null=True, blank=True)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    cpu_type = models.CharField(max_length=100, null=True, blank=True)
    disk_gb = models.IntegerField(null=True, blank=True)
    os_arch = models.CharField(max_length=50, null=True, blank=True)
    os_name = models.CharField(max_length=100, null=True, blank=True)
    os_type = models.CharField(max_length=50, null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    ram_gb  = models.IntegerField(null=True, blank=True)
    empleado = models.CharField(max_length=150, null=True, blank=True)
    dept_per = models.CharField(max_length=100, null=True, blank=True)
    zona = models.CharField(max_length=100, null=True, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entregada_real = models.DateField(null=True, blank=True)
    cambio_reservado_a_aplicado = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.codigo} – {self.nombre}"



class Equipamiento(models.Model):
    NOMBRE_PRODUCTO_CHOICES = [
        ('Disco', 'Disco'),
        ('Memoria', 'Memoria'),
        ('Mouse', 'Mouse'),
        ('Teclado', 'Teclado'),
        ('Kit inalámbrico', 'Kit inalámbrico'),
    ]

    CAPACIDAD_CHOICES = [
        ('-', '-'),
        ('240 GB', '240 GB'),
        ('480 GB', '480 GB'),
    ]

    MEMORIA_CHOICES = [
        ('-', '-'),
        ('2 GB', '2 GB'),
        ('4 GB', '4 GB'),
        ('8 GB', '8 GB'),
        ('16 GB', '16 GB'),
        ('32 GB', '32 GB'),
    ]

    MODELO_CHOICES = [
        ('-', '-'),
        ('Laptop', 'Laptop'),
        ('Desktop', 'Desktop'),
    ]

    ESTADO_CHOICES = [
        ('Reservado', 'Reservado'),
        ('Aplicado', 'Aplicado'),
    ]
    codigo = models.CharField(max_length=32, unique=True, blank=True)
    nombre_producto = models.CharField(max_length=50, choices=NOMBRE_PRODUCTO_CHOICES)
    capacidad = models.CharField(max_length=10, choices=CAPACIDAD_CHOICES, default='-')
    memoria = models.CharField(max_length=10, choices=MEMORIA_CHOICES, blank=True, null=True)
    modelo = models.CharField(max_length=10, choices=MODELO_CHOICES, blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="Reservado")

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"EQP-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)



class Pedido(models.Model):
    numero = models.CharField(max_length=20, unique=True, editable=False)
    fecha_creacion = models.DateField(auto_now_add=True)
    localidad = models.CharField(max_length=100, null=True, blank=True)
    zona = models.CharField(max_length=30, blank=True, null=True)  # <--- AGREGA ESTA LÍNEA

    def save(self, *args, **kwargs):
        if not self.numero:
            today = self.fecha_creacion or timezone.localdate()
            seq = Pedido.objects.filter(fecha_creacion=today).count() + 1
            self.numero = f"PED-{today.strftime('%Y%m%d')}-{seq:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero


class PedidoItem(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='lineas')
    item = models.ForeignKey('Item', on_delete=models.PROTECT)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    # No incluimos fecha_entregada_real según tu nuevo flujo
    localidad = models.CharField(max_length=100, null=True, blank=True)
    # Si quieres guardar el estado anterior del item para el histórico:
    estado_anterior = models.CharField(max_length=100, null=True, blank=True)
    fecha_entregada_real = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.pedido.numero} - {self.item.codigo}"

    # Si quieres fácil acceso al código, agrega esta propiedad
    @property
    def codigo(self):
        return self.item.codigo
    








class ProyeccionVenta(models.Model):
    fecha = models.DateField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    venta_proyectada = models.IntegerField()
    venta_real = models.IntegerField()

    def mape_individual(self):
        if self.venta_real == 0:
            return None  # evita división por cero
        return abs((self.venta_real - self.venta_proyectada) / self.venta_real) * 100

    def __str__(self):
        return f"{self.item.codigo} ({self.fecha})"

class HistoricoMAPE(models.Model):
    fecha = models.DateTimeField()
    mape = models.FloatField()
    cantidad_registros = models.IntegerField()
    proyecciones_incluidas = models.ManyToManyField('ProyeccionVenta', blank=True)
    
    # NUEVO CAMPO:
    tipo_error = models.CharField(
        max_length=20,
        choices=[("Favorable", "Favorable"), ("Desfavorable", "Desfavorable"), ("Mixto", "Mixto")],
        default="Mixto"
    )

    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.mape}%"






class PedidoEquipamiento(models.Model):
    pedido = models.ForeignKey('Pedido', related_name='equipamientos', on_delete=models.CASCADE)
    equipamiento = models.ForeignKey('Equipamiento', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=[('Reservado', 'Reservado'), ('Aplicado', 'Aplicado')], default='Reservado')
    fecha_entrega_estimada = models.DateField()