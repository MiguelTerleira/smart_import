# SmartImport

SmartImport es un módulo desarrollado para **Odoo 17 Community** orientado a mejorar la gestión logística en entornos con múltiples ubicaciones. Su finalidad es facilitar el control de entradas de mercancía, transferencias internas, salidas asociadas a ventas, consulta de stock distribuido y trazabilidad de productos dentro del propio ERP.

## Descripción

El módulo ha sido desarrollado como parte del Trabajo de Fin de Grado del ciclo formativo de **Desarrollo de Aplicaciones Multiplataforma (DAM)**. Su objetivo principal es contribuir a la digitalización de procesos logísticos mediante una solución integrada en Odoo, reutilizando modelos estándar del sistema y ampliando sus funcionalidades en el ámbito de compras, ventas y control de stock.

## Funcionalidades principales

- Gestión de ubicaciones logísticas.
- Registro de entradas de mercancía.
- Gestión de transferencias internas entre ubicaciones.
- Registro de salidas de mercancía asociadas a ventas.
- Consulta de stock por producto y por ubicación.
- Consulta de trazabilidad e histórico de movimientos.
- Solicitudes de transferencia por falta de stock.
- Integración con compras.
- Integración con ventas.
- Gestión de permisos por perfiles de usuario.

## Requisitos

Para ejecutar el módulo es necesario disponer de:

- Una instalación de **Odoo 17 Community**
- **PostgreSQL**
- Un entorno Python compatible con Odoo 17
- Acceso a la carpeta de addons personalizados de Odoo

## Instalación

1. Clonar o copiar el módulo en la carpeta de addons personalizados.
2. Añadir dicha ruta al archivo de configuración de Odoo si fuera necesario.
3. Reiniciar el servicio o la instancia de Odoo.
4. Actualizar la lista de aplicaciones desde el ERP.
5. Buscar e instalar el módulo **SmartImport**.

## Configuración inicial

Una vez instalado el módulo, es necesario revisar los permisos de usuario para que pueda visualizarse y utilizarse correctamente. Para ello, deben asignarse a cada usuario los grupos correspondientes dentro de SmartImport:

- **Administrador SmartImport**
- **Usuario logístico SmartImport**
- **Usuario de ventas SmartImport**

Si el usuario no tiene asignado alguno de estos grupos, el módulo no aparecerá en su interfaz o no podrá acceder a determinadas funcionalidades.

## Uso básico

Una vez instalado y configurado el módulo, el flujo básico de uso es el siguiente:

1. Crear las ubicaciones logísticas necesarias.
2. Registrar entradas de mercancía.
3. Consultar el stock disponible por producto o por ubicación.
4. Realizar transferencias internas cuando sea necesario.
5. Gestionar solicitudes de transferencia en situaciones de falta de stock.
6. Validar ventas teniendo en cuenta la ubicación logística seleccionada.

## Estructura del módulo


```md id="hans9j"
smart_import/
├── data/
│   └── sequence.xml                      (Secuencia de referencias de movimientos)
├── models/
│   ├── __init__.py                      (Carga de los modelos del módulo)
│   ├── logistic_location.py             (Modelo de ubicaciones logísticas)
│   ├── movement.py                      (Modelo de movimientos de mercancía)
│   ├── purchase_order_inherit.py        (Extensión del modelo de compras)
│   ├── sale_order_inherit.py            (Extensión del modelo de ventas)
│   ├── stock.py                         (Modelo de stock distribuido)
│   └── transfer_request.py              (Modelo de solicitudes de transferencia)
├── security/
│   ├── ir.model.access.csv              (Permisos de acceso a modelos)
│   └── security.xml                     (Grupos de usuario del módulo)
├── static/
│   └── description/
│       └── icon.png                     (Icono del módulo)
├── views/
│   ├── logistic_location_views.xml      (Vistas de ubicaciones logísticas)
│   ├── movement_views.xml               (Vistas de movimientos)
│   ├── purchase_order_inherit_views.xml (Vistas extendidas de compras)
│   ├── sale_order_inherit_views.xml     (Vistas extendidas de ventas)
│   ├── smart_import_menus.xml           (Menús del módulo)
│   ├── stock_views.xml                  (Vistas de stock)
│   └── transfer_request_views.xml       (Vistas de solicitudes de transferencia)
└── wizard/
    ├── __init__.py                      (Carga de asistentes)
    ├── purchase_entry_wizard.py         (Asistente de entrada desde compra)
    ├── purchase_entry_wizard_views.xml  (Vista del asistente de entrada)
    ├── stock_warning_wizard.py          (Asistente de falta de stock)

```

## Estado del proyecto

Proyecto desarrollado y validado como parte de un TFG, con integración funcional en Odoo 17 y pruebas realizadas tanto en entorno local como en entorno VPS.

## Autor

**Miguel Ángel Terleira**

