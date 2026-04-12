from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SmartImportTransferRequest(models.Model):
    _name = "smart.import.transfer.request"
    _description = "Solicitud de transferencia"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "product_id"

    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        required=True,
        tracking=True,
    )

    quantity = fields.Float(
        string="Cantidad",
        required=True,
        tracking=True,
    )

    location_origin_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación origen",
        tracking=True,
    )

    location_destination_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación destino",
        tracking=True,
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Pedido de venta",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("pending", "Pendiente"),
            ("done", "Completado"),
        ],
        string="Estado",
        default="pending",
        tracking=True,
    )

    def action_execute_transfer(self):
        self.ensure_one()

        if not self.location_origin_id:
            raise ValidationError("Debe seleccionar una ubicación de origen.")

        if not self.location_destination_id:
            raise ValidationError("Debe existir una ubicación de destino.")

        stock = self.env["smart.import.movement"]._compute_stock(
            self.product_id,
            self.location_origin_id
        )

        if self.quantity > stock:
            raise ValidationError("No hay stock suficiente en la ubicación de origen seleccionada.")

        movement = self.env["smart.import.movement"].create({
            "product_id": self.product_id.id,
            "quantity": self.quantity,
            "movement_type": "transfer",
            "location_origin_id": self.location_origin_id.id,
            "location_destination_id": self.location_destination_id.id,
        })

        movement.action_confirm()
        self.state = "done"