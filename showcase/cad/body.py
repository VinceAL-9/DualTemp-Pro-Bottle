# showcase/cad/body.py
from typing import cast
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cone,
    Cylinder,
    Location,
    Mode,
    Part,
    insert,
    fillet,
)

OUTER_RADIUS = 42.0
NECK_RADIUS = 37.0
BODY_Z_START = 68.0
SHOULDER_Z = 196.0
BODY_Z_END = 218.0
CHAMBER_FLOOR_Z = 84.0
CHAMBER_TOP_Z = 216.0
SEPTUM_X = -1.8  # Shifts boundary toward -X for 350 ml Hot / 400 ml Cold split


def _pill_cutout_y(z_center: float, width: float, height: float, depth: float) -> Part:
    """Create a vertical pill-shaped solid along +Y for bezel cutouts and molding."""
    pill = Location((0, OUTER_RADIUS - (depth / 2.0) + 1.0, z_center)) * Box(
        width, depth + 2.0, height, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    return cast(
        Part, fillet(pill.edges().filter_by(Axis.Y), radius=(width / 2.0) - 0.2)
    )


def build_outer_body_shell() -> Part:
    """Matte powder-coated stainless steel outer shell with tapered shoulder and grip recess."""
    lower_cyl = Location((0, 0, BODY_Z_START)) * Cylinder(
        radius=OUTER_RADIUS,
        height=SHOULDER_Z - BODY_Z_START,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shoulder = Location((0, 0, SHOULDER_Z)) * Cone(
        bottom_radius=OUTER_RADIUS,
        top_radius=NECK_RADIUS,
        height=BODY_Z_END - SHOULDER_Z,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shell = lower_cyl + shoulder

    inner_cyl = Location((0, 0, BODY_Z_START - 0.5)) * Cylinder(
        radius=OUTER_RADIUS - 1.4,
        height=(SHOULDER_Z - BODY_Z_START) + 0.6,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    inner_shoulder = Location((0, 0, SHOULDER_Z)) * Cone(
        bottom_radius=OUTER_RADIUS - 1.4,
        top_radius=NECK_RADIUS - 1.4,
        height=(BODY_Z_END - SHOULDER_Z) + 0.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shell = shell - (inner_cyl + inner_shoulder)

    grip_groove_outer = Location((0, 0, 104.0)) * Cylinder(
        radius=OUTER_RADIUS + 0.5,
        height=72.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    grip_groove_inner = Location((0, 0, 104.0)) * Cylinder(
        radius=OUTER_RADIUS - 0.5,
        height=72.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shell = shell - (grip_groove_outer - grip_groove_inner)
    shell = shell - _pill_cutout_y(z_center=170.0, width=23.6, height=43.6, depth=4.0)

    shell.label = "outer_body_shell"
    return cast(Part, shell)


# Replace build_silicone_grip() in showcase/cad/body.py
def build_silicone_grip() -> Part:
    """Food-grade RTV-2 textured grey silicone midsection grip sleeve."""
    outer = Location((0, 0, 104.0)) * Cylinder(
        radius=OUTER_RADIUS + 0.35,
        height=72.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    inner = Location((0, 0, 103.5)) * Cylinder(
        radius=OUTER_RADIUS - 0.45,
        height=73.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    cutout = _pill_cutout_y(z_center=170.0, width=24.2, height=44.2, depth=4.0)

    with BuildPart() as grip_builder:
        insert(outer)
        insert(inner, mode=Mode.SUBTRACT)
        insert(cutout, mode=Mode.SUBTRACT)

    grip = grip_builder.part
    if grip is None:
        raise RuntimeError("Failed to construct silicone_grip geometry.")

    grip.label = "silicone_grip"
    return grip


def _build_d_chamber(is_hot: bool) -> Part:
    """Construct a 316 stainless steel D-shaped chamber (350 ml Hot or 400 ml Cold)."""
    r_outer = 38.2
    wall = 1.2
    height = CHAMBER_TOP_Z - CHAMBER_FLOOR_Z
    gap_half = 2.0

    full_cyl = Location((0, 0, CHAMBER_FLOOR_Z)) * Cylinder(
        radius=r_outer, height=height, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    inner_cyl = Location((0, 0, CHAMBER_FLOOR_Z + wall)) * Cylinder(
        radius=r_outer - wall,
        height=height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    if is_hot:
        x_max = SEPTUM_X - gap_half
        outer_clip = Location((x_max - 45.0, 0, CHAMBER_FLOOR_Z)) * Box(
            90.0, 90.0, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        inner_clip = Location((x_max - wall - 45.0, 0, CHAMBER_FLOOR_Z + wall)) * Box(
            90.0, 90.0, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    else:
        x_min = SEPTUM_X + gap_half
        outer_clip = Location((x_min + 45.0, 0, CHAMBER_FLOOR_Z)) * Box(
            90.0, 90.0, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        inner_clip = Location((x_min + wall + 45.0, 0, CHAMBER_FLOOR_Z + wall)) * Box(
            90.0, 90.0, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )

    solid_d = full_cyl & outer_clip
    hollow_d = inner_cyl & inner_clip
    chamber = solid_d - hollow_d
    chamber.label = "hot_chamber_liner" if is_hot else "cold_chamber_liner"
    return cast(Part, chamber)


def build_copper_radiant_shield() -> Part:
    """Copper foil radiant heat barrier suspended inside the 4 mm central vacuum gap."""
    shield = Location((SEPTUM_X, 0, CHAMBER_FLOOR_Z + 1.0)) * Box(
        0.6,
        72.0,
        (CHAMBER_TOP_Z - CHAMBER_FLOOR_Z) - 3.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    shield.label = "copper_radiant_shield"
    return cast(Part, shield)


def build_power_button_assembly() -> tuple[Part, Part]:
    """Front brushed-aluminum bezel and tactile power button with green LED ring."""
    bezel = Location((0, OUTER_RADIUS - 0.6, 170.0)) * Box(
        23.0, 2.4, 43.0, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    bezel = fillet(bezel.edges().filter_by(Axis.Y), radius=11.2)

    bore = Location((0, OUTER_RADIUS - 0.6, 170.0)) * Cylinder(
        radius=6.6, height=4.0, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    ).rotate(Axis.X, 90)
    bezel = bezel - bore
    bezel.label = "power_button_bezel"

    button = Location((0, OUTER_RADIUS - 0.3, 170.0)) * Cylinder(
        radius=6.1, height=2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER)
    ).rotate(Axis.X, 90)
    button.label = "power_button_cap"

    return cast(Part, bezel), cast(Part, button)


def build_body_subassemblies() -> list[Part]:
    """Return all labeled dual-chamber body and power-switch components."""
    outer_shell = build_outer_body_shell()
    grip = build_silicone_grip()
    hot_chamber = _build_d_chamber(is_hot=True)
    cold_chamber = _build_d_chamber(is_hot=False)
    copper_shield = build_copper_radiant_shield()
    bezel, button = build_power_button_assembly()
    return [
        outer_shell,
        grip,
        hot_chamber,
        cold_chamber,
        copper_shield,
        bezel,
        button,
    ]