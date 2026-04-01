from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SmartImportLogisticLocation(models.Model):
    _name = "smart.import.logistic.location"
    _description = "Ubicación logística"
    _order = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    code = fields.Char(
        string="Código",
        required=True,
        copy=False,
    )

    location_type = fields.Selection(
        selection=[
            ("port", "Puerto"),
            ("warehouse", "Almacén"),
            ("store", "Punto de venta"),
        ],
        string="Tipo de ubicación",
        required=True,
        default="warehouse",
    )

    stock_ids = fields.One2many(
        "smart.import.stock",
        "location_id",
        string="Stock en ubicación",
    )

    street = fields.Char(string="Dirección")
    city = fields.Char(string="Ciudad")
    zip = fields.Char(string="Código postal")
    state_id = fields.Many2one("res.country.state", string="Provincia")
    country_id = fields.Many2one("res.country", string="País")
    description = fields.Text(string="Descripción")
    active = fields.Boolean(string="Activa", default=True)

    display_name_full = fields.Char(
        string="Nombre completo",
        compute="_compute_display_name_full",
        store=False,
    )

    _sql_constraints = [
        (
            "unique_code",
            "unique(code)",
            "El código de la ubicación debe ser único.",
        ),
    ]

    @api.depends("name", "location_type")
    def _compute_display_name_full(self):
        type_labels = {
            "port": "Puerto",
            "warehouse": "Almacén",
            "store": "Punto de venta",
        }
        for record in self:
            label = type_labels.get(record.location_type, "")
            if label:
                record.display_name_full = f"{record.name} ({label})"
            else:
                record.display_name_full = record.name or ""

    @api.constrains("code")
    def _check_code_not_empty(self):
        for record in self:
            if record.code and not record.code.strip():
                raise ValidationError(_("El código de la ubicación no puede estar vacío."))

    @api.constrains("name")
    def _check_name_not_empty(self):
        for record in self:
            if record.name and not record.name.strip():
                raise ValidationError(_("El nombre de la ubicación no puede estar vacío."))

    def unlink(self):
        movement_model = self.env["smart.import.movement"]
        stock_model = self.env["smart.import.stock"]

        for record in self:
            movements_count = movement_model.search_count([
                "|",
                ("location_origin_id", "=", record.id),
                ("location_destination_id", "=", record.id),
            ])

            stock_records = stock_model.search([
                ("location_id", "=", record.id),
            ])

            stock_with_quantity = stock_records.filtered(lambda s: s.quantity > 0)

            if movements_count > 0 or stock_with_quantity:
                raise ValidationError(_(
                    "No se puede eliminar la ubicación '%s' porque tiene movimientos "
                    "de mercancía o stock asociado. Puede desactivarla en lugar de eliminarla."
                ) % record.name)

        return super().unlink()