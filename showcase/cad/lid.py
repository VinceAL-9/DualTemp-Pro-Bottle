# showcase/cad/lid.py
from typing import cast

from build123d import (
    Align,
    Axis,
    Box,
    Cone,
    Cylinder,
    Ellipse,
    Location,
    Part,
    Rot,
    chamfer,
    extrude,
    fillet,
)

NECK_RADIUS = 37.0       # Matches NECK_RADIUS in body.py (74.0 mm diameter)
LID_Z_START = 218.0      # Mates flush with BODY_Z_END in body.py
COLLAR_TOP_Z = 244.0     # Upper rim of main lid collar
GALLERY_TOP_Z = 255.0    # Underside of overhanging SAP bridge
CAP_TOP_Z = 261.0        # Top surface of SAP bridge housing
SEPTUM_X = -1.8          # Matches asymmetric 350 ml Hot / 400 ml Cold split
BRIDGE_X = -1.6          # Centerline of the SAP bridge between Hot (-5.4) & Cold (+2.2) bays


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
        3.2, 65.0, 25.5, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # Risers terminate at Z = 242.0 mm to form lower valve seats for the pivoting spouts
    hot_riser_outer = Location((-17.5, 0, 217.0)) * Cylinder(
        radius=9.5, height=25.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    hot_riser_bore = Location((-17.5, 0, 216.5)) * Cylinder(
        radius=6.8, height=26.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    cold_riser_outer = Location((15.5, 0, 217.0)) * Cylinder(
        radius=10.5, height=25.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    cold_riser_bore = Location((15.5, 0, 216.5)) * Cylinder(
        radius=7.6, height=26.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
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

    # Vertical travel clearance slot for the SAP locking yoke (-3.4 mm stroke)
    yoke_travel_slot = Location((BRIDGE_X, 0, GALLERY_TOP_Z - 6.0)) * Box(
        6.4,
        6.4,
        7.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    center_post = center_post - yoke_travel_slot

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


def _build_ribbed_zip_spout(
    x_pos: float, radius: float, side_sign: float, label: str
) -> Part:
    """Construct a hinged drinking spout with bellows ribs, outer pivot knuckle & oval lip nozzle."""
    # 1. Lower spherical-bottomed valve base seating onto the chamber riser (Z = 241.0..245.5)
    valve_base = Location((x_pos, 0, 241.0)) * Cylinder(
        radius=radius - 0.8,
        height=4.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    valve_base = fillet(
        valve_base.edges().filter_by(lambda e: e.center().Z < 241.5),
        radius=1.2,
    )

    # 2. Outer Y-axis hinge knuckle where the spout pivots outward when unlocked
    hinge_x = x_pos + side_sign * (radius - 1.2)
    hinge_knuckle = (
        Location((hinge_x, 0, 243.5))
        * Rot(90, 0, 0)
        * Cylinder(
            radius=2.6,
            height=9.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
    )

    # 3. Dual accordion silicone sealing ribs visible inside the recessed lid gallery
    lower_rib = Location((x_pos, 0, 244.8)) * Cylinder(
        radius=radius + 1.4,
        height=2.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    lower_rib = fillet(lower_rib.edges(), radius=0.9)

    upper_rib = Location((x_pos, 0, 248.4)) * Cylinder(
        radius=radius + 1.0,
        height=2.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    upper_rib = fillet(upper_rib.edges(), radius=0.9)

    # 4. Tapered conical shoulder transitioning from circular bellows into an oval sip nozzle
    shoulder = Location((x_pos + side_sign * 0.7, 0, 250.2)) * Cone(
        bottom_radius=radius - 0.6,
        top_radius=radius - 2.6,
        height=2.6,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # 5. Outward-offset oval lip-contoured mouthpiece (Z = 251.6..255.0)
    mouthpiece_x = x_pos + side_sign * 1.8
    mouthpiece = Location((mouthpiece_x, 0, 251.6)) * extrude(
        Ellipse(
            x_radius=(radius - 1.6) * 0.68,
            y_radius=(radius - 1.6) * 0.92,
        ),
        amount=3.4,
    )
    mouthpiece = fillet(
        mouthpiece.edges().filter_by(lambda e: e.center().Z > 254.8),
        radius=0.9,
    )

    spout = (
        valve_base
        + hinge_knuckle
        + lower_rib
        + upper_rib
        + shoulder
        + mouthpiece
    )

    # 6. Internal flow channel: circular intake at the riser tapering to an oval sip slot at the lip
    lower_bore = Location((x_pos, 0, 240.0)) * Cylinder(
        radius=radius - 3.6,
        height=11.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    upper_sip_slot = Location((mouthpiece_x, 0, 250.5)) * extrude(
        Ellipse(
            x_radius=(radius - 3.8) * 0.62,
            y_radius=(radius - 3.8) * 0.88,
        ),
        amount=5.5,
    )

    return _finalize_part(spout - lower_bore - upper_sip_slot, label)


def build_zip_spouts() -> tuple[Part, Part]:
    """Color-coded Red (Hot, -X) and Blue (Cold, +X) independent zip spouts."""
    hot_spout = _build_ribbed_zip_spout(
        x_pos=-17.5, radius=10.2, side_sign=-1.0, label="hot_zip_spout"
    )
    cold_spout = _build_ribbed_zip_spout(
        x_pos=15.5, radius=11.4, side_sign=1.0, label="cold_zip_spout"
    )
    return hot_spout, cold_spout


def build_sap_top_assembly() -> tuple[Part, Part]:
    """Central front-to-back SAP bridge with open left/right side bays for both spouts."""
    top_cap = Location((0, 0, GALLERY_TOP_Z)) * Cylinder(
        radius=35.8,
        height=CAP_TOP_Z - GALLERY_TOP_Z,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_cap = chamfer(top_cap.edges(), length=1.0)

    # Open left (-X, Hot) and right (+X, Cold) side bays leaving the bridge at X = -5.4..+2.2 mm
    left_spout_bay = Location((-21.7, 0, GALLERY_TOP_Z - 0.5)) * Box(
        32.6,
        34.0,
        (CAP_TOP_Z - GALLERY_TOP_Z) + 1.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    right_spout_bay = Location((20.1, 0, GALLERY_TOP_Z - 0.5)) * Box(
        35.8,
        34.0,
        (CAP_TOP_Z - GALLERY_TOP_Z) + 1.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Pill-shaped upper counterbore on the 7.6 mm central bridge for the SAP release button
    lock_bore = Location((BRIDGE_X, 0, GALLERY_TOP_Z + 1.5)) * Box(
        5.6,
        18.6,
        6.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    lock_bore = fillet(lock_bore.edges().filter_by(Axis.Z), radius=2.6)

    # Lower guide bore for the internal yoke stem & SUS304 return spring
    stem_bore = Location((BRIDGE_X, 0, GALLERY_TOP_Z - 0.5)) * Cylinder(
        radius=3.2,
        height=3.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    top_cap_part = _finalize_part(
        top_cap - left_spout_bay - right_spout_bay - lock_bore - stem_bore,
        "sap_top_cap",
    )

    sap_button = Location((BRIDGE_X, 0, GALLERY_TOP_Z + 2.2)) * Box(
        4.8,
        17.8,
        7.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    sap_button = fillet(sap_button.edges().filter_by(Axis.Z), radius=2.2)
    sap_button = fillet(
        sap_button.edges().filter_by(lambda e: e.center().Z > GALLERY_TOP_Z + 8.5),
        radius=0.7,
    )
    sap_button_part = _finalize_part(sap_button, "sap_safety_lock_button")

    return top_cap_part, sap_button_part


def build_sap_interlock_internals(bridge_z: float = GALLERY_TOP_Z) -> list[Part]:
    """Internal SUS304 return spring and dual-lug locking yoke under sap_safety_lock_button."""
    stem = Location((BRIDGE_X, 0, bridge_z - 1.5)) * Cylinder(
        radius=1.8,
        height=5.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    crossbar = Location((BRIDGE_X, 0, bridge_z - 2.4)) * Box(
        11.6,
        4.8,
        1.8,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Twin downward locking lugs tucked behind the inner shoulders of Hot (-6.2) and Cold (+3.0) spouts
    left_lug = Location((-6.2, 0, bridge_z - 3.6)) * Box(
        2.4,
        4.8,
        2.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    right_lug = Location((3.0, 0, bridge_z - 3.6)) * Box(
        2.4,
        4.8,
        2.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    yoke_part = _finalize_part(
        stem + crossbar + left_lug + right_lug,
        "sap_locking_yoke",
    )

    spring_outer = Location((BRIDGE_X, 0, bridge_z - 0.2)) * Cylinder(
        radius=3.0,
        height=3.4,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    spring_inner = Location((BRIDGE_X, 0, bridge_z - 0.3)) * Cylinder(
        radius=2.1,
        height=3.6,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    spring_part = _finalize_part(
        spring_outer - spring_inner,
        "sap_return_spring",
    )

    return [yoke_part, spring_part]


def build_lid_subassemblies() -> list[Part]:
    """Return all 10 labeled dual-zip lid and SAP safety lock components."""
    gasket = build_lid_silicone_gasket()
    separators = build_flow_separators()
    collar = build_lid_collar_base()
    locks = build_individual_spout_locks()
    hot_spout, cold_spout = build_zip_spouts()
    top_cap, sap_button = build_sap_top_assembly()
    yoke, spring = build_sap_interlock_internals()
    return [
        gasket,
        separators,
        collar,
        locks,
        hot_spout,
        cold_spout,
        top_cap,
        sap_button,
        yoke,
        spring,
    ]