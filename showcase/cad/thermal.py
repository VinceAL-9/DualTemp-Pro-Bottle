# showcase/cad/thermal.py
from build123d import (
    Align,
    Box,
    BuildPart,
    Cylinder,
    Locations,
    Mode,
    Part,
)

INNER_RADIUS = 40.5  # Matches OUTER_RADIUS (42.0) - WALL_THICKNESS (1.5) in base.py
BULKHEAD_Z = 68.0    # Mates flush with top of base_housing


def build_thermal_bulkhead() -> Part:
    """Structural thermal-isolation plate at Z = 68 mm separating base and upper body."""
    with BuildPart() as builder:
        with Locations((0, 0, BULKHEAD_Z)):
            Cylinder(
                radius=INNER_RADIUS - 0.2,
                height=3.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        # Central cutout allowing the TEC1-12706 Peltier stack and heatsinks to pass through
        with Locations((0, 0, BULKHEAD_Z - 0.5)):
            Box(
                46.0,
                42.0,
                4.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    assert builder.part is not None
    bulkhead = builder.part
    bulkhead.label = "thermal_bulkhead"
    return bulkhead


def build_peltier_module() -> Part:
    """TEC1-12706 40x40mm thermoelectric plate oriented for dual-chamber heat pumping."""
    # Mounted vertically at X = -1.8 mm to align with the 350ml / 400ml chamber septum
    with BuildPart() as builder:
        with Locations((-1.8, 0, 56.0)):
            Box(3.8, 36.0, 28.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    assert builder.part is not None
    plate = builder.part
    plate.label = "peltier_module"
    return plate


def _build_finned_heatsink(x_sign: int, x_face: float, label: str) -> Part:
    """Custom extruded-style aluminum heatsink block coupling Peltier face to chamber floor."""
    spine_x = x_face + (x_sign * 2.0)
    top_plate_x = x_face + (x_sign * 11.0)
    fin_x = x_face + (x_sign * 10.5)
    fin_locations = [(fin_x, 0, 56.0 + (i * 4.0)) for i in range(6)]

    with BuildPart() as builder:
        # Vertical contact spine against the Peltier ceramic face
        with Locations((spine_x, 0, 55.0)):
            Box(4.0, 34.0, 29.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Top horizontal spreader plate pressing directly against the Z = 84 mm chamber floor
        with Locations((top_plate_x, 0, 80.5)):
            Box(22.0, 34.0, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # 6 horizontal cooling/heating fins aligned with the side louver vents
        with Locations(*fin_locations):
            Box(21.0, 32.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))

    assert builder.part is not None
    sink = builder.part
    sink.label = label
    return sink


def build_heatsinks() -> tuple[Part, Part]:
    """Build hot-side (-X, 65°C) and cold-side (+X, 4°C) custom aluminum heatsinks."""
    hot_sink = _build_finned_heatsink(x_sign=-1, x_face=-3.7, label="hot_heatsink")
    cold_sink = _build_finned_heatsink(x_sign=1, x_face=0.1, label="cold_heatsink")
    return hot_sink, cold_sink


def build_ntc_sensor_harness() -> Part:
    """Dual NTC 10k thermistor probes monitoring hot (65°C) and cold (4°C) chamber floors."""
    with BuildPart() as builder:
        with Locations((-16.0, 18.0, 72.0), (14.0, 18.0, 72.0)):
            Cylinder(
                radius=1.5,
                height=12.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with Locations((-1.0, 18.0, 71.0)):
            Box(32.0, 2.2, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    assert builder.part is not None
    sensors = builder.part
    sensors.label = "ntc_sensor_harness"
    return sensors


def build_thermal_subassemblies() -> list[Part]:
    """Return all labeled thermoelectric subsystem components."""
    bulkhead = build_thermal_bulkhead()
    peltier = build_peltier_module()
    hot_sink, cold_sink = build_heatsinks()
    sensors = build_ntc_sensor_harness()
    return [bulkhead, peltier, hot_sink, cold_sink, sensors]