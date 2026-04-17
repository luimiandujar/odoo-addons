# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # ── Activador ──────────────────────────────────────────────────────────────
    is_print_product = fields.Boolean(
        string="Producto de imprenta",
        default=False,
        help="Activa los campos de spec de impresión y la pestaña Print Spec.",
    )

    # ── Clasificación ──────────────────────────────────────────────────────────
    print_type = fields.Selection(
        [
            ("commercial", "Comercial"),
            ("plegadiza", "Empaque plegadizo"),
            ("etiqueta", "Etiqueta"),
            ("continuo", "Formulario continuo"),
            ("gran_formato", "Gran formato"),
            ("libro", "Libro"),
            ("otro", "Otro"),
        ],
        string="Tipo de impresión",
    )

    # ── Formatos ───────────────────────────────────────────────────────────────
    closed_format_w = fields.Float(
        string="Ancho cerrado (in)", digits=(6, 3),
        help="Formato final después de corte/troquelado.",
    )
    closed_format_h = fields.Float(string="Alto cerrado (in)", digits=(6, 3))
    open_format_w = fields.Float(
        string="Ancho abierto (in)", digits=(6, 3),
        help="Antes de pliegue. Para productos no plegables = igual al cerrado.",
    )
    open_format_h = fields.Float(string="Alto abierto (in)", digits=(6, 3))

    # ── Colores y páginas ──────────────────────────────────────────────────────
    page_count = fields.Integer(string="Número de páginas", default=1)
    colors_front = fields.Integer(string="Colores anverso", default=4)
    colors_back = fields.Integer(string="Colores reverso", default=0)

    # ── Sangre ─────────────────────────────────────────────────────────────────
    has_bleed = fields.Boolean(string="Tiene sangre", default=True)
    bleed_mm = fields.Float(string="Sangre (mm)", default=3.0, digits=(6, 2))

    # ── Papel ──────────────────────────────────────────────────────────────────
    default_paper_id = fields.Many2one(
        "product.product",
        string="Papel por defecto",
        domain=[("type", "in", ["product", "consu"])],
    )
    default_paper_weight_g = fields.Float(
        string="Gramaje por defecto (g/m²)", digits=(6, 1)
    )
    grain_direction = fields.Selection(
        [("long_grain", "Grano largo"), ("short_grain", "Grano corto"), ("any", "Indiferente")],
        string="Dirección de fibra",
        default="any",
    )

    # ── Imposición y merma ─────────────────────────────────────────────────────
    standard_ups = fields.Integer(
        string="Imposición estándar (ups)",
        help="Piezas por pliego. Calculada o definida manualmente.",
    )
    standard_waste_pct = fields.Float(
        string="Merma estándar (%)",
        digits=(5, 4),
        default=0.08,
        help="Porcentaje sobre corrida neta. Ej: 0.08 = 8%.",
    )

    # ── Acabados ───────────────────────────────────────────────────────────────
    finishing_line_ids = fields.One2many(
        "conadex.print.finishing.line",
        "product_tmpl_id",
        string="Acabados",
    )

    # ── Referencias ────────────────────────────────────────────────────────────
    artwork_location = fields.Char(
        string="Ubicación del arte",
        help="URL o ruta Google Drive del arte aprobado.",
    )
    customer_code = fields.Char(
        string="Código cliente",
        help="Código del producto según el cliente. Aparece en Job Ticket y facturas.",
    )

    @api.constrains("colors_front", "colors_back")
    def _check_colors(self):
        for rec in self:
            if rec.is_print_product:
                if not (0 <= rec.colors_front <= 8):
                    raise ValidationError(f"'{rec.name}': colores anverso debe estar entre 0 y 8.")
                if not (0 <= rec.colors_back <= 8):
                    raise ValidationError(f"'{rec.name}': colores reverso debe estar entre 0 y 8.")

    @api.constrains("standard_waste_pct")
    def _check_waste_pct(self):
        for rec in self:
            if rec.is_print_product and not (0 <= rec.standard_waste_pct <= 1):
                raise ValidationError(
                    f"'{rec.name}': merma estándar debe ser un valor entre 0 y 1 (ej: 0.08 para 8%)."
                )
