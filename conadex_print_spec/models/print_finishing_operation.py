# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PrintFinishingOperation(models.Model):
    _name = "conadex.print.finishing.operation"
    _description = "Operación de acabado (catálogo maestro)"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(
        required=True,
        help="Código corto único: BARN_UV, LAM_MATE, LAM_BRILLO, UV_SEL, TROQ, FOIL, PEGADO",
    )
    sequence = fields.Integer(default=10)
    workcenter_id = fields.Many2one(
        "mrp.workcenter",
        string="Work Center",
        # El post_init_hook asigna el work center por código en la instalación.
        # required=True se aplica a nivel de vista, no de modelo, para permitir seed data limpio.
    )
    setup_minutes = fields.Float(string="Minutos de setup", required=True)
    setup_cost = fields.Float(
        string="Costo fijo de setup (USD)",
        digits=(12, 2),
        help="Materiales de arranque, pruebas, etc.",
    )
    run_unit = fields.Selection(
        [
            ("sheets", "Pliegos"),
            ("m2", "Metros cuadrados"),
            ("m_linear", "Metros lineales"),
            ("units", "Unidades"),
        ],
        string="Unidad de corrida",
        required=True,
        default="sheets",
    )
    run_rate = fields.Float(
        string="Velocidad de corrida (unidades/hora)",
        required=True,
        help="Ej: 3000 pliegos/hora para barniz UV",
    )
    cost_per_hour = fields.Float(
        string="Costo por hora (USD)",
        digits=(12, 2),
        required=True,
    )
    consumable_line_ids = fields.One2many(
        "conadex.print.finishing.consumable.line",
        "operation_id",
        string="Consumibles",
    )
    notes = fields.Text(string="Observaciones técnicas para el operario")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "El código de operación de acabado debe ser único."),
    ]

    @api.constrains("run_rate")
    def _check_run_rate(self):
        for rec in self:
            if rec.run_rate <= 0:
                raise ValidationError(f"La velocidad de corrida de '{rec.name}' debe ser mayor a cero.")


class PrintFinishingConsumableLine(models.Model):
    _name = "conadex.print.finishing.consumable.line"
    _description = "Consumible de una operación de acabado"

    operation_id = fields.Many2one(
        "conadex.print.finishing.operation",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Consumible",
        required=True,
        domain=[("type", "in", ["product", "consu"])],
    )
    consumption_basis = fields.Selection(
        [
            ("per_setup", "Por setup"),
            ("per_sheet", "Por pliego"),
            ("per_m2", "Por m²"),
            ("per_unit", "Por unidad"),
            ("per_hour", "Por hora"),
        ],
        string="Base de consumo",
        required=True,
        default="per_sheet",
    )
    quantity = fields.Float(
        string="Cantidad",
        required=True,
        digits=(12, 6),
        help="Cantidad consumida en la base elegida. Ej: 0.002 kg por pliego.",
    )
    uom_id = fields.Many2one(
        related="product_id.uom_id",
        string="UdM",
        readonly=True,
    )
