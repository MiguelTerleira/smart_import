from odoo import models, _


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    def action_open_smart_import_entry_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Registrar entrada SmartImport"),
            "res_model": "smart.import.purchase.entry.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_purchase_id": self.id,
            },
        }