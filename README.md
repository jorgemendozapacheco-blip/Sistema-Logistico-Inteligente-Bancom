# 🏦 Sistema Inteligente de Gestión Logística - BANCOM

![Estado](https://img.shields.io/badge/Estado-Finalizado-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Frontend-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

> **Proyecto de Tesis para optar el Título de Ingeniero de Sistemas**
> *Universidad Autónoma del Perú*

---

## 🎬 Demostración del Sistema

Descubre cómo la automatización y la inteligencia de datos optimizan la logística bancaria.

<a href="https://youtu.be/lzWgds9iSwg" target="_blank">
 <img src="https://img.youtube.com/vi/lzWgds9iSwg/maxresdefault.jpg" alt="Ver Demo del Sistema BANCOM" width="100%" style="border-radius: 10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);" />
</a>

---

## 📖 Sobre el Proyecto

Este **Sistema Web Inteligente** fue desarrollado para transformar digitalmente la gestión logística del **Banco de Comercio (BANCOM)**.

El proyecto aborda la problemática de la gestión manual y descentralizada (Excel), implementando una solución robusta que centraliza el inventario, automatiza los pedidos entre sedes y utiliza algoritmos matemáticos para mejorar la toma de decisiones.

### 🚀 Impacto y Resultados
* **Optimización de Procesos:** Reducción del tiempo de gestión de inventarios mediante carga masiva y validaciones automáticas.
* **Inteligencia de Negocios:** Implementación del algoritmo **MAPE** (Error Porcentual Absoluto Medio) para validar la precisión de las proyecciones de demanda.
* **Asistencia Virtual:** Integración de un **Chatbot** para consultas rápidas de stock y estado de pedidos.

---

## ✨ Módulos Principales

### 1. 📊 Dashboard Ejecutivo
Panel de control visual para la toma de decisiones estratégicas.
* **KPIs en Tiempo Real:** Total de activos, valorización, pedidos pendientes y cumplimiento de entregas (OTD).
* **Gráficos Interactivos:** Distribución de activos por sede y estado.

### 2. 📦 Gestión Logística Avanzada
* **Inventario Centralizado:** Carga masiva de activos tecnológicos mediante plantillas Excel.
* **Flujo de Pedidos:** Sistema de solicitud y aprobación de suministros diferenciado por sedes (Lima vs Provincia).
* **Alertas Inteligentes:** Notificaciones automáticas ante quiebres de stock.

### 3. 🤖 Módulo de Análisis & IA
* **Cálculo de Proyecciones:** Módulo estadístico que compara la demanda proyectada vs. real.
* **Asistente "Banci":** Chatbot integrado que responde en lenguaje natural consultas sobre la disponibilidad de equipos.

---

## 🛠️ Stack Tecnológico

El sistema sigue una arquitectura **MTV (Model-Template-View)** modular y escalable.

| Capa | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Lenguaje** | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | Lógica de negocio y procesamiento de datos. |
| **Framework** | ![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white) | Gestión de rutas, ORM, autenticación y seguridad. |
| **Frontend** | ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5&logoColor=white) ![Bootstrap](https://img.shields.io/badge/-Bootstrap-7952B3?logo=bootstrap&logoColor=white) | Interfaz responsiva y amigable para el usuario. |
| **Base de Datos** | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white) | Persistencia de datos (Entorno de Desarrollo). |
| **Librerías** | `NumPy`, `OpenPyXL` | Cálculos estadísticos y manipulación de archivos Excel. |

---

## 🔧 Instalación y Despliegue

Si deseas probar el código en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/jorgemendozapacheco-blip/sistema-logistico-inteligente-bancom.git](https://github.com/jorgemendozapacheco-blip/sistema-logistico-inteligente-bancom.git)
    cd sistema-logistico-inteligente-bancom
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install django numpy openpyxl
    ```

4.  **Configurar Base de Datos:**
    ```bash
    python manage.py migrate
    ```

5.  **Crear Administrador:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Ejecutar Servidor:**
    ```bash
    python manage.py runserver
    ```
    Visita: `http://127.0.0.1:8000/`

---

## 👥 Autores

* **Jorge Eduardo Mendoza Pacheco** - *Fullstack Developer & Cloud Architecture* - [GitHub](https://github.com/jorgemendozapacheco-blip) | [LinkedIn](https://www.linkedin.com/in/jorge-mendoza-pachecoo)
* **Fabricio Aguilar Quispe** - *Backend & Data Analyst*
* **Kevin Espinoza Cayhualla** - *Frontend & QA*

---
© 2025 - Propiedad Intelectual de los Autores y la Universidad Autónoma del Perú.
