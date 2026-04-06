from odoo import models, fields, api, _


class StockWarningWizard(models.TransientModel):
    _name = "smart.import.stock.warning.wizard"
    _description = "Aviso de falta de stock"

    product_id = fields.Many2one("product.product", string="Producto", readonly=True)
    quantity = fields.Float(string="Cantidad solicitada", readonly=True)
    available_quantity = fields.Float(string="Cantidad disponible", readonly=True)

    location_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación sin stock",
        readonly=True,
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Pedido de venta",
        readonly=True,
    )

    logistic_user_id = fields.Many2one(
        "res.users",
        string="Usuario logístico",
        domain=lambda self: [
            ("groups_id", "in", self.env.ref("smart_import.group_smart_import_logistics").ids)
        ],
    )

    email_to = fields.Char(string="Correo de aviso")

    alternative_stock_info = fields.Html(
        string="Stock disponible en otras ubicaciones",
        compute="_compute_alternative_stock_info",
        readonly=True,
    )

    @api.depends("product_id", "location_id")
    def _compute_alternative_stock_info(self):
        movement_model = self.env["smart.import.movement"]
        location_model = self.env["smart.import.logistic.location"]

        for wizard in self:
            if not wizard.product_id:
                wizard.alternative_stock_info = _("<p>No hay información disponible.</p>")
                continue

            locations = location_model.search([
                ("active", "=", True),
                ("id", "!=", wizard.location_id.id),
            ])

            rows = []
            for location in locations:
                qty = movement_model._compute_stock(wizard.product_id, location)
                if qty > 0:
                    rows.append(
                        "<li><strong>%s</strong>: %s unidades</li>" % (
                            location.display_name_full or location.name,
                            qty,
                        )
                    )

            if rows:
                wizard.alternative_stock_info = (
                    "<p>Se ha detectado stock disponible en otras ubicaciones:</p><ul>%s</ul>"
                    % "".join(rows)
                )
            else:
                wizard.alternative_stock_info = _(
                    "<p>No existe stock disponible del producto en otras ubicaciones activas.</p>"
                )

    def action_create_transfer_request(self):
        self.ensure_one()

        request = self.env["smart.import.transfer.request"].create({
            "product_id": self.product_id.id,
            "quantity": self.quantity,
            "location_origin_id": self.location_id.id,
        })

        # mensaje interno en la solicitud
        request.message_post(
            body=_(
                "Se ha creado una solicitud de transferencia para el producto '%s' "
                "por falta de stock en la ubicación '%s'."
            ) % (
                self.product_id.display_name,
                self.location_id.display_name,
            )
        )

        # mensaje relacionado con el pedido de venta
        if self.sale_order_id:
            request.message_post(
                body=_(
                    "La solicitud está relacionada con el pedido de venta '%s'."
                ) % self.sale_order_id.name
            )


        # actividad para el usuari logístico
        if self.logistic_user_id:
            request.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.logistic_user_id.id,
                summary=_("Revisar solicitud de transferencia"),
                note=_(
                    "Revisar la solicitud de transferencia del producto '%s' "
                    "para cubrir la falta de stock en '%s'."
                ) % (
                    self.product_id.display_name,
                    self.location_id.display_name,
                ),
            )

        # mail opcional
        if self.email_to:
            mail_values = {
                "subject": _("Solicitud de transferencia de stock"),
                "body_html": _(
                    "<p>Se ha generado una solicitud de transferencia de stock.</p>"
                    "<ul>"
                    "<li><strong>Producto:</strong> %s</li>"
                    "<li><strong>Cantidad solicitada:</strong> %s</li>"
                    "<li><strong>Cantidad disponible:</strong> %s</li>"
                    "<li><strong>Ubicación sin stock:</strong> %s</li>"
                    "</ul>"
                    "<p>Acceda a SmartImport para revisar y procesar la solicitud.</p>"
                ) % (
                    self.product_id.display_name,
                    self.quantity,
                    self.available_quantity,
                    self.location_id.display_name,
                ),
                "email_to": self.email_to,
            }
            self.env["mail.mail"].create(mail_values).send()

        return {"type": "ir.actions.act_window_close"}