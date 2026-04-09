from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SmartImportPurchaseEntryWizard(models.TransientModel):
    _name = "smart.import.purchase.entry.wizard"
    _description = "Registrar entrada asociada a compra"

    purchase_id = fields.Many2one(
        "purchase.order",
        string="Orden de compra",
        required=True,
        readonly=True,
    )

    purchase_line_id = fields.Many2one(
        "purchase.order.line",
        string="Línea de compra",
        required=True,
        domain="[('order_id', '=', purchase_id)]",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        compute="_compute_product_id",
        store=False,
        readonly=True,
    )

    quantity = fields.Float(
        string="Cantidad recibida",
        required=True,
    )

    location_destination_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación destino",
        required=True,
        domain="[('active', '=', True)]",
    )

    notes = fields.Text(string="Observaciones")

    @api.depends("purchase_line_id")
    def _compute_product_id(self):
        for wizard in self:
            wizard.product_id = wizard.purchase_line_id.product_id if wizard.purchase_line_id else False

    @api.onchange("purchase_line_id")
    def _onchange_purchase_line_id(self):
        if self.purchase_line_id:
            self.quantity = self.purchase_line_id.product_qty

    def action_register_entry(self):
        self.ensure_one()

        if self.quantity <= 0:
            raise ValidationError(_("La cantidad recibida debe ser mayor que 0."))

        if not self.location_destination_id:
            raise ValidationError(_("Debe seleccionar una ubicación de destino."))

        movement = self.env["smart.import.movement"].create({
            "product_id": self.purchase_line_id.product_id.id,
            "quantity": self.quantity,
            "movement_type": "in",
            "location_destination_id": self.location_destination_id.id,
            "purchase_id": self.purchase_id.id,
            "notes": self.notes or _("Entrada generada desde la orden de compra %s") % self.purchase_id.name,
        })

        movement.action_confirm()

        return {"type": "ir.actions.act_window_close"}