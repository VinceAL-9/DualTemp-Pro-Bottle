# showcase/management/commands/build_model.py
from pathlib import Path
from build123d import Compound, export_gltf
from django.conf import settings
from django.core.management.base import BaseCommand
from showcase.cad.base import build_base_subassemblies


class Command(BaseCommand):
    help = "Builds the DualTemp Pro Smart Bottle 3D assembly and exports binary glTF."

    def handle(self, *args, **options):
        parts = build_base_subassemblies()
        assembly = Compound(label="dualtemp_pro_bottle", children=parts)

        output_dir = Path(settings.BASE_DIR) / "static" / "models"
        output_dir.mkdir(parents=True, exist_ok=True)
        glb_path = output_dir / "dualtemp_base.glb"

        export_gltf(assembly, str(glb_path), binary=True)
        size_kb = glb_path.stat().st_size / 1024
        self.stdout.write(
            self.style.SUCCESS(f"Exported {glb_path} ({size_kb:.1f} KB)")
        )