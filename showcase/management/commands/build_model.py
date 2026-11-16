# showcase/management/commands/build_model.py
from pathlib import Path
from build123d import Compound, export_gltf, export_step
from django.conf import settings
from django.core.management.base import BaseCommand
from showcase.cad.base import build_base_subassemblies
from showcase.cad.body import build_body_subassemblies
from showcase.cad.thermal import build_thermal_subassemblies


class Command(BaseCommand):
    help = "Builds the DualTemp Pro Smart Bottle 3D assembly and exports binary glTF."

    def add_arguments(self, parser):
        parser.add_argument(
            "--step",
            action="store_true",
            help="Also export a CAD STEP assembly into exports/dualtemp_bottle.step",
        )

    def handle(self, *args, **options):
        parts = [
            *build_base_subassemblies(),
            *build_thermal_subassemblies(),
            *build_body_subassemblies(),
        ]
        assembly = Compound(label="dualtemp_pro_bottle", children=parts)

        output_dir = Path(settings.BASE_DIR) / "static" / "models"
        output_dir.mkdir(parents=True, exist_ok=True)
        glb_path = output_dir / "dualtemp_bottle.glb"

        export_gltf(assembly, str(glb_path), binary=True)
        size_kb = glb_path.stat().st_size / 1024
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {glb_path} ({size_kb:.1f} KB, {len(parts)} sub-assemblies)"
            )
        )

        if options["step"]:
            step_dir = Path(settings.BASE_DIR) / "exports"
            step_dir.mkdir(parents=True, exist_ok=True)
            step_path = step_dir / "dualtemp_bottle.step"
            export_step(assembly, str(step_path))
            self.stdout.write(self.style.SUCCESS(f"Exported {step_path}"))