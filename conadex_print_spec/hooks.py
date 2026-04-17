# Copyright 2026 Luis Miguel Andújar
# Todos los derechos reservados.
# Prohibida su distribución, modificación o uso sin autorización expresa del autor.

"""
post_init_hook para conadex_print_spec.

Tareas que se ejecutan DESPUÉS de que los archivos de datos XML se cargan:
  1. Crear external IDs (ir.model.data) para los work centers existentes en Conadex,
     usando sus códigos como clave estable.
  2. Poblar los campos de capacidad de las prensas (is_press, velocidades, pliegos).
  3. Enlazar el catálogo de acabados con los work centers por código.
  4. Vincular los tamaños de pliego con las máquinas compatibles.
"""

import logging

_logger = logging.getLogger(__name__)

MODULE = "conadex_print_spec"

# Mapeo código de work center → external ID a asignar
WC_XIDS = {
    "HEI-PM74":    "wc_pm74",
    "HEI-QM52-1":  "wc_qm52_1",
    "HEI-QM52-2":  "wc_qm52_2",
    "ATF-UV126":   "wc_barniz_uv",
    "LAM-950":     "wc_laminadora",
    "TROQ-THOM":   "wc_troqueladora",
    "DEPAI-750":   "wc_depai_foil",
    "FORMA-WY500": "wc_formadora",
    "GUI-POL50":   "wc_guillotina",
}

# Capacidades de las prensas de impresión
PRESS_CAPACITY = {
    "HEI-PM74": {
        "is_press": True,
        "press_type": "offset",
        "max_sheet_w_in": 20.5,
        "max_sheet_h_in": 29.0,
        "max_colors_per_pass": 4,
        "makeready_sheets": 400,
        "run_speed_sph": 7500,
    },
    "HEI-QM52-1": {
        "is_press": True,
        "press_type": "offset",
        "max_sheet_w_in": 14.0,
        "max_sheet_h_in": 20.0,
        "max_colors_per_pass": 2,
        "makeready_sheets": 250,
        "run_speed_sph": 10000,
    },
    "HEI-QM52-2": {
        "is_press": True,
        "press_type": "offset",
        "max_sheet_w_in": 14.0,
        "max_sheet_h_in": 20.0,
        "max_colors_per_pass": 2,
        "makeready_sheets": 250,
        "run_speed_sph": 10000,
    },
}

# Acabado (code) → código del work center que lo ejecuta
FINISHING_WC = {
    "BARN_UV":    "ATF-UV126",
    "LAM_MATE":   "LAM-950",
    "LAM_BRILLO": "LAM-950",
    "UV_SEL":     "ATF-UV126",
    "TROQ":       "TROQ-THOM",
    "FOIL":       "DEPAI-750",
    "PEGADO":     "FORMA-WY500",
}

# Tamaño de pliego (name) → lista de códigos de work centers compatibles
SHEET_SIZE_MACHINES = {
    "10 × 14":   ["HEI-QM52-1", "HEI-QM52-2"],
    "12 × 18":   ["HEI-QM52-1", "HEI-QM52-2"],
    "13 × 19":   ["HEI-QM52-1", "HEI-QM52-2"],
    "14 × 20":   ["HEI-QM52-1", "HEI-QM52-2"],
    "16 × 22":   ["HEI-PM74"],
    "18 × 25":   ["HEI-PM74"],
    "20 × 28":   ["HEI-PM74"],
    "20.5 × 29": ["HEI-PM74"],
}


def post_init_hook(env):
    _assign_workcenter_xids(env)
    _set_press_capacity(env)
    _link_finishing_workcenters(env)
    _link_sheet_size_machines(env)


def _assign_workcenter_xids(env):
    """Crea external IDs para los work centers existentes usando su código."""
    IrModelData = env["ir.model.data"]
    Workcenter = env["mrp.workcenter"]

    for wc_code, xml_name in WC_XIDS.items():
        wc = Workcenter.search([("code", "=", wc_code)], limit=1)
        if not wc:
            _logger.warning("post_init_hook: work center con código '%s' no encontrado.", wc_code)
            continue

        existing = IrModelData.search(
            [("module", "=", MODULE), ("name", "=", xml_name)], limit=1
        )
        if existing:
            continue  # ya existe el external ID, no tocar

        IrModelData.create({
            "name": xml_name,
            "module": MODULE,
            "model": "mrp.workcenter",
            "res_id": wc.id,
            "noupdate": True,
        })
        _logger.info("post_init_hook: external ID '%s.%s' → id=%d (%s)", MODULE, xml_name, wc.id, wc_code)


def _set_press_capacity(env):
    """Pobla los campos de capacidad en las prensas de impresión."""
    Workcenter = env["mrp.workcenter"]
    for wc_code, vals in PRESS_CAPACITY.items():
        wc = Workcenter.search([("code", "=", wc_code)], limit=1)
        if wc:
            wc.write(vals)
            _logger.info("post_init_hook: capacidad actualizada para %s", wc_code)


def _link_finishing_workcenters(env):
    """Asigna el work center correcto a cada operación del catálogo de acabados."""
    Finishing = env["conadex.print.finishing.operation"]
    Workcenter = env["mrp.workcenter"]

    for finish_code, wc_code in FINISHING_WC.items():
        op = Finishing.search([("code", "=", finish_code)], limit=1)
        wc = Workcenter.search([("code", "=", wc_code)], limit=1)
        if op and wc:
            op.workcenter_id = wc
            _logger.info("post_init_hook: %s → %s (%s)", finish_code, wc_code, wc.name)
        elif not op:
            _logger.warning("post_init_hook: operación '%s' no encontrada en catálogo.", finish_code)
        elif not wc:
            _logger.warning("post_init_hook: work center '%s' no encontrado.", wc_code)


def _link_sheet_size_machines(env):
    """Vincula los tamaños de pliego con las máquinas compatibles."""
    SheetSize = env["conadex.print.sheet.size"]
    Workcenter = env["mrp.workcenter"]

    for size_name, wc_codes in SHEET_SIZE_MACHINES.items():
        size = SheetSize.search([("name", "=", size_name)], limit=1)
        if not size:
            _logger.warning("post_init_hook: tamaño de pliego '%s' no encontrado.", size_name)
            continue

        wcs = Workcenter.search([("code", "in", wc_codes)])
        if wcs:
            size.compatible_machine_ids = wcs
            _logger.info("post_init_hook: pliego '%s' vinculado a %s", size_name, wc_codes)
