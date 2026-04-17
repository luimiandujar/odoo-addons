# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import api, fields, models


class PrintPressSpeedLine(models.Model):
    _name = "conadex.press.speed.line"
    _description = "Velocidad de prensa por tamaño de pliego"
    _order = "workcenter_id, sheet_size_id"

    workcenter_id = fields.Many2one(
        "mrp.workcenter",
        string="Máquina",
        required=True,
        ondelete="cascade",
    )
    sheet_size_id = fields.Many2one(
        "conadex.print.sheet.size",
        string="Tamaño de pliego",
        required=True,
    )
    speed_value = fields.Integer(
        string="Velocidad",
        required=True,
        help="Velocidad de corrida en la unidad seleccionada.",
    )
    speed_unit = fields.Selection(
        [("sph", "Pliegos/hora (sph)"), ("ppm", "Páginas/minuto (ppm)")],
        string="Unidad",
        required=True,
        default="sph",
    )
    speed_sph = fields.Integer(
        string="Velocidad (sph)",
        compute="_compute_speed_sph",
        store=True,
        help="Velocidad normalizada a pliegos/hora. Usada por el motor de estimación.",
    )

    @api.depends("speed_value", "speed_unit")
    def _compute_speed_sph(self):
        for rec in self:
            if rec.speed_unit == "ppm":
                rec.speed_sph = rec.speed_value * 60
            else:
                rec.speed_sph = rec.speed_value
