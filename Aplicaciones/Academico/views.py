import pandas as pd
import tempfile
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Item, Pedido, PedidoItem, PedidoEquipamiento
from .utils import importar_excel
from .models import Equipamiento
from django.utils import timezone
from datetime import timedelta
import re
from django.db import transaction
from datetime import timedelta






#Recien agregado
from .models import ProyeccionVenta 
from .forms import ProyeccionVentaForm
#aca igual
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProyeccionVenta, HistoricoMAPE
import numpy as np
from django.utils.timezone import now
from .models import ProyeccionVenta, HistoricoMAPE
from .forms import ProyeccionVentaForm
from django.db.models import Avg
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime
from calendar import monthrange
from django.db.models import Sum

from django.views.decorators.csrf import csrf_exempt
from rapidfuzz import process

# 1) Cabeceras de Excel que queremos importar


@login_required
def home(request):
    return redirect('academico:modulo1')
@login_required
def inventario(request):
    if request.method == 'POST' and 'excel_file' in request.FILES:
        f = request.FILES['excel_file']
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            for chunk in f.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # Importar por lotes (ajusta batch_size aquí)
        try:
            importar_excel(tmp_path, batch_size=100000)  # puedes subir a 3000-5000 si tienes mucha RAM
            messages.success(request, "Importación completada correctamente.")
        except Exception as e:
            messages.error(request, f"Error durante la importación: {e}")

        return redirect('academico:inventario')

    items = Item.objects.all()
    prefijo = "BCO-COMERCIO-PE-"
    for item in items:
        if item.localidad and item.localidad.startswith(prefijo):
            item.localidad_limpia = item.localidad[len(prefijo):]
        else:
            item.localidad_limpia = item.localidad or ""

    return render(request, 'inventario.html', {'items': items})


@login_required
def clear_inventario(request):
    if request.method == 'POST':
        # Elimina primero todos los PedidoItem (y Pedido si deseas)
        from .models import PedidoItem, Pedido
        PedidoItem.objects.all().delete()
        Pedido.objects.all().delete()  # si quieres limpiar también pedidos
        Item.objects.all().delete()
        messages.success(request, 'Inventario limpiado correctamente.')
    return redirect('academico:inventario')

@login_required
def modulo1(request):
    equipamientos = Equipamiento.objects.all()
    # Para los choices, pasar opciones al template
    equip_choices = {
        'nombre_producto': Equipamiento.NOMBRE_PRODUCTO_CHOICES,
        'capacidad': Equipamiento.CAPACIDAD_CHOICES,
        'memoria': Equipamiento.MEMORIA_CHOICES,
        'modelo': Equipamiento.MODELO_CHOICES,
    }
    bajos_stock = equipamientos.filter(cantidad__lt=5)

    return render(request, 'modulo1.html', {
        "equipamientos": equipamientos, 
        "equip_choices": equip_choices,
        "bajos_stock": bajos_stock,
        })


@login_required
def registrarEquipamiento(request):
    nombre_producto = request.POST['nombre_producto']
    capacidad = request.POST.get('capacidad', '-')
    memoria = request.POST.get('memoria', None)
    modelo = request.POST.get('modelo', None)
    cantidad = int(request.POST.get('cantidad', 1))
    estado = request.POST.get('estado', 'Reservado')

    equip = Equipamiento.objects.create(
        nombre_producto=nombre_producto,
        capacidad=capacidad,
        memoria=memoria,
        modelo=modelo,
        cantidad=cantidad,
        estado=estado
    )
    messages.success(request, f'Equipamiento agregado (código: {equip.codigo})')
    return redirect('/modulo1/')

@login_required
def editarEquipamiento(request):
    codigo = request.POST['codigo']
    equip = get_object_or_404(Equipamiento, codigo=codigo)

    equip.nombre_producto = request.POST['nombre_producto']
    equip.capacidad = request.POST.get('capacidad', '-')
    equip.memoria = request.POST.get('memoria', None)
    equip.modelo = request.POST.get('modelo', None)
    equip.cantidad = int(request.POST.get('cantidad', 1))
    equip.estado = request.POST.get('estado', 'Reservado')
    equip.save()

    messages.success(request, 'Equipamiento actualizado correctamente')
    return redirect('/modulo1/')

@login_required
def eliminarEquipamiento(request, codigo):
    equip = get_object_or_404(Equipamiento, codigo=codigo)
    equip.delete()
    messages.success(request, 'Equipamiento eliminado correctamente')
    return redirect('academico:modulo1')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    prefix = "BCO-COMERCIO-PE-"
    localidades_raw = Item.objects.values_list('localidad', flat=True).distinct()
    localidades = []
    for loc in localidades_raw:
        label = loc[len(prefix):] if loc and loc.startswith(prefix) else loc
        localidades.append({'value': loc, 'label': label})

    nombres = Item.objects.values_list('nombre', flat=True).distinct()
    estados = Item.objects.values_list('estado', flat=True).distinct()

    # KPI pedidos reservados y aplicados (por estado de ítems en cada pedido)
    total_pedidos_reservados = Pedido.objects.filter(
        lineas__item__estado__iexact="Reservado"
    ).distinct().count()
    total_pedidos_aplicados = Pedido.objects.filter(
        lineas__item__estado__iexact="Aplicado"
    ).distinct().count()

    total_localidades = len(localidades)

    return render(request, 'dashboard.html', {
        'localidades': localidades,
        'nombres': nombres,
        'estados': estados,
        'items_count': Item.objects.count(),
        'total_localidades': total_localidades,
        'total_pedidos_reservados': total_pedidos_reservados,
        'total_pedidos_aplicados': total_pedidos_aplicados,
    })
