from odoo import api, fields, models


class SmartImportStock(models.Model):
    _name = "smart.import.stock"
    _description = "Stock por ubicación"

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