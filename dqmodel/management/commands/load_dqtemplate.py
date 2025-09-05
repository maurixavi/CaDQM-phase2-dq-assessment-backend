from django.core.management.base import BaseCommand
from pathlib import Path
from dqmodel.templates.loaders.md_parser import parse_markdown
from dqmodel.templates.loaders.data_builder import DQModelBuilder
from dqmodel.templates.loaders.db_loader import DQModelLoader

class Command(BaseCommand):
    help = "Carga datos iniciales de DQModel desde un template Markdown"

    def add_arguments(self, parser):
        parser.add_argument(
            '--template',
            default='dqmodel_base',
            help='Nombre del template ubicado en dqmodel/templates/definitions/'
        )

    def handle(self, *args, **options):
        template_name = options['template']
        md_path = Path(f"dqmodel/templates/definitions/{template_name}.md")

        if not md_path.exists():
            self.stderr.write(f"Error: No se encontró el template '{md_path}'")
            return

        try:
            # 1. Parsear Markdown
            self.stdout.write(f"Leyendo template: {md_path}")
            raw_data = parse_markdown(md_path)

            # 2. Construir instancias de modelos
            self.stdout.write("Construyendo instancias modelos...")
            builder = DQModelBuilder(raw_data)
            model_instances = builder.build_all()

            # 3. Cargar en la base de datos
            self.stdout.write("Guardando en base de datos...")
            loader = DQModelLoader()
            stats = loader.load_all(model_instances)

            # Mostrar resultados
            self.stdout.write("\n✅ CARGA COMPLETADA")
            for model_type, counts in stats.items():
                self.stdout.write(
                    f"  - {model_type.capitalize()}: "
                    f"{counts['created']} nuevos, "
                    f"{counts['existing']} ya existentes, "
                    f"{counts['errors']} errores"
                )

        except Exception as e:
            self.stderr.write(f"\n❌ ERROR CRÍTICO: {str(e)}")
            raise