@login_required
def loc_prod_data(request):
    loc  = request.GET.get('loc', '')
    prod = request.GET.get('prod','')

    prefix = "BCO-COMERCIO-PE-"

    def clean_loc(loc_str):
        if loc_str and loc_str.startswith(prefix):
            return loc_str[len(prefix):]
        return loc_str or "todas las localidades"

    # Usa la localidad limpia para los filtros y conteos
    loc_filter = loc if loc else None

    if loc_filter:
        count_loc = Item.objects.filter(localidad=loc_filter).count()
    else:
        count_loc = Item.objects.count()

    if loc_filter and prod:
        count_both = Item.objects.filter(localidad=loc_filter, nombre=prod).count()
        labels = [f'{prod} en {clean_loc(loc)}', f'Otros en {clean_loc(loc)}']
        counts = [count_both, count_loc - count_both]
    else:
        labels = [f'Items en {clean_loc(loc)}', 'Otros']
        counts = [count_loc, Item.objects.count() - count_loc]

    return JsonResponse({'labels': labels, 'counts': counts})


@login_required
def prod_data(request):
    """
    Si llega ?prod=Nombre, devuelve [Nombre]:[count]
    Si no, devuelve todos los productos con sus counts.
    """
    prod = request.GET.get('prod', '').strip()
    if prod:
        # Sólo el producto seleccionado
        count = Item.objects.filter(nombre=prod).count()
        labels = [prod]
        counts = [count]
    else:
        # Todos los productos
        qs = (
            Item.objects
            .values('nombre')
            .annotate(count=Count('codigo'))  # <--- CAMBIA AQUÍ
            .order_by('-count')
        )
        labels = [row['nombre'] for row in qs]
        counts = [row['count']  for row in qs]

    return JsonResponse({'labels': labels, 'counts': counts})

@login_required
def prod_state_data(request):

    # 1) estados únicos
    estados_qs = Item.objects.values_list('estado', flat=True).distinct()
    estados = [e or 'Sin estado' for e in estados_qs]

    # 2) conteos agrupados
    qs = Item.objects.values('nombre', 'estado').annotate(count=Count('id'))

    # 3) construir mapa producto→{estado:count}
    data_map = {}
    for row in qs:
        prod = row['nombre']
        est  = row['estado'] or 'Sin estado'
        cnt  = row['count']
        data_map.setdefault(prod, {})[est] = cnt

    productos = sorted(data_map.keys())

    # 4) datasets para cada estado
    datasets = []
    for i, est in enumerate(estados):
        datasets.append({
            'label': est,
            'data': [ data_map[p].get(est, 0) for p in productos ],
            'backgroundColor': f'hsl({(i*60)%360},70%,60%)'
        })

    return JsonResponse({'labels': productos, 'datasets': datasets})

@login_required
def estado_prod_donut_data(request):
    estado = request.GET.get('estado', '').strip()
    producto = request.GET.get('producto', '').strip()

    # 1) total de ítems en este estado
    if estado:
        total_en_estado = Item.objects.filter(estado=estado).count()
    else:
        total_en_estado = Item.objects.count()

    # 2) ítems que además coinciden en producto
    if estado and producto:
        seleccionados = Item.objects.filter(estado=estado, nombre=producto).count()
        labels = [f'{producto} en "{estado}"', f'Otros en "{estado}"']
        counts = [seleccionados, total_en_estado - seleccionados]
    else:
        # si no hay filtro o sólo uno, muestro todo vs resto
        labels = [f'Ítems en "{estado or "todos"}"', 'Otros']
        counts = [total_en_estado, Item.objects.count() - total_en_estado]

    return JsonResponse({'labels': labels, 'counts': counts})



@login_required
def obtener_item_por_codigo(request):
    codigo = request.GET.get('codigo', '').strip()
    try:
        item = Item.objects.get(codigo__iexact=codigo)
        data = {
            'codigo': item.codigo,
            'etiqueta': item.etiqueta or '',
            'numerodeserie': item.numerodeserie or '',
            'estado': item.estado or '',
            'motivo_estado': item.motivo_estado or '',
            'proveedor': item.proveedor or '',
            'modelo': item.modelo or '',
            'marca': item.marca or '',
            'nombre': item.nombre or '',
            'localidad': item.localidad or '',
            'zona': item.zona or '',
            'cpu_type': item.cpu_type or '',
            'fecha_entrega_estimada': item.fecha_entrega_estimada.isoformat() if item.fecha_entrega_estimada else '',
            'fecha_entregada_real': item.fecha_entregada_real.isoformat() if item.fecha_entregada_real else '',
        }
        return JsonResponse(data)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Código no encontrado'}, status=404)



