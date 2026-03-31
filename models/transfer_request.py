from odoo import models, fields


class SmartImportTransferRequest(models.Model):
    _name = "smart.import.transfer.request"
    _description = "Solicitud de transferencia"

    product_id = fields.Many2one("product.product", string="Producto", required=True)

    quantity = fields.Float(string="Cantidad", required=True)

    location_origin_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación origen",
    )

    location_destination_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación destino",
        required=True,
    )

    state = fields.Selection([
        ("pending", "Pendiente"),
        ("done", "Completado"),
    ], default="pending")

    def action_execute_transfer(self):
        self.env["smart.import.movement"].create({
            "product_id": self.product_id.id,
            "quantity": self.quantity,
            "movement_type": "transfer",
            "location_origin_id": self.location_origin_id.id,
            "location_destination_id": self.location_destination_id.id,
        })

        self.state = "done"