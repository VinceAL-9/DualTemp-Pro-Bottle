# showcase/cad/base.py
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    Locations,
    Mode,
    Part,
    chamfer,
    fillet,
)

OUTER_RADIUS = 42.0   # 84 mm total bottle diameter
WALL_THICKNESS = 1.5  # 81 mm internal bay diameter
BASE_HEIGHT = 68.0    # Z = 0 to 68 mm electronics & battery bay


def build_base_housing() -> Part:
    """Matte 304/316 stainless steel lower skirt with USB-C cutout and heat vents."""
    with BuildPart() as builder:
        Cylinder(
            radius=OUTER_RADIUS,
            height=BASE_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # Fillet bottom edge resting on Z = 0
        fillet(builder.edges().filter_by(lambda e: e.center().Z < 0.1), radius=3.0)

        # Hollow out interior cavity above a 2.5 mm solid bottom floor
        with Locations((0, 0, 2.5)):
            Cylinder(
                radius=OUTER_RADIUS - WALL_THICKNESS,
                height=BASE_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Cut stadium-shaped USB-C opening on the +Y wall at Z = 11 mm
        with BuildPart(mode=Mode.SUBTRACT) as cutout:
            with Locations((0, OUTER_RADIUS - 0.5, 11.0)):
                Box(10.4, 6.0, 4.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            fillet(cutout.edges().filter_by(Axis.Y), radius=1.9)

        # Cut 4 horizontal heat-exchange louver slots on -X and +X near top of bay
        for side in (-1, 1):
            for i in range(4):
                z_pos = 54.0 + (i * 2.6)
                with Locations((side * (OUTER_RADIUS - 0.5), 0, z_pos)):
                    Box(
                        6.0,
                        22.0,
                        1.2,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        mode=Mode.SUBTRACT,
                    )

    assert builder.part is not None
    housing = builder.part
    housing.label = "base_housing"
    return housing


def build_battery_pack() -> Part:
    """Ultra-slim 10,000mAh dual-cell LiPo pouch pack seated in the rear half of the bay."""
    with BuildPart() as builder:
        for y_pos in (-14.0, -3.5):
            with Locations((0, y_pos, 28.0)):
                Box(52.0, 9.5, 44.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        fillet(builder.edges(), radius=1.2)

    assert builder.part is not None
    pack = builder.part
    pack.label = "battery_pack"
    return pack


def build_controller_pcb() -> Part:
    """30W PD USB-C BMS & fixed-temperature thermoelectric controller board."""
    with BuildPart() as builder:
        with Locations((0, 18.0, 24.0)):
            Box(50.0, 1.6, 32.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        with Locations((-10.0, 15.8, 18.0)):
            Box(10.0, 3.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        with Locations((8.0, 16.4, 26.0)):
            Box(9.0, 1.8, 9.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    assert builder.part is not None
    pcb = builder.part
    pcb.label = "controller_pcb"
    return pcb


def build_usbc_assembly() -> tuple[Part, Part]:
    """Waterproof USB-C 30W PD receptacle and removable RTV-2 silicone IPX7 plug."""
    with BuildPart() as port_builder:
        with Locations((0, 29.5, 11.0)):
            Box(9.0, 23.0, 3.2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        fillet(port_builder.edges().filter_by(Axis.Y), radius=1.3)

    assert port_builder.part is not None
    port = port_builder.part
    port.label = "usbc_port"

    with BuildPart() as plug_builder:
        with Locations((0, OUTER_RADIUS - 0.4, 11.0)):
            Box(10.2, 2.4, 4.4, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        fillet(plug_builder.edges().filter_by(Axis.Y), radius=1.8)
        chamfer(plug_builder.faces().sort_by(Axis.Y)[-1].edges(), length=0.4)

    assert plug_builder.part is not None
    plug = plug_builder.part
    plug.label = "usbc_silicone_plug"

    return port, plug


def build_base_subassemblies() -> list[Part]:
    """Return all labeled base components positioned in the master Z-up coordinate frame."""
    housing = build_base_housing()
    battery = build_battery_pack()
    pcb = build_controller_pcb()
    port, plug = build_usbc_assembly()
    return [housing, battery, pcb, port, plug]