@login_required
def pedidos_cambio_reservado_a_aplicado(request):
    pedidos = (
        Pedido.objects.prefetch_related('lineas__item')
        .filter(lineas__item__estado="Aplicado")
        .distinct()
    )

    pedidos_aplicados = []
    for ped in pedidos:
        lineas = ped.lineas.all()
        # Solo pedidos donde TODAS las líneas están aplicadas y tienen fecha_entregada_real
        if all(li.item.estado == "Aplicado" and li.fecha_entregada_real for li in lineas):
            pedidos_aplicados.append(ped)

    pedidos_lima = [p for p in pedidos_aplicados if any(li.item.zona.upper() == "LIMA" for li in p.lineas.all())]
    pedidos_provincia = [p for p in pedidos_aplicados if all(li.item.zona.upper() != "LIMA" for li in p.lineas.all())]

    return render(request, "pedidos_cambio_reservado_a_aplicado.html", {
        "pedidos_lima": pedidos_lima,
        "pedidos_provincia": pedidos_provincia,
    })

@login_required
@require_POST
def agregar_pedido_items_reservados(request):
    codigos_raw = request.POST.get('codigos', '').strip()
    localidad_destino = request.POST.get('localidad', '').strip()
    codigos = [c.strip() for c in codigos_raw.splitlines() if c.strip()]
    equipamientos = Equipamiento.objects.all()

    # --- VALIDACIONES DE LOCALIDAD ---
    if not localidad_destino:
        messages.error(request, 'Debe seleccionar una localidad.')
        request.session['abrir_modal_agregar_pedido'] = True
        return redirect('academico:items_reservados')

    # SIEMPRE trabajar con localidad CON PREFIJO
    PREFIJO = "BCO-COMERCIO-PE-"
    localidad_db = f"{PREFIJO}{localidad_destino}" if not localidad_destino.startswith(PREFIJO) else localidad_destino

    # --- 1. Procesar ÍTEMS DEL EXCEL (códigos) ---
    zona_destino = (
        Item.objects.filter(localidad__iexact=localidad_db)
        .values_list('zona', flat=True)
        .first()
    )
    if not zona_destino:
        # Intenta buscar sin importar el prefijo, solo por si acaso
        zona_destino = (
            Item.objects.filter(localidad__iendswith=localidad_destino)
            .values_list('zona', flat=True)
            .first()
        )
    if not zona_destino:
        zona_destino = "PROVINCIA"

    codigos_reservados = []
    items_a_reservar = []
    codigos_no_encontrados = []

    for codigo in codigos:
        try:
            item = Item.objects.get(codigo__iexact=codigo)
            if item.estado and item.estado.lower() == 'reservado':
                codigos_reservados.append(codigo)
            else:
                items_a_reservar.append(item)
        except Item.DoesNotExist:
            codigos_no_encontrados.append(codigo)

    if codigos_reservados:
        messages.error(request, f'No se creó el pedido porque los siguientes códigos ya están en estado "Reservado": {", ".join(codigos_reservados)}')
        request.session['abrir_modal_agregar_pedido'] = True
        return redirect('academico:items_reservados')

    if codigos_no_encontrados and not equipamientos.exists():
        messages.error(request, f'No se creó el pedido porque los siguientes códigos no existen: {", ".join(codigos_no_encontrados)}')
        request.session['abrir_modal_agregar_pedido'] = True
        return redirect('academico:items_reservados')

    # --- 2. Procesar EQUIPAMIENTOS SELECCIONADOS ---
    equip_seleccionados = []
    for equip in equipamientos:
        key = f"equip_{equip.codigo}"
        try:
            cantidad = int(request.POST.get(key, "0"))
        except (ValueError, TypeError):
            cantidad = 0
        if cantidad > 0:
            if cantidad > equip.cantidad:
                messages.error(request, f'No hay suficiente stock de {equip.nombre_producto}. Disponible: {equip.cantidad}.')
                request.session['abrir_modal_agregar_pedido'] = True
                return redirect('academico:items_reservados')
            equip_seleccionados.append((equip, cantidad))

    if not items_a_reservar and not equip_seleccionados:
        messages.error(request, 'Debe agregar al menos un ítem o equipamiento al pedido.')
        request.session['abrir_modal_agregar_pedido'] = True
        return redirect('academico:items_reservados')

    # --- 3. CREAR PEDIDO Y GUARDAR LÓGICA EN UNA TRANSACCIÓN ---
    with transaction.atomic():
        pedido = Pedido.objects.create(localidad=localidad_db, zona=zona_destino)
        hoy = timezone.localdate()

        # Ítems del Excel
        for item in items_a_reservar:
            estado_ant = item.estado
            item.estado = "Reservado"
            item.localidad = localidad_db  # Guardar CON prefijo
            item.zona = zona_destino
            dias = 4 if zona_destino.strip().upper() == "LIMA" else 7
            item.fecha_entrega_estimada = hoy + timedelta(days=dias)
            item.save()
            PedidoItem.objects.create(
                pedido=pedido,
                item=item,
                fecha_entrega_estimada=item.fecha_entrega_estimada,
                localidad=localidad_db,  # Guardar CON prefijo
                estado_anterior=estado_ant,
            )
        
        # Equipamientos (con decremento de stock)
        for equip, cant in equip_seleccionados:
            dias = 4 if zona_destino.strip().upper() == "LIMA" else 7
            equip.cantidad -= cant
            equip.save()
            PedidoEquipamiento.objects.create(
                pedido=pedido,
                equipamiento=equip,
                cantidad=cant,
                fecha_entrega_estimada=hoy + timedelta(days=dias),
                estado="Reservado",  # Si tienes este campo
            )

    request.session.pop('abrir_modal_agregar_pedido', None)
    messages.success(request, f'Pedido {pedido.numero} creado correctamente.')
    return redirect('academico:items_reservados')

