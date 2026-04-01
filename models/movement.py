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

    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("done", "Confirmado"),
        ],
        string="Estado",
        default="draft",
    )

    notes = fields.Text(string="Observaciones")



 
    #restricciones para validar los datos antes de guardar el movimiento

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_("La cantidad debe ser mayor que 0."))

    @api.constrains("movement_type", "location_origin_id", "location_destination_id")
    def _check_locations(self):
        for rec in self:
            if rec.movement_type == "in":
                if not rec.location_destination_id:
                    raise ValidationError(_("En un movimiento de entrada es obligatorio indicar la ubicación de destino."))
            elif rec.movement_type == "out":
                if not rec.location_origin_id:
                    raise ValidationError(_("En un movimiento de salida es obligatorio indicar la ubicación de origen."))
            elif rec.movement_type == "transfer":
                if not rec.location_origin_id or not rec.location_destination_id:
                    raise ValidationError(_("En una transferencia es obligatorio indicar ubicación de origen y destino."))
                if rec.location_origin_id == rec.location_destination_id:
                    raise ValidationError(_("La ubicación origen y destino no pueden ser la misma."))

    
    #logica para generar la referencia del movimiento al crear un nuevo registro (vinculado con archivo sequence.xml)
    @api.model
    def create(self, vals):
        if vals.get("name", "Nuevo") == "Nuevo":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "smart.import.movement"
            ) or "MOV/0000"

        movement_type = vals.get("movement_type")

        if movement_type == "in":
            vals["location_origin_id"] = False
        elif movement_type == "out":
            vals["location_destination_id"] = False

        # Validación de stock para salidas y transferencias
        if movement_type in ["out", "transfer"]:
            product = self.env["product.product"].browse(vals.get("product_id"))
            origin = self.env["smart.import.logistic.location"].browse(vals.get("location_origin_id"))

            stock = self._compute_stock(product, origin)

           # if vals.get("quantity", 0) > stock:
            #    raise ValidationError(_("No hay stock suficiente en la ubicación de origen."))
        
        # creacion automatica de stock al registrar movimientos
        if movement_type == "in":
            self._create_stock_if_not_exists(vals.get("product_id"), vals.get("location_destination_id"))

        elif movement_type == "out":
            self._create_stock_if_not_exists(vals.get("product_id"), vals.get("location_origin_id"))

        elif movement_type == "transfer":
            self._create_stock_if_not_exists(vals.get("product_id"), vals.get("location_origin_id"))
            self._create_stock_if_not_exists(vals.get("product_id"), vals.get("location_destination_id"))

        return super().create(vals)
    

    #logica para validar salidas y transferencias
    def action_confirm(self):
        self.ensure_one()

        # validar para salidas y transferencias
        if self.movement_type in ["out", "transfer"]:

            stock = self._compute_stock(self.product_id, self.location_origin_id)

            if self.quantity > stock:
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Stock insuficiente"),
                    "res_model": "smart.import.stock.warning.wizard",
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                        "default_product_id": self.product_id.id,
                        "default_quantity": self.quantity,
                        "default_location_id": self.location_origin_id.id,
                    }
                }

        # confirmar si todo es correcto
        self.state = "done"

    
    #logica para calcular el stock en funcion del movimiento registrado
    def _compute_stock(self, product, location):
        if not product or not location:
            return 0.0

        movements = self.search([
            ("product_id", "=", product.id),
            ("state", "=", "done"),
            "|",
            ("location_origin_id", "=", location.id),
            ("location_destination_id", "=", location.id),
        ])

        stock = 0.0

        for move in movements:
            if move.movement_type == "in":
                if move.location_destination_id and move.location_destination_id.id == location.id:
                    stock += move.quantity

            elif move.movement_type == "out":
                if move.location_origin_id and move.location_origin_id.id == location.id:
                    stock -= move.quantity

            elif move.movement_type == "transfer":
                if move.location_origin_id and move.location_origin_id.id == location.id:
                    stock -= move.quantity
                if move.location_destination_id and move.location_destination_id.id == location.id:
                    stock += move.quantity

        return stock

    #logica para autocreacion de stock al registrar movimientos
    def _create_stock_if_not_exists(self, product_id, location_id):
        if not product_id or not location_id:
            return

        stock = self.env["smart.import.stock"].search([
            ("product_id", "=", product_id),
            ("location_id", "=", location_id)
        ], limit=1)

        if not stock:
            self.env["smart.import.stock"].create({
                "product_id": product_id,
                "location_id": location_id,
            })

    #logica para abrir el asistente de solicitud de transferencia desde un movimiento de salida
    def action_open_stock_warning_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Solicitar transferencia"),
            "res_model": "smart.import.stock.warning.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_product_id": self.product_id.id,
                "default_quantity": self.quantity,
                "default_location_id": self.location_origin_id.id,
            },
        }