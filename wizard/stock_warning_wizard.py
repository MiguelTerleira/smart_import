from odoo import models, fields, _


class StockWarningWizard(models.TransientModel):
    _name = "smart.import.stock.warning.wizard"
    _description = "Aviso de falta de stock"

    product_id = fields.Many2one("product.product", string="Producto")
    quantity = fields.Float(string="Cantidad")
    location_id = fields.Many2one(
        "smart.import.logistic.location",
        string="Ubicación sin stock",
    )

    logistic_user_id = fields.Many2one(
        "res.users",
        string="Usuario logístico",
        domain=lambda self: [
        ("groups_id", "in", self.env.ref("smart_import.group_smart_import_logistics").ids)
        ],
    )

    email_to = fields.Char(string="Correo de aviso")

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
                    "<li><strong>Cantidad:</strong> %s</li>"
                    "<li><strong>Ubicación sin stock:</strong> %s</li>"
                    "</ul>"
                    "<p>Acceda a SmartImport para revisar y procesar la solicitud.</p>"
                ) % (
                    self.product_id.display_name,
                    self.quantity,
                    self.location_id.display_name,
                ),
                "email_to": self.email_to,
            }
            self.env["mail.mail"].create(mail_values).send()

        return {"type": "ir.actions.act_window_close"}