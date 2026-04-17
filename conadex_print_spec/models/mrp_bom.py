# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from math import floor

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    sheet_size_id = fields.Many2one(
        "conadex.print.sheet.size",
        string="Tamaño de pliego",
        help="Pliego de impresión usado en esta BOM.",
    )
    ups_computed = fields.Integer(
        string="Ups calculados",
        compute="_compute_ups",
        store=True,
        help="Piezas por pliego calculadas desde el tamaño de pliego y el formato abierto del producto.",
    )
    ups_override = fields.Integer(
        string="Ups manuales",
        help="Si se especifica, sobreescribe el valor calculado. Dejar en 0 para usar el calculado.",
    )
    ups_effective = fields.Integer(
        string="Ups efectivos",
        compute="_compute_ups_effective",
        store=True,
    )
    tiro_retiro = fields.Selection(
        [
            ("tiro_solo", "Tiro solo (1 cara)"),
            ("tiro_retiro", "Tiro y retiro (2 pasadas, placas distintas)"),
            ("tiro_propio_retiro", "Tiro propio retiro (2 pasadas, mismo set de placas)"),
        ],
        string="Tiro/Retiro",
        default="tiro_solo",
        required=True,
    )
    plate_count = fields.Integer(
        string="Placas requeridas",
        compute="_compute_plate_count",
        store=True,
    )
    requires_die_id = fields.Many2one(
        "maintenance.equipment",
        string="Suaje requerido",
        help="Suaje o troquel. Se valida su existencia al lanzar la orden de manufactura.",
    )
    setup_sheets = fields.Integer(
        string="Pliegos de arranque",
        default=250,
        help="Pliegos de afinación antes de corrida válida. QM52: 250, PM74: 400.",
    )

    @api.depends(
        "sheet_size_id.width_in",
        "sheet_size_id.height_in",
        "product_tmpl_id.open_format_w",
        "product_tmpl_id.open_format_h",
        "product_tmpl_id.has_bleed",
        "product_tmpl_id.bleed_mm",
    )
    def _compute_ups(self):
        for bom in self:
            tmpl = bom.product_tmpl_id
            sheet = bom.sheet_size_id
            if not sheet or not tmpl or not tmpl.open_format_w or not tmpl.open_format_h:
                bom.ups_computed = 0
                continue

            bleed_in = (tmpl.bleed_mm / 25.4) if tmpl.has_bleed else 0.0
            pw = tmpl.open_format_w + 2 * bleed_in
            ph = tmpl.open_format_h + 2 * bleed_in

            ups_std = floor(sheet.width_in / pw) * floor(sheet.height_in / ph)
            ups_rot = floor(sheet.width_in / ph) * floor(sheet.height_in / pw)
            bom.ups_computed = max(ups_std, ups_rot, 0)

    @api.depends("ups_computed", "ups_override")
    def _compute_ups_effective(self):
        for bom in self:
            bom.ups_effective = bom.ups_override if bom.ups_override > 0 else bom.ups_computed

    @api.depends(
        "product_tmpl_id.colors_front",
        "product_tmpl_id.colors_back",
        "tiro_retiro",
    )
    def _compute_plate_count(self):
        for bom in self:
            cf = bom.product_tmpl_id.colors_front or 0
            cb = bom.product_tmpl_id.colors_back or 0
            if bom.tiro_retiro == "tiro_solo":
                bom.plate_count = cf
            elif bom.tiro_retiro == "tiro_retiro":
                bom.plate_count = cf + cb
            else:  # tiro_propio_retiro
                bom.plate_count = max(cf, cb)
