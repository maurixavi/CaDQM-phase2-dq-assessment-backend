from django.db import migrations
import os
import sys
from pathlib import Path


# Obtener la ruta al directorio padre (dqmodel)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Agregar el directorio padre al path de Python
sys.path.append(parent_dir)

# Configuración de paths para importar getData
# parent_dir = Path(__file__).resolve().parent.parent  # dqmodel/migrations/ -> dqmodel/
# sys.path.append(str(parent_dir))

# Importar las funciones de parseo desde getData
from getData import (
    read_markdown,
    extract_dimensions,
    extract_factors,
    extract_metrics,
    extract_methods
)

def load_initial_data(apps, schema_editor):
    """Carga todos los datos desde el markdown usando getData.py"""
    # Obtener modelos históricos
    DQDimensionBase = apps.get_model('dqmodel', 'DQDimensionBase')
    DQFactorBase = apps.get_model('dqmodel', 'DQFactorBase')
    DQMetricBase = apps.get_model('dqmodel', 'DQMetricBase')
    DQMethodBase = apps.get_model('dqmodel', 'DQMethodBase')
    
    # Ruta al archivo markdown (relativa a esta migración)
    # Construir la ruta al archivo dqmodel_template_data.md
    md_file_path = os.path.join(parent_dir, 'dqmodel_template_data.md')
    # md_file_path = os.path.join(parent_dir, 'dqmodel_template_data.md')
    
    try:
        # Leer y parsear el markdown
        markdown_text = read_markdown(md_file_path)
        
        # ===== 1. Cargar Dimensiones =====
        dimensions = extract_dimensions(markdown_text)
        for dim in dimensions:
            DQDimensionBase.objects.get_or_create(
                name=dim['name'],
                defaults={'semantic': dim['semantic']}
            )
        
        # ===== 2. Cargar Factores =====
        factors = extract_factors(markdown_text)
        for factor in factors:
            try:
                dimension = DQDimensionBase.objects.get(name=factor['dimension'])
                DQFactorBase.objects.get_or_create(
                    name=factor['name'],
                    defaults={
                        'semantic': factor['semantic'],
                        'facetOf': dimension
                    }
                )
            except DQDimensionBase.DoesNotExist:
                print(f"⚠️ Dimensión no encontrada: {factor['dimension']}")
        
        # ===== 3. Cargar Métricas =====
        metrics = extract_metrics(markdown_text)
        for metric in metrics:
            try:
                factor = DQFactorBase.objects.get(name=metric['factor'])
                DQMetricBase.objects.get_or_create(
                    name=metric['name'],
                    defaults={
                        'purpose': metric['purpose'],
                        'granularity': metric['granularity'],
                        'resultDomain': metric['result_domain'],
                        'measures': factor
                    }
                )
            except DQFactorBase.DoesNotExist:
                print(f"⚠️ Factor no encontrado: {metric['factor']}")
        
        # ===== 4. Cargar Métodos =====
        methods = extract_methods(markdown_text)
        for method in methods:
            try:
                metric = DQMetricBase.objects.get(name=method['metric'])
                DQMethodBase.objects.get_or_create(
                    name=method['name'],
                    defaults={
                        'inputDataType': method['input_data_type'],
                        'outputDataType': method['output_data_type'],
                        'algorithm': method['algorithm'],
                        'implements': metric
                    }
                )
            except DQMetricBase.DoesNotExist:
                print(f"⚠️ Métrica no encontrada: {method['metric']}")
                
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo markdown en: {md_file_path}")
        raise

class Migration(migrations.Migration):
    initial = False  # No es la migración inicial

    dependencies = [
        ('dqmodel', '0017_aggregationdqmethod_algorithm_and_more'),  
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]