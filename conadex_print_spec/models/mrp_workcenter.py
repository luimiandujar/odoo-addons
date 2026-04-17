# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    max_sheet_w_in = fields.Float(
        string="Pliego máx. ancho (in)",
        digits=(6, 3),
        help="Ancho máximo del pliego que acepta esta máquina.",
    )
    max_sheet_h_in = fields.Float(
        string="Pliego máx. alto (in)",
        digits=(6, 3),
    )
    max_colors_per_pass = fields.Integer(
        string="Colores máx. por pasada",
        help="QM52 = 2; PM74 = 4 (o 5 con unidad adicional).",
    )
    makeready_sheets = fields.Integer(
        string="Pliegos de arranque por defecto",
        help="Pliegos de afinación antes de corrida válida. Sobreescribible por BOM.",
    )
    run_speed_sph = fields.Integer(
        string="Velocidad de corrida (pliegos/hora)",
        help="Sheets per hour en condiciones normales de operación.",
    )
    is_press = fields.Boolean(
        string="Es prensa de impresión",
        default=False,
        help="Marca las máquinas de prensa para que el motor de estimación las considere en la selección.",
    )
