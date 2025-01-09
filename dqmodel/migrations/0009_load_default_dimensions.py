from django.db import migrations

def load_default_dimensions_factors(apps, schema_editor):
    # Obtiene el modelo de las dimensiones desde el apps registry.
    DQDimensionBase = apps.get_model('dqmodel', 'DQDimensionBase')
    DQFactorBase = apps.get_model('dqmodel', 'DQFactorBase')
    
    # Crear dimensiones base
    dimensions_base = [
        {"name": "Accuracy (preset)", "semantic": "Indicates that the data is correct and precise."},
        {"name": "Completeness (preset)", "semantic": "Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making."},
        {"name": "Freshness (preset)", "semantic": "Refers to the recency and update status of the data, indicating whether the data is current and up-to-date."},
        {"name": "Consistency (preset)", "semantic": "Ensures that the data is coherent across different sources and over time, maintaining integrity and reliability."},
        {"name": "Uniqueness (preset)", "semantic": "Indicates that each data entry must be unique, with no duplicates present in the dataset."},
    ]
    
    # Crear las dimensiones
    for dim in dimensions_base:
        DQDimensionBase.objects.create(name=dim['name'], semantic=dim['semantic'])

    # Crear los factores asociados a cada dimensión
    factors_base = [
        {"name": "Semantic Accuracy (preset)", "semantic": "The data correctly represents entities or states of the real world.", "dimension": "Accuracy (preset)"},
        {"name": "Syntactic Accuracy (preset)", "semantic": "The data is free from syntactic errors.", "dimension": "Accuracy (preset)"},
        {"name": "Precision (preset)", "semantic": "The data has an adequate level of detail.", "dimension": "Accuracy (preset)"},
        {"name": "Density (preset)", "semantic": "The proportion of actual data entries compared to the total possible entries.", "dimension": "Completeness (preset)"},
        {"name": "Coverage (preset)", "semantic": "The extent to which the data covers the required scope or domain.", "dimension": "Completeness (preset)"},
        {"name": "Currency (preset)", "semantic": "Indicates how up-to-date the data is.", "dimension": "Freshness (preset)"},
        {"name": "Timeliness (preset)", "semantic": "The data is available when needed.", "dimension": "Freshness (preset)"},
        {"name": "Volatility (preset)", "semantic": "The rate at which the data changes over time.", "dimension": "Freshness (preset)"},
        {"name": "Domain Integrity (preset)", "semantic": "Ensures that the data values fall within a defined range or set of values.", "dimension": "Consistency (preset)"},
        {"name": "Intra-relationship Integrity (preset)", "semantic": "Ensures that data within a single dataset is consistent.", "dimension": "Consistency (preset)"},
        {"name": "Inter-relationship Integrity (preset)", "semantic": "Ensures that data across multiple datasets is consistent.", "dimension": "Consistency (preset)"},
        {"name": "No-duplication (preset)", "semantic": "Ensures that there are no duplicate entries in the dataset.", "dimension": "Uniqueness (preset)"},
        {"name": "No-contradiction (preset)", "semantic": "Ensures that there are no conflicting entries within the dataset.", "dimension": "Uniqueness (preset)"},
    ]


    
    # Crear los factores asociados a cada dimensión
    for factor in factors_base:
        # Buscar la dimensión correspondiente
        dimension = DQDimensionBase.objects.get(name=factor['dimension'])
        
        # Crear el factor y asociarlo a la dimensión mediante facetOf
        DQFactorBase.objects.create(
            name=factor['name'],
            semantic=factor['semantic'],
            facetOf=dimension
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dqmodel', '0006_dqmodeldimension_context_components'),
    ]

    operations = [
        migrations.RunPython(load_default_dimensions_factors),
    ]
