{
    "name": "SmartImport",
    "version": "17.0.1.0.0",
    "summary": "Gestión inteligente de importaciones y stock distribuido",
    "description": """
Módulo para la gestión de ubicaciones logísticas, movimientos de mercancía,
stock distribuido y trazabilidad en Odoo.
    """,
    "author": "Miguel Ángel Terleira Cortés",
    "website": "",
    "category": "Inventory/Inventory",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
        "stock",
        "purchase",
        "sale_management",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/logistic_location_views.xml",
        "views/smart_import_menus.xml",
        
    ],
    "application": True,
    "installable": True,
}