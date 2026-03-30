from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SmartImportMovement(models.Model):
    _name = "smart.import.movement"
    _description = "Movimiento de mercancía"
    _order = "date desc"

    name = fields.Char(
        string="Referencia",
        required=True,
        copy=False,
        default="Nuevo",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        required=True,
    )

    quantity = fields.Float(
        string="Cantidad",
        required=True,
    )

    movement_type = fields.Selection(
        [
            ("in", "Entrada"),
            ("transfer", "Transferencia"),
            ("out", "Salida"),
        ],
        string="Tipo de movimiento",
        required=True,
    )

    location_origin_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación origen",
    )

    location_destination_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación destino",
    )

    date = fields.Datetime(
        string="Fecha",
        default=fields.Datetime.now,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Usuario",
        default=lambda self: self.env.user,
    )

    purchase_id = fields.Many2one(
        "purchase.order",
        string="Orden de compra",
    )

    sale_id = fields.Many2one(
        "sale.order",
        string="Orden de venta",
    )

    notes = fields.Text(string="Observaciones")

 
    #restricciones para validar los datos antes de guardar el movimiento

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_("La cantidad debe ser mayor que 0."))

    @api.constrains("location_origin_id", "location_destination_id")
    def _check_locations(self):
        for rec in self:
            if rec.movement_type == "transfer":
                if rec.location_origin_id == rec.location_destination_id:
                    raise ValidationError(
                        _("La ubicación origen y destino no pueden ser la misma.")
                    )

    
    #logica para generar la referencia del movimiento al crear un nuevo registro (vinculado con archivo sequence.xml)
    @api.model
    def create(self, vals):
        if vals.get("name", "Nuevo") == "Nuevo":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "smart.import.movement"
            ) or "MOV/0000"

        return super().create(vals)