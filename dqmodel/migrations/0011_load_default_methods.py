from django.db import migrations
import os
import sys

# Obtener la ruta al directorio padre (dqmodel)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Agregar el directorio padre al path de Python
sys.path.append(parent_dir)

# Ahora puedes importar desde getData
from getData import extract_methods, read_markdown

def load_default_methods(apps, schema_editor):
    # Obtiene el modelo de las dimensiones desde el apps registry.
    DQMetricBase = apps.get_model('dqmodel', 'DQMetricBase')
    DQMethodBase = apps.get_model('dqmodel', 'DQMethodBase')

    # Construir la ruta al archivo dqmodel_template_data.md
    md_file_path = os.path.join(parent_dir, 'dqmodel_template_data.md')
    
    # Leer el archivo markdown y Extraer los métodos
    markdown_text = read_markdown(md_file_path)
    methods_base = extract_methods(markdown_text)
    
    # Crear los metodos asociados a cada metrica
    for method in methods_base:
        # Get metric id as implements fk for the method
        try:
            metric = DQMetricBase.objects.get(name=method['metric'])
        except DQMetricBase.DoesNotExist:
            metric = None
        
        # Crear el factor y asociarlo a la dimensión mediante facetOf
        DQMethodBase.objects.create(
            name=method['name'],
            inputDataType=method['input_data_type'],
            outputDataType=method['output_data_type'],
            algorithm=method['algorithm'],
            implements=metric
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dqmodel', '0010_load_default_metrics'),
    ]

    operations = [
        migrations.RunPython(load_default_methods),
    ]
