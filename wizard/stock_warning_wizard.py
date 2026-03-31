from odoo import models, fields


class StockWarningWizard(models.TransientModel):
    _name = "smart.import.stock.warning.wizard"
    _description = "Aviso de falta de stock"

    product_id = fields.Many2one("product.product")
    quantity = fields.Float()
    location_id = fields.Many2one("smart.import.logistic.location")

    def action_request_transfer(self):
        self.env["smart.import.transfer.request"].create({
            "product_id": self.product_id.id,
            "quantity": self.quantity,
            "location_destination_id": self.location_id.id,
        })

    def action_create_transfer_request(self):
        self.ensure_one()

        self.env["smart.import.transfer.request"].create({
            "product_id": self.product_id.id,
            "quantity": self.quantity,
            "location_origin_id": self.location_id.id,
            "location_destination_id": self.location_id.id,  # temporal para que no falle
        })

        return {"type": "ir.actions.act_window_close"}    