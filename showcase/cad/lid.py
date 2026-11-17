# showcase/cad/lid.py
from typing import cast

from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Location,
    Part,
    chamfer,
    fillet,
)

NECK_RADIUS = 37.0       # Matches NECK_RADIUS in body.py (74.0 mm diameter)
LID_Z_START = 218.0      # Mates flush with BODY_Z_END in body.py
COLLAR_TOP_Z = 244.0     # Upper rim of main lid collar
GALLERY_TOP_Z = 255.0    # Underside of overhanging SAP top cap
CAP_TOP_Z = 261.0        # Top surface of SAP cap housing
SEPTUM_X = -1.8          # Matches asymmetric 350 ml Hot / 400 ml Cold split


def _finalize_part(shape: object, label: str) -> Part:
    """Narrow build123d boolean/fillet union return types to Part and attach node label."""
    part = cast(Part, shape)
    part.label = label
    return part


def build_lid_silicone_gasket() -> Part:
    """Food-grade RTV-2 silicone perimeter ring and dual-chamber septum seal."""
    ring_outer = Location((0, 0, 216.0)) * Cylinder(
        radius=NECK_RADIUS - 1.6,
        height=7.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    ring_inner = Location((0, 0, 215.5)) * Cylinder(
        radius=NECK_RADIUS - 4.2,
        height=8.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    gasket = ring_outer - ring_inner

    septum_seal = Location((SEPTUM_X, 0, 215.8)) * Box(
        6.4, 68.0, 5.2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    return _finalize_part(gasket + septum_seal, "lid_silicone_gasket")


def build_flow_separators() -> Part:
    """BPA-free PP/PETG internal flow baffle and dual isolated drinking risers."""
    deck = Location((0, 0, 222.0)) * Cylinder(
        radius=NECK_RADIUS - 3.6,
        height=3.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    divider = Location((SEPTUM_X, 0, 216.5)) * Box(
        3.2, 65.0, 27.5, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    hot_riser_outer = Location((-17.5, 0, 217.0)) * Cylinder(
        radius=9.5, height=27.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    hot_riser_bore = Location((-17.5, 0, 216.5)) * Cylinder(
        radius=7.2, height=28.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    cold_riser_outer = Location((15.5, 0, 217.0)) * Cylinder(
        radius=10.5, height=27.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    cold_riser_bore = Location((15.5, 0, 216.5)) * Cylinder(
        radius=8.0, height=28.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    separators = (
        deck
        + divider
        + (hot_riser_outer - hot_riser_bore)
        + (cold_riser_outer - cold_riser_bore)
    )
    return _finalize_part(separators, "flow_separators")


def build_lid_collar_base() -> Part:
    """Matte black BPA-free PP/PETG lid collar with recessed spout gallery & bridge pillars."""
    seam = Location((0, 0, LID_Z_START)) * Cylinder(
        radius=NECK_RADIUS - 0.5,
        height=1.6,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    main_collar = Location((0, 0, LID_Z_START + 1.5)) * Cylinder(
        radius=NECK_RADIUS,
        height=COLLAR_TOP_Z - (LID_Z_START + 1.5),
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    main_collar = chamfer(
        main_collar.edges().filter_by(lambda e: e.center().Z > COLLAR_TOP_Z - 0.2),
        length=1.8,
    )

    collar = seam + main_collar

    cavity = Location((0, 0, LID_Z_START - 0.5)) * Cylinder(
        radius=NECK_RADIUS - 3.4,
        height=(COLLAR_TOP_Z - LID_Z_START) + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    collar = collar - cavity

    front_latch_recess = Location((0, NECK_RADIUS - 1.0, 231.0)) * Box(
        18.5, 4.0, 14.5, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    collar = collar - front_latch_recess

    front_pillar = Location((0, 25.0, COLLAR_TOP_Z - 1.0)) * Box(
        16.0,
        14.0,
        (GALLERY_TOP_Z - COLLAR_TOP_Z) + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    rear_pillar = Location((0, -25.0, COLLAR_TOP_Z - 1.0)) * Box(
        16.0,
        14.0,
        (GALLERY_TOP_Z - COLLAR_TOP_Z) + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    center_post = Location((SEPTUM_X, 0, COLLAR_TOP_Z - 1.0)) * Box(
        4.4,
        56.0,
        (GALLERY_TOP_Z - COLLAR_TOP_Z) + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    return _finalize_part(
        collar + front_pillar + rear_pillar + center_post,
        "lid_collar_base",
    )


def build_individual_spout_locks() -> Part:
    """Front thumb-release latch button and individual left/right spout safety lock tabs."""
    front_latch = Location((0, NECK_RADIUS - 0.6, 231.0)) * Box(
        17.2, 3.2, 13.2, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    front_latch = fillet(front_latch.edges().filter_by(Axis.Y), radius=1.8)
    front_latch = chamfer(
        front_latch.faces().sort_by(Axis.Y)[-1].edges(), length=0.6
    )

    hot_lock_tab = Location((-7.5, 19.5, 245.5)) * Box(
        5.5, 5.0, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    cold_lock_tab = Location((5.5, 19.5, 245.5)) * Box(
        5.5, 5.0, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    return _finalize_part(
        front_latch + hot_lock_tab + cold_lock_tab,
        "individual_spout_locks",
    )


def _build_ribbed_zip_spout(x_pos: float, radius: float, label: str) -> Part:
    """Construct a color-coded leak-proof zip spout with dual silicone sealing ribs."""
    core = Location((x_pos, 0, 242.0)) * Cylinder(
        radius=radius,
        height=13.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    lower_rib = Location((x_pos, 0, 244.8)) * Cylinder(
        radius=radius + 2.2,
        height=2.8,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    lower_rib = fillet(lower_rib.edges(), radius=1.1)

    upper_rib = Location((x_pos, 0, 249.4)) * Cylinder(
        radius=radius + 2.2,
        height=2.8,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    upper_rib = fillet(upper_rib.edges(), radius=1.1)

    spout = core + lower_rib + upper_rib

    bore = Location((x_pos, 0, 241.5)) * Cylinder(
        radius=radius - 2.4,
        height=14.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return _finalize_part(spout - bore, label)


def build_zip_spouts() -> tuple[Part, Part]:
    """Color-coded Red (Hot, -X) and Blue (Cold, +X) independent zip spouts."""
    hot_spout = _build_ribbed_zip_spout(
        x_pos=-17.5, radius=10.2, label="hot_zip_spout"
    )
    cold_spout = _build_ribbed_zip_spout(
        x_pos=15.5, radius=11.4, label="cold_zip_spout"
    )
    return hot_spout, cold_spout


def build_sap_top_assembly() -> tuple[Part, Part]:
    """Overhanging top cap housing and central SAP Safety Lock release button."""
    top_cap = Location((0, 0, GALLERY_TOP_Z)) * Cylinder(
        radius=35.8,
        height=CAP_TOP_Z - GALLERY_TOP_Z,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_cap = chamfer(top_cap.edges(), length=1.0)

    lock_bore = Location((0, 0, GALLERY_TOP_Z + 1.5)) * Cylinder(
        radius=13.2,
        height=6.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_cap_part = _finalize_part(top_cap - lock_bore, "sap_top_cap")

    sap_button = Location((0, 0, GALLERY_TOP_Z + 2.2)) * Cylinder(
        radius=12.0,
        height=7.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    sap_button = fillet(
        sap_button.edges().filter_by(lambda e: e.center().Z > GALLERY_TOP_Z + 8.5),
        radius=1.4,
    )
    sap_button_part = _finalize_part(sap_button, "sap_safety_lock_button")

    return top_cap_part, sap_button_part


def build_lid_subassemblies() -> list[Part]:
    """Return all 8 labeled dual-zip lid and SAP safety lock components."""
    gasket = build_lid_silicone_gasket()
    separators = build_flow_separators()
    collar = build_lid_collar_base()
    locks = build_individual_spout_locks()
    hot_spout, cold_spout = build_zip_spouts()
    top_cap, sap_button = build_sap_top_assembly()
    return [
        gasket,
        separators,
        collar,
        locks,
        hot_spout,
        cold_spout,
        top_cap,
        sap_button,
    ]