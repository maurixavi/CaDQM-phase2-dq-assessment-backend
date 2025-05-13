#!/usr/bin/env python
import os
import django
import sys
from pathlib import Path
from django.core.exceptions import ObjectDoesNotExist

# Configurar Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from dqmodel.models import DQDimensionBase, DQFactorBase, DQMetricBase, DQMethodBase
from .markdown_parser import extract_dimensions, extract_factors, extract_metrics, extract_methods

class DataLoader:
    def __init__(self):
        self.counts = {
            'dimensions': 0,
            'factors': 0,
            'metrics': 0,
            'methods': 0
        }

    def load_from_markdown(self, file_path: str):
        """Carga todos los datos desde un archivo markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("⏳ Extrayendo datos del markdown...")
            dimensions = extract_dimensions(content)
            factors = extract_factors(content)
            metrics = extract_metrics(content)
            methods = extract_methods(content)

            self._load_dimensions(dimensions)
            self._load_factors(factors)
            self._load_metrics(metrics)
            self._load_methods(methods)

            self._print_summary()

        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {file_path}")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            raise

    def _load_dimensions(self, dimensions: list):
        for dim in dimensions:
            _, created = DQDimensionBase.objects.get_or_create(
                name=dim['name'],
                defaults={'semantic': dim['semantic']}
            )
            if created: self.counts['dimensions'] += 1

    def _load_factors(self, factors: list):
        for factor in factors:
            try:
                dimension = DQDimensionBase.objects.get(name=factor['dimension'])
                _, created = DQFactorBase.objects.get_or_create(
                    name=factor['name'],
                    defaults={
                        'semantic': factor['semantic'],
                        'facetOf': dimension
                    }
                )
                if created: self.counts['factors'] += 1
            except ObjectDoesNotExist:
                print(f"⚠️ Dimensión faltante: {factor['dimension']}")

    def _load_metrics(self, metrics: list):
        for metric in metrics:
            try:
                factor = DQFactorBase.objects.get(name=metric['factor'])
                _, created = DQMetricBase.objects.get_or_create(
                    name=metric['name'],
                    defaults={
                        'purpose': metric['purpose'],
                        'granularity': metric['granularity'],
                        'resultDomain': metric['result_domain'],
                        'measures': factor
                    }
                )
                if created: self.counts['metrics'] += 1
            except ObjectDoesNotExist:
                print(f"⚠️ Factor faltante: {metric['factor']}")

    def _load_methods(self, methods: list):
        for method in methods:
            try:
                metric = DQMetricBase.objects.get(name=method['metric'])
                _, created = DQMethodBase.objects.get_or_create(
                    name=method['name'],
                    defaults={
                        'inputDataType': method['input_data_type'],
                        'outputDataType': method['output_data_type'],
                        'algorithm': method['algorithm'],
                        'implements': metric
                    }
                )
                if created: self.counts['methods'] += 1
            except ObjectDoesNotExist:
                print(f"⚠️ Métrica faltante: {method['metric']}")

    def _print_summary(self):
        print("\n✅ Carga completada:")
        for model, count in self.counts.items():
            print(f"- {model.capitalize()}: {count} nuevos")
        print("💡 Objetos existentes no fueron modificados")

if __name__ == '__main__':
    loader = DataLoader()
    md_file = Path(__file__).parent / "../data_sources/dqmodel_template_data.md"
    loader.load_from_markdown(md_file.resolve())