@login_required  
def items_reservados(request):
    prefijo = "BCO-COMERCIO-PE-"
    items_lima = Item.objects.filter(estado__iexact="reservado", zona__iexact="LIMA")
    items_provincia = Item.objects.filter(estado__iexact="reservado").exclude(zona__iexact="LIMA")

    def limpiar_localidad(items):
        lista = list(items)
        for item in lista:
            if item.localidad and item.localidad.startswith(prefijo):
                item.localidad_limpia = item.localidad[len(prefijo):]
            else:
                item.localidad_limpia = item.localidad or ""
        return lista

    items_lima = limpiar_localidad(items_lima)
    items_provincia = limpiar_localidad(items_provincia)

    localidades_raw = Item.objects.values_list('localidad', flat=True).distinct()
    localidades = []
    for loc in localidades_raw:
        limpia = loc[len(prefijo):] if loc and loc.startswith(prefijo) else loc or ''
        if limpia and limpia not in localidades:
            localidades.append(limpia)

    pedidos = Pedido.objects.prefetch_related('lineas__item').order_by('-fecha_creacion')
    # SOLO pedidos con AL MENOS UN ítem en estado "Reservado"
    pedidos_lima = pedidos.filter(
        lineas__item__zona__iexact="LIMA",
        lineas__item__estado__iexact="Reservado"
    ).distinct()
    pedidos_provincia = pedidos.exclude(
        lineas__item__zona__iexact="LIMA"
    ).filter(
        lineas__item__estado__iexact="Reservado"
    ).distinct()

    # NUEVO: Equipamientos disponibles para mostrar en el formulario
    equipamientos = Equipamiento.objects.filter(cantidad__gt=0)

    abrir_modal = request.session.pop('abrir_modal_agregar_pedido', False)
    return render(request, "items_reservados.html", {
        "items_lima": items_lima,
        "items_provincia": items_provincia,
        "localidades": localidades,
        "pedidos_lima": pedidos_lima,
        "pedidos_provincia": pedidos_provincia,
        "equipamientos": equipamientos,  # <--- para el select en el modal
        "abrir_modal_agregar_pedido": abrir_modal,
    })
@login_required
@require_POST
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == "POST":
        for linea in pedido.lineas.all():
            item = linea.item
            if linea.estado_anterior is not None:
                item.estado = linea.estado_anterior
                item.save()
        pedido.delete()
        messages.success(request, f"Pedido {pedido.numero} eliminado correctamente y estados de los ítems restaurados.")
        request.session.pop('abrir_modal_agregar_pedido', None)
        return redirect('academico:items_reservados')
    return redirect('academico:items_reservados')

@login_required
@require_POST
def marcar_pedido_aplicado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    hoy = timezone.localdate()
    for linea in pedido.lineas.all():
        item = linea.item
        item.estado = "Aplicado"
        item.save()
        linea.fecha_entregada_real = hoy
        linea.save()
    # NO ELIMINES el pedido ni sus líneas
    messages.success(request, f'Todos los ítems del pedido {pedido.numero} fueron marcados como Aplicados.')
    return redirect('academico:items_reservados')




