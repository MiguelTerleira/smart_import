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
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",

        "views/logistic_location_views.xml",
        "views/movement_views.xml",
        "views/stock_views.xml",
        "views/transfer_request_views.xml",
        "views/sale_order_inherit_views.xml",
        "views/purchase_order_inherit_views.xml",
        "views/smart_import_menus.xml",
        

        "wizard/stock_warning_wizard_views.xml",
        "wizard/purchase_entry_wizard_views.xml",
        
    ],
    "application": True,
    "installable": True,
}