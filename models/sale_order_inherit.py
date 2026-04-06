from odoo import models, fields, _
from odoo.exceptions import ValidationError

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    smart_import_location_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación logística",
        domain=[("active", "=", True)],
    )

    def action_confirm(self):
        movement_model = self.env["smart.import.movement"]

        for order in self:
            if not order.smart_import_location_id:
                raise ValidationError(_(
                    "Debe seleccionar una ubicación logística antes de confirmar la venta."
                ))

            for line in order.order_line:
                if not line.product_id:
                    continue

                if line.product_id.type not in ["product", "consu"]:
                    continue

                stock_available = movement_model._compute_stock(
                    line.product_id,
                    order.smart_import_location_id
                )

                if line.product_uom_qty > stock_available:
                    return {
                        "type": "ir.actions.act_window",
                        "name": _("Falta de stock"),
                        "res_model": "smart.import.stock.warning.wizard",
                        "view_mode": "form",
                        "target": "new",
                        "context": {
                            "default_product_id": line.product_id.id,
                            "default_quantity": line.product_uom_qty,
                            "default_location_id": order.smart_import_location_id.id,
                            "default_sale_order_id": order.id,
                            "default_available_quantity": stock_available,
                        },
                    }

        return super().action_confirm()