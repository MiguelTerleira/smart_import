from odoo import api, fields, models


class SmartImportStock(models.Model):
    _name = "smart.import.stock"
    _description = "Stock por ubicación"
    _rec_name = "product_id"


    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        required=True,
    )

    location_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación",
        required=True,
    )

    quantity = fields.Float(
        string="Stock",
        compute="_compute_quantity",
        store=False,
    )

    @api.depends("product_id", "location_id")
    def _compute_quantity(self):
        movement_model = self.env["smart.import.movement"]

        for rec in self:
            if rec.product_id and rec.location_id:
                rec.quantity = movement_model._compute_stock(
                    rec.product_id,
                    rec.location_id
                )
            else:
                rec.quantity = 0

    # Acción para ver la trazabilidad del producto
    def action_view_product_traceability(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Trazabilidad del producto",
            "res_model": "smart.import.movement",
            "view_mode": "tree,form",
            "domain": [("product_id", "=", self.product_id.id)],
            "context": {
                "search_default_group_date": 0,
                "default_product_id": self.product_id.id,
            },
        }