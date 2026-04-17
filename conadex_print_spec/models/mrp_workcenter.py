# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    is_press = fields.Boolean(
        string="Es prensa de impresión",
        default=False,
        help="Marca las máquinas de prensa para que el motor de estimación las considere en la selección.",
    )
    press_type = fields.Selection(
        [("offset", "Offset"), ("digital", "Digital"), ("gran_formato", "Gran formato")],
        string="Tipo de prensa",
        help="Determina el modelo de costo que usa el motor: offset = placas + tiempo; digital = costo por click.",
    )
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
        help="Velocidad por defecto para offset. Para digital, usar la tabla de velocidades por pliego.",
    )
    cost_per_click = fields.Float(
        string="Costo por click (USD)",
        digits=(12, 4),
        help="Solo para prensas digitales. Un click = una cara impresa.",
    )
    speed_line_ids = fields.One2many(
        "conadex.press.speed.line",
        "workcenter_id",
        string="Velocidades por tamaño de pliego",
        help="Para prensas digitales con velocidad variable según formato.",
    )
