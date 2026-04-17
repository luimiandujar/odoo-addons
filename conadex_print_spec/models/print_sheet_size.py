# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import fields, models


class PrintSheetSize(models.Model):
    _name = "conadex.print.sheet.size"
    _description = "Tamaño de pliego de impresión"
    _order = "width_in, height_in"

    name = fields.Char(required=True)
    width_in = fields.Float(string="Ancho (in)", required=True, digits=(6, 3))
    height_in = fields.Float(string="Alto (in)", required=True, digits=(6, 3))
    compatible_machine_ids = fields.Many2many(
        "mrp.workcenter",
        "print_sheet_size_workcenter_rel",
        "sheet_size_id",
        "workcenter_id",
        string="Máquinas compatibles",
    )
    active = fields.Boolean(default=True)

    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.width_in} × {rec.height_in} in)") for rec in self]
