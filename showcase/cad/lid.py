from __future__ import annotations

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    RectangleRounded,
    chamfer,
    extrude,
    fillet,
    revolve,
)


def _require_part(builder: BuildPart, part_name: str) -> Part:
    """Narrow BuildPart.part from `Part | None` to `Part` for strict static typing."""
    if builder.part is None:
        raise RuntimeError(f"Failed to generate CAD geometry for '{part_name}'.")
    return builder.part


def _build_collar_and_canopy(
    outer_radius: float,
    collar_height: float,
    canopy_bottom_z: float,
    canopy_thickness: float,
    sap_pocket_radius: float,
) -> Part:
    """Build the lower threaded PP/PETG collar, individual spout locks, twin pillars, and top canopy."""
    wall_thickness: float = 3.0
    deck_thickness: float = 4.0
    inner_radius: float = outer_radius - wall_thickness
    canopy_radius: float = outer_radius + 1.2

    with BuildPart() as housing:
        # 1. Main lower collar cylinder
        Cylinder(
            radius=outer_radius,
            height=collar_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        bottom_edge = housing.edges().sort_by(Axis.Z)[0]
        top_collar_edge = housing.edges().sort_by(Axis.Z)[-1]
        chamfer(bottom_edge, length=0.8)
        chamfer(top_collar_edge, length=1.0)

        # 2. Hollow underside cavity for bottle neck engagement
        Cylinder(
            radius=inner_radius,
            height=collar_height - deck_thickness,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

        # 3. Internal annular thread ribs inside the collar skirt
        for thread_z in (6.5, 11.5):
            with BuildSketch(Plane.XZ):
                with Locations((inner_radius, thread_z)):
                    Circle(radius=0.85)
            revolve(axis=Axis.Z, mode=Mode.ADD)

        # 4. Recessed circular spout wells on the top deck (Left = Hot, Right = Cold)
        with BuildSketch(Plane.XY.offset(collar_height - 1.4)):
            with Locations((-17.5, 0.0), (17.5, 0.0)):
                Circle(radius=9.6)
        extrude(amount=1.6, mode=Mode.SUBTRACT)

        # 5. Individual Spout Safety Lock buttons on front (-Y) and rear (+Y) collar faces
        for y_sign in (-1.0, 1.0):
            lock_plane = Plane(
                origin=(0.0, y_sign * (outer_radius - 0.6), collar_height * 0.52),
                z_dir=(0.0, y_sign, 0.0),
            )
            with BuildSketch(lock_plane):
                RectangleRounded(width=14.0, height=9.5, radius=2.0)
            extrude(amount=2.1, mode=Mode.ADD)

            ridge_plane = Plane(
                origin=(0.0, y_sign * (outer_radius + 1.4), collar_height * 0.52 + 1.8),
                z_dir=(0.0, y_sign, 0.0),
            )
            with BuildSketch(ridge_plane):
                RectangleRounded(width=9.5, height=1.8, radius=0.6)
            extrude(amount=0.7, mode=Mode.ADD)

        # 6. Twin curved vertical support pillars framing the recessed left/right spout bays
        pillar_height: float = canopy_bottom_z - collar_height + 0.5
        pillar_outer_r: float = outer_radius - 0.6
        pillar_inner_r: float = outer_radius - 5.4

        with BuildSketch(Plane.XY.offset(collar_height - 0.2)):
            Circle(radius=pillar_outer_r)
            Circle(radius=pillar_inner_r, mode=Mode.SUBTRACT)
        extrude(amount=pillar_height, mode=Mode.ADD)

        bay_cut_height: float = canopy_bottom_z - collar_height
        for x_sign in (-1.0, 1.0):
            with Locations((x_sign * (outer_radius * 0.68), 0.0, collar_height)):
                Box(
                    outer_radius * 1.15,
                    outer_radius * 1.48,
                    bay_cut_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

        # 7. Overhanging protective top canopy disc
        with Locations((0.0, 0.0, canopy_bottom_z)):
            Cylinder(
                radius=canopy_radius,
                height=canopy_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.ADD,
            )

        top_canopy_rim = housing.edges().sort_by(Axis.Z)[-1]
        chamfer(top_canopy_rim, length=1.1)

        # 8. Central recessed pocket for the SAP Safety Lock button
        with Locations((0.0, 0.0, canopy_bottom_z + 1.2)):
            Cylinder(
                radius=sap_pocket_radius,
                height=canopy_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    part = _require_part(housing, "lid_collar_and_canopy")
    part.label = "lid_collar"
    part.color = Color(0.11, 0.12, 0.13)
    return part


def _build_sap_safety_lock(
    canopy_bottom_z: float,
    canopy_thickness: float,
    pocket_radius: float,
) -> Part:
    """Build the central top SAP Safety Lock actuator button."""
    button_radius: float = pocket_radius - 1.6
    button_base_z: float = canopy_bottom_z + 1.4
    button_height: float = canopy_thickness + 2.6

    with BuildPart() as sap_lock:
        with Locations((0.0, 0.0, button_base_z)):
            Cylinder(
                radius=button_radius,
                height=button_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        top_rim = sap_lock.edges().sort_by(Axis.Z)[-1]
        chamfer(top_rim, length=1.2)

        with Locations((0.0, 0.0, button_base_z + button_height - 0.35)):
            Cylinder(
                radius=button_radius - 2.6,
                height=0.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    part = _require_part(sap_lock, "sap_safety_lock")
    part.label = "sap_safety_lock"
    part.color = Color(0.24, 0.25, 0.27)
    return part


def _build_zip_spout(
    x_offset: float,
    collar_height: float,
    canopy_bottom_z: float,
    label: str,
    color: Color,
) -> Part:
    """Build an independent color-coded zip spout (Red = Hot 65°C, Blue = Cold 4°C)."""
    x_sign: float = -1.0 if x_offset < 0.0 else 1.0
    stem_base_z: float = collar_height - 1.2
    stem_height: float = (canopy_bottom_z - stem_base_z) - 0.8
    tilt_angle: float = 16.0 * x_sign

    with BuildPart() as spout:
        with Locations((x_offset, 0.0, stem_base_z)):
            Cylinder(
                radius=7.2,
                height=stem_height * 0.52,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        rotated_plane = Plane.XY.offset(stem_base_z + stem_height * 0.45).rotated(
            (0.0, tilt_angle, 0.0)
        )
        nozzle_plane = Plane(
            origin=(x_offset, 0.0, stem_base_z + stem_height * 0.45),
            z_dir=rotated_plane.z_dir,
        )
        with BuildSketch(nozzle_plane):
            RectangleRounded(width=12.6, height=10.4, radius=4.2)
        extrude(amount=stem_height * 0.56, mode=Mode.ADD)

        with BuildSketch(nozzle_plane):
            RectangleRounded(width=7.4, height=5.6, radius=2.4)
        extrude(amount=stem_height * 0.62, mode=Mode.SUBTRACT)

        with Locations((x_offset - x_sign * 5.8, 0.0, stem_base_z + stem_height * 0.48)):
            Cylinder(
                radius=2.2,
                height=9.6,
                rotation=(90.0, 0.0, 0.0),
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.ADD,
            )

    part = _require_part(spout, label)
    part.label = label
    part.color = color
    return part


def _build_silicone_seals(
    outer_radius: float,
    collar_height: float,
) -> Part:
    """Build food-grade RTV-2 stacked spout sealing rings and IPX7 perimeter neck gasket."""
    inner_neck_radius: float = outer_radius - 3.0

    with BuildPart() as seals:
        for x_offset in (-17.5, 17.5):
            for ring_z in (collar_height + 2.2, collar_height + 5.2):
                with BuildPart(mode=Mode.ADD) as ring_builder:
                    with BuildSketch(Plane.XZ):
                        with Locations((8.3, ring_z)):
                            Circle(radius=1.35)
                    revolve(axis=Axis.Z)
                ring_part = _require_part(ring_builder, "spout_silicone_ring")
                if seals.part is not None:
                    seals.part.fuse(ring_part.moved(Location((x_offset, 0.0, 0.0))))

        with BuildSketch(Plane.XZ):
            with Locations((inner_neck_radius - 0.3, 4.2)):
                Circle(radius=1.2)
        revolve(axis=Axis.Z, mode=Mode.ADD)

    part = _require_part(seals, "silicone_seals")
    part.label = "silicone_seals"
    part.color = Color(0.84, 0.87, 0.90, 0.92)
    return part


def _build_flow_separator(
    outer_radius: float,
    collar_height: float,
) -> Part:
    """Build the underside vertical septum isolating the 350 ml Hot and 400 ml Cold chambers."""
    deck_bottom_z: float = collar_height - 4.0
    septum_height: float = 14.5
    septum_width: float = (outer_radius - 3.4) * 2.0
    chamber_split_x: float = -1.8

    with BuildPart() as separator:
        with Locations((chamber_split_x, 0.0, deck_bottom_z - septum_height)):
            Box(
                3.2,
                septum_width,
                septum_height + 0.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        bottom_tip = separator.edges().sort_by(Axis.Z)[0]
        fillet(bottom_tip, radius=1.0)

    part = _require_part(separator, "flow_separator")
    part.label = "flow_separator"
    part.color = Color(0.16, 0.17, 0.19)
    return part

# In showcase/cad/lid.py — update build_lid_subassemblies at the bottom of the file:

DEFAULT_NECK_RADIUS: float = 39.0   # Match outer neck radius in showcase/cad/body.py
DEFAULT_LID_BASE_Z: float = 218.0   # Match top Z of bottle neck in showcase/cad/body.py


def build_lid_subassemblies(
    outer_radius: float = DEFAULT_NECK_RADIUS,
    collar_height: float = 20.0,
    canopy_gap: float = 17.0,
    canopy_thickness: float = 5.0,
    z_offset: float = DEFAULT_LID_BASE_Z,
) -> list[Part]:
    """Return all labeled DualTemp Pro lid sub-parts positioned at the bottle neck."""
    canopy_bottom_z: float = collar_height + canopy_gap
    sap_pocket_radius: float = 11.4

    parts: list[Part] = [
        _build_collar_and_canopy(
            outer_radius=outer_radius,
            collar_height=collar_height,
            canopy_bottom_z=canopy_bottom_z,
            canopy_thickness=canopy_thickness,
            sap_pocket_radius=sap_pocket_radius,
        ),
        _build_sap_safety_lock(
            canopy_bottom_z=canopy_bottom_z,
            canopy_thickness=canopy_thickness,
            pocket_radius=sap_pocket_radius,
        ),
        _build_zip_spout(
            x_offset=-17.5,
            collar_height=collar_height,
            canopy_bottom_z=canopy_bottom_z,
            label="hot_spout_red",
            color=Color(0.84, 0.13, 0.16),
        ),
        _build_zip_spout(
            x_offset=17.5,
            collar_height=collar_height,
            canopy_bottom_z=canopy_bottom_z,
            label="cold_spout_blue",
            color=Color(0.09, 0.44, 0.86),
        ),
        _build_silicone_seals(
            outer_radius=outer_radius,
            collar_height=collar_height,
        ),
        _build_flow_separator(
            outer_radius=outer_radius,
            collar_height=collar_height,
        ),
    ]

    if z_offset != 0.0:
        parts = [part.moved(Location((0.0, 0.0, z_offset))) for part in parts]

    return parts

def build_lid(
    outer_radius: float = 39.0,
    collar_height: float = 20.0,
    canopy_gap: float = 17.0,
    canopy_thickness: float = 5.0,
    z_offset: float = 0.0,
) -> Compound:
    """Construct the complete DualTemp Pro Dual-Zip Spout Lid Compound."""
    return Compound(
        label="lid",
        children=build_lid_subassemblies(
            outer_radius=outer_radius,
            collar_height=collar_height,
            canopy_gap=canopy_gap,
            canopy_thickness=canopy_thickness,
            z_offset=z_offset,
        ),
    )


create_lid = build_lid