@login_required
def pedidos_a_tiempo_data(request):
    # 1. Considera SOLO pedidos que tengan AL MENOS UN item aplicado y fechas reales/estimadas
    pedidos_aplicados = Pedido.objects.filter(
        lineas__item__estado="Aplicado",
        lineas__fecha_entrega_estimada__isnull=False,
        lineas__fecha_entregada_real__isnull=False
    ).distinct()

    a_tiempo = 0
    fuera_tiempo = 0
    total = pedidos_aplicados.count()
    lima_tiempo = 0
    lima_total = 0
    provincia_tiempo = 0
    provincia_total = 0

    for pedido in pedidos_aplicados:
        # Encuentra la zona predominante (puedes ajustar la lógica si quieres solo la del primer item)
        zona = None
        if pedido.zona:
            zona = pedido.zona.upper()
        else:
            # Fallback: toma la zona del primer ítem, si no tiene
            linea = pedido.lineas.first()
            zona = linea.item.zona.upper() if linea and linea.item.zona else ""

        if zona == "LIMA":
            lima_total += 1
            dias_max = 4
        else:
            provincia_total += 1
            dias_max = 7

        # REGLA CLAVE:
        # El pedido es "a tiempo" SOLO si TODOS los ítems están en estado Aplicado
        # y todas las fechas_entregada_real <= fecha_entrega_estimada según zona

        lineas = pedido.lineas.filter(
            fecha_entrega_estimada__isnull=False,
            fecha_entregada_real__isnull=False
        )

        # Si algún ítem está fuera de tiempo o no está en "Aplicado", todo el pedido es fuera de tiempo
        pedido_en_tiempo = True
        for li in lineas:
            if li.item.estado != "Aplicado":
                pedido_en_tiempo = False
                break
            # Se permite a tiempo solo si entregado <= estimada
            if li.fecha_entregada_real > li.fecha_entrega_estimada:
                pedido_en_tiempo = False
                break

        if pedido_en_tiempo:
            a_tiempo += 1
            if zona == "LIMA":
                lima_tiempo += 1
            else:
                provincia_tiempo += 1
        else:
            fuera_tiempo += 1

    porcentaje = int((a_tiempo / total) * 100) if total else 0
    otd_lima = int((lima_tiempo / lima_total) * 100) if lima_total else 0
    otd_provincia = int((provincia_tiempo / provincia_total) * 100) if provincia_total else 0

    data = {
        "labels": ["A tiempo", "Fuera de tiempo"],
        "values": [a_tiempo, fuera_tiempo],
        "porcentaje": porcentaje,
        "a_tiempo": a_tiempo,
        "fuera_tiempo": fuera_tiempo,
        "otd_lima": otd_lima,
        "otd_provincia": otd_provincia,
        "total": total,
    }
    return JsonResponse(data)

@login_required
def calcular_mape_manual(request):

    form = ProyeccionVentaForm()
    mape_result = None

    if request.method == "POST":
        if "registrar" in request.POST:
            form = ProyeccionVentaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "✔️ Proyección registrada correctamente.")
            else:
                messages.error(request, "⚠️ Revisa los datos del formulario.")
        elif "calcular" in request.POST:
            proyecciones = (
                ProyeccionVenta.objects
                .filter(venta_real__isnull=False,
                        venta_proyectada__isnull=False)
                .exclude(historicomape__isnull=False)   
            )
            if not proyecciones.exists():
                messages.warning(
                    request,
                    "⚠️ No hay proyecciones nuevas para calcular el MAPE."
                )
            else:
                reales    = np.array([p.venta_real       for p in proyecciones],dtype=float)
                estimados = np.array([p.venta_proyectada for p in proyecciones],dtype=float)

                # MAPE(*individual de este lote*)
                mape_result = round(np.mean(np.abs((reales - estimados) / reales)) * 100, 2)

                tipo_error = _get_tipo_error(mape_result)
                
                # Guardar en histórico
                h = HistoricoMAPE.objects.create(
                        fecha=now(),
                        mape=mape_result,
                        cantidad_registros=len(proyecciones),
                        tipo_error=tipo_error,
                )
                h.proyecciones_incluidas.set(proyecciones)
                messages.success(
                    request,
                    f"✅ MAPE calculado: {mape_result:.2f}%"
                )
    return render(request, "calcular_mape.html",
                  {"form": form, "mape_result": mape_result})

 
@login_required
def borrar_mape(request):
    if request.method == "POST":
        HistoricoMAPE.objects.all().delete()
        messages.success(request, "Historial de MAPE eliminado correctamente.")
    return redirect('academico:ver_mape')

def _get_tipo_error(valor_mape: float) -> str:

    if valor_mape < 10:
        return "Favorable"
    if valor_mape < 20:
        return "Aceptable"
    if valor_mape < 50:
        return "Revisar"
    return "Crítico"

def ver_mape(request):
    """Historial de cálculos MAPE recientes + promedio global."""
    historial = HistoricoMAPE.objects.all().order_by("-fecha")

    # ─────────────── PAGINACIÓN ───────────────
    paginator   = Paginator(historial, 10)          # 10 registros por página
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # ─────────────── PROMEDIO MAPE GLOBAL ───────────────
    # Incluimos TODOS los registros (también los que tienen 0 %)
    total_registros = sum(h.cantidad_registros for h in page_obj)
    mape_total      = sum(h.mape * h.cantidad_registros for h in page_obj)

    promedio_mape = round(mape_total / total_registros, 2) if total_registros else None
    tiene_mape    = total_registros > 0

    # ─────────────── Funciones auxiliares ───────────────
    def _get_mape_color(val):
        """Devuelve la clase-color según el rango del MAPE global."""
        if val is None:      return "secondary"
        if val < 10:         return "success"    # verde
        if 10 <= val < 20:   return "warning"    # amarillo
        if 20 <= val < 50:   return "orange"     # naranja (clase propia)
        return "danger"                          # rojo

    # ─────────────── Formateo fila a fila ───────────────
    for h in page_obj:
        val = h.mape if h.mape is not None else 0
        h.tipo_error = _get_tipo_error(val)
        h.mape_str = f"{val:.2f}%"
        item_rel = h.proyecciones_incluidas.first()
        h.item_nombre = item_rel.item.nombre if item_rel else "—"

    # ─────────────── Contexto al template ───────────────
    context = {
        "historico"     : page_obj,                    # filas paginadas
        "pagina"        : page_obj,                    # alias → si lo usas en la plantilla
        "promedio_mape" : promedio_mape,               # 0.00 → se envía igual
        "mape_color"    : _get_mape_color(promedio_mape),
        "tiene_mape"    : tiene_mape,
    }
    return render(request, "ver_mape.html", context)

