# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

from odoo import fields, models


class PrintFinishingLine(models.Model):
    """Línea de acabado específica de un producto (instancia del catálogo maestro)."""

    _name = "conadex.print.finishing.line"
    _description = "Acabado asignado a un producto"
    _order = "sequence, id"

    product_tmpl_id = fields.Many2one(
        "product.template",
        required=True,
        ondelete="cascade",
    )
    operation_id = fields.Many2one(
        "conadex.print.finishing.operation",
        string="Operación",
        required=True,
    )
    sequence = fields.Integer(default=10, help="Orden de ejecución del acabado.")
    notes = fields.Char(string="Notas específicas del producto")

    # campos de solo lectura del catálogo para referencia rápida
    workcenter_id = fields.Many2one(
        related="operation_id.workcenter_id",
        string="Work Center",
        readonly=True,
    )
    run_unit = fields.Selection(
        related="operation_id.run_unit",
        string="Unidad corrida",
        readonly=True,
    )