@login_required
def historial_mape(request):
    proyecciones = ProyeccionVenta.objects.select_related('item').order_by('-fecha')

    # Calcular MAPE individual por proyección
    for p in proyecciones:
        if p.venta_real and p.venta_real != 0:
            mape_individual = abs((p.venta_proyectada - p.venta_real) / p.venta_real) * 100
        else:
            mape_individual = 0.00
        p.mape_individual = round(mape_individual, 2)

    return render(request, 'historico_mape.html', {'proyecciones': proyecciones})

@login_required
def limpiar_historial_mape(request):
    if request.method == 'POST':
        ProyeccionVenta.objects.all().delete()
        HistoricoMAPE.objects.all().delete()
        messages.success(request, "🧹 Historial limpiado correctamente.")
    return redirect(request.META.get('HTTP_REFERER', 'academico:historial_mape'))
    
@login_required
def limpiar_proyecciones(request):
    """
    Elimina solo las proyecciones registradas (ProyeccionVenta)
    sin afectar el historial MAPE.
    """
    if request.method == "POST":
        ProyeccionVenta.objects.all().delete()
        messages.success(request, "📦 Proyecciones eliminadas correctamente.")
    return redirect('academico:historial_mape')

def debe_mostrar_alerta():
    today = datetime.now().day
    last_day = monthrange(datetime.now().year, datetime.now().month)[1]
    return today <= 2 or today >= (last_day - 3)

# --- LISTAS BASE (puedes mantenerlas actualizadas dinámicamente si lo deseas) ---
LOCALIDADES = [
    "OE-PUCALLPA", "OP-SAN-ISIDRO", "AG-MIRAFLORES", "AG-ARENALES", "AG-JESUS-MARIA", "AG-SAN-ISIDRO", "AG-PIURA",
    "AG-CHACARILLA", "AG-LAMPA", "OE-CUSCO", "AG-FAUCETT", "AG-SAN-BORJA", "AG-IQUITOS", "OE-CUARTEL-GENERAL-EJERCITO",
    "OE-TUMBES", "AG-CHICLAYO", "AG-HUANCAYO", "AG-SIMON SALGUERO", "OE-TARAPOTO", "AG-CAMANA", "AG-TRUJILLO",
    "OI-FINPOL", "AG-SANTA-ANITA", "OE-PISCO", "OE-SULLANA", "OE-LOS-OLIVOS", "OE-CAJAMARCA", "AG-AREQUIPA",
    "OE-BAZAR-NAVAL", "OE-COEDE-ESCUELA-MILITAR", "TDP-PE-LINCE", "TDP-PE-MONTERRICO", "OE-CUARTEL-FAP", "OI-GRUPO-AEREO-8",
    "OI-BASE-LAS-PALMAS", "OE-UNFV-POSTGRADO", "OE-SEDAPAR"
]

PRODUCTOS = [
    "MONITOR", "LAPTOP", "DESKTOP", "BIOMETRICO", "IMPRESORA MATRICIAL", "SWITCH", "PINPAD", "IMPRESORA TERMICA",
    "ROUTER", "IMPRESORA LASER", "PROYECTOR", "SERVIDOR", "IMPRESORA MULTIFUNCIONAL", "DISCO DURO",
    "IMPRESORA INYECCION DE TINTA", "TELEFONO ANALOGICO", "UNIDAD CD/DVD", "DOCKING STATION", "TELEFONO IP",
    "AS400", "CENTRAL ANALOGICA", "BLADE", "PIN PAD", "ACCES POINT", "TELEFONO DIGITAL", "DEMARCADOR",
    "BANDEJA MODULAR", "ESCANER", "EXPANSION", "TELEFONO ANALOGO"
]

ESTADOS = [
    "Aplicado", "Fin de vida útil", "Eliminado", "En reparación", "Fuera de servicio", "Recibido", "En inventario", "En préstamo", "Transferido", "Reservado"
]

# --- LÓGICA DINÁMICA ---
def responder_chatbot(pregunta):
    pregunta = pregunta.strip().lower()

# CHEQUEO GENERAL DE STOCK BAJO (antes de cualquier otro intent)
    if ("bajo stock" in pregunta or "stock bajo" in pregunta or "stock crítico" in pregunta or 
    "bajos en stock" in pregunta or "pocos productos" in pregunta or "productos con poco stock" in pregunta):
            return productos_bajo_stock()

            # Preguntas por cantidad de producto
            if re.search(r"cu[aá]nt(os|as) .*?%s.*?(hay|tengo|existen|en inventario)?" % producto.lower(), pregunta):
                cantidad = Item.objects.filter(nombre_producto__icontains=producto).count()
                return f"Actualmente tienes {cantidad} {producto.lower()}(s) en inventario."
            # Listado de productos
            if re.search(r"(lista|muestr[aá]me|d[aá]me|qu[eé]s|cu[aá]les son) .*?%s" % producto.lower(), pregunta):
                lista = Item.objects.filter(nombre_producto__icontains=producto)
                if lista.exists():
                    return "<br>".join([f"{item.codigo} - {item.nombre_producto} - {item.estado} ({item.localidad})" for item in lista[:15]])  # Solo los primeros 15 para no saturar
                else:
                    return f"No hay {producto.lower()}s registrados actualmente."
    
    # === CONSULTAS SOBRE EQUIPAMIENTOS ===
    # === CONSULTAS SOBRE EQUIPAMIENTOS ===

    # Patrón 1: ¿Cuántos [nombre_producto] hay en equipamiento?
    if "cuántos" in pregunta or "cuantos" in pregunta:
        for producto in Equipamiento.objects.values_list('nombre_producto', flat=True).distinct():
            producto_lower = producto.lower()
            if producto_lower in pregunta and "equipamiento" in pregunta:
                equipqs = Equipamiento.objects.filter(nombre_producto__iexact=producto)
                cantidad = equipqs.aggregate(total=Sum('cantidad'))['total'] or 0
                detalles = []
                for e in equipqs:
                    cap = f", Capacidad: {e.capacidad}" if e.capacidad and e.capacidad != "-" else ""
                    mem = f", Memoria: {e.memoria}" if e.memoria and e.memoria not in ("-", "None", None) else ""
                    detalles.append(f"{e.nombre_producto} ({e.modelo}{cap}{mem}): {e.cantidad} unidades")
                respuesta = f"Actualmente tienes {cantidad} {producto_lower}(s) en equipamiento.<br>"
                respuesta += "<br>".join(detalles)
                return respuesta

    # Patrón 2: ¿Cuántos [nombre_producto] modelo [modelo] hay?
    if "cuántos" in pregunta or "cuantos" in pregunta:
        for producto in Equipamiento.objects.values_list('nombre_producto', flat=True).distinct():
            for modelo in Equipamiento.objects.values_list('modelo', flat=True).distinct():
                if modelo and producto:
                    producto_lower = producto.lower()
                    modelo_lower = modelo.lower()
                    if producto_lower in pregunta and modelo_lower in pregunta:
                        equipqs = Equipamiento.objects.filter(
                            nombre_producto__iexact=producto,
                            modelo__iexact=modelo
                        )
                        cantidad = equipqs.aggregate(total=Sum('cantidad'))['total'] or 0
                        detalles = []
                        for e in equipqs:
                            cap = f", Capacidad: {e.capacidad}" if e.capacidad and e.capacidad != "-" else ""
                            mem = f", Memoria: {e.memoria}" if e.memoria and e.memoria not in ("-", "None", None) else ""
                            detalles.append(f"{e.nombre_producto} ({e.modelo}{cap}{mem}): {e.cantidad} unidades")
                        respuesta = f"Actualmente tienes {cantidad} {producto_lower}(s) del modelo {modelo_lower} en equipamiento.<br>"
                        respuesta += "<br>".join(detalles)
                        return respuesta

    # Patrón 3: Lista todos los equipamientos con detalles
    if (("lista" in pregunta or "muestrame" in pregunta or "listado" in pregunta) and "equipamiento" in pregunta):
        productos = Equipamiento.objects.all()
        if productos.exists():
            tabla = "<table border='1' style='border-collapse:collapse;'><tr><th>Producto</th><th>Modelo</th><th>Capacidad</th><th>Memoria</th><th>Cantidad</th></tr>"
            for e in productos:
                cap = e.capacidad if e.capacidad else "-"
                mem = e.memoria if e.memoria else "-"
                tabla += f"<tr><td>{e.nombre_producto}</td><td>{e.modelo}</td><td>{cap}</td><td>{mem}</td><td>{e.cantidad}</td></tr>"
            tabla += "</table>"
            return tabla
        else:
            return "No hay equipamientos registrados actualmente."

    # 2. PREGUNTAS POR ESTADO
    for estado in ESTADOS:
        if estado.lower() in pregunta:
            if re.search(r"cu[aá]nt(os|as) .*?%s.*?(hay|tengo|existen)?" % estado.lower(), pregunta):
                cantidad = Item.objects.filter(estado__iexact=estado).count()
                return f"Actualmente tienes {cantidad} items en estado {estado}."
            if re.search(r"(lista|muestr[aá]me|d[aá]me|qu[eé]s|cu[aá]les son) .*?%s" % estado.lower(), pregunta):
                lista = Item.objects.filter(estado__iexact=estado)
                if lista.exists():
                    return "<br>".join([f"{item.codigo} - {item.nombre_producto} ({item.localidad})" for item in lista[:15]])
                else:
                    return f"No hay items en estado {estado}."
                
    # 3. PREGUNTAS POR LOCALIDAD
    for localidad in LOCALIDADES:
        if localidad.lower() in pregunta:
            if re.search(r"cu[aá]nt(os|as) .*?(hay|tengo|existen)? .*?(en|de) %s" % localidad.lower(), pregunta):
                cantidad = Item.objects.filter(localidad__iexact=localidad).count()
                return f"Actualmente tienes {cantidad} items en {localidad}."
            if re.search(r"(lista|muestr[aá]me|d[aá]me|qu[eé]s|cu[aá]les son).*?(en|de) %s" % localidad.lower(), pregunta):
                lista = Item.objects.filter(localidad__iexact=localidad)
                if lista.exists():
                    return "<br>".join([f"{item.codigo} - {item.nombre_producto} - {item.estado}" for item in lista[:15]])
                else:
                    return f"No hay items registrados en {localidad}."
                
    # 4. COMBINACIONES (PRODUCTO + ESTADO + LOCALIDAD)
    for producto in PRODUCTOS:
        if producto.lower() in pregunta:
            for estado in ESTADOS:
                if estado.lower() in pregunta:
                    for localidad in LOCALIDADES:
                        if localidad.lower() in pregunta:
                            cantidad = Item.objects.filter(
                                nombre_producto__icontains=producto,
                                estado__iexact=estado,
                                localidad__iexact=localidad
                            ).count()
                            return f"Actualmente tienes {cantidad} {producto.lower()}(s) en estado {estado} en {localidad}."
    # 5. PREGUNTAS DIRECTAS GENERALES
    if "cuántos items" in pregunta or "cuantos items" in pregunta:
        total = Item.objects.count()
        return f"Actualmente tienes {total} items en inventario."
    if "bajo stock" in pregunta or "stock crítico" in pregunta or "bajos de stock" in pregunta:
        criticos = Item.objects.filter(cantidad__lte=5)  # O tu criterio de crítico
        if criticos.exists():
            return "<br>".join([f"{i.nombre_producto} ({i.localidad}) - {i.cantidad} unidades" for i in criticos[:15]])
        else:
            return "No hay productos bajos en stock actualmente."
        
    # 6. HISTÓRICO MAPE
    if "promedio mape" in pregunta or "mape global" in pregunta:
        prom = HistoricoMAPE.objects.all().aggregate_avg("mape")['mape__avg']
        return f"El promedio MAPE global es {prom:.2f}%." if prom is not None else "No hay datos de MAPE registrados aún."
    
     # 7. PEDIDOS
    if "cuántos pedidos" in pregunta or "cuantos pedidos" in pregunta or "total de pedidos" in pregunta:
        total = Pedido.objects.count()
        return f"Actualmente tienes {total} pedidos registrados."
    if "pedidos aplicados" in pregunta:
        total = Pedido.objects.filter(estado__iexact="Aplicado").count()
        return f"Actualmente tienes {total} pedidos aplicados."
    if "pedidos reservados" in pregunta:
        total = Pedido.objects.filter(estado__iexact="Reservado").count()
        return f"Actualmente tienes {total} pedidos reservados."
    if "lista los pedidos" in pregunta or "qué pedidos existen" in pregunta:
        pedidos = Pedido.objects.all()
        if pedidos.exists():
            return "<br>".join([f"Pedido {p.id}: {p.estado}" for p in pedidos[:15]])
        else:
            return "No hay pedidos registrados actualmente."
        
    # 8. LOCALIDADES DISPONIBLES
    if "localidades" in pregunta or "agencias" in pregunta:
        return "<br>".join(LOCALIDADES)

    # 9. PRODUCTOS DISPONIBLES
    if "productos" in pregunta and "hay" in pregunta:
        return "<br>".join(PRODUCTOS)

    # 10. ESTADOS DISPONIBLES
    if "estados" in pregunta:
        return "<br>".join(ESTADOS)

    # SI NO SABE RESPONDER
    return "Lo siento, no tengo información suficiente para responder eso por ahora."

    # --- VIEW DEL CHATBOT ---
@csrf_exempt
def chatbot_faq(request):
    if request.method == "POST":
        pregunta = request.POST.get("pregunta", "")
        respuesta = responder_chatbot(pregunta)
        return JsonResponse({"respuesta": respuesta})

def productos_bajo_stock():
    # Considera 'Equipamiento' como tu modelo de la tabla, o usa el que corresponda
    bajos = Equipamiento.objects.filter(cantidad__lt=5)
    if bajos.exists():
        mensajes = []
        for eq in bajos:
            mensajes.append(f"Quedan {eq.cantidad} unidades de {eq.nombre_producto} de {eq.modelo}")
        return "¡Atención!<br>" + "<br>".join(mensajes)
    else:
        return "No hay productos bajos en stock actualmente."
    
@login_required
def informacion(request):
    return render(request, 'informacion.html')