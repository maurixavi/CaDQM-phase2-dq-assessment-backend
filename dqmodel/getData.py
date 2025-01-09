import re

def read_markdown(md_file_path):
    with open(md_file_path, 'r') as file:
        markdown_text = file.read()
    return markdown_text

def extract_dimensions(markdown_text):
    # Expresion regular para encontrar las dimensiones y sus descripciones
    dimension_pattern = re.compile(r"## DQ Dimension: (.+?)\n\*\*Semantic:\*\* (.+?)(?=\n##|$)", re.DOTALL)
    dimensions_matches = dimension_pattern.findall(markdown_text)

    dimensions_base = []
    for dim_name, dim_semantic in dimensions_matches:
        dimensions_base.append({
            "name": f"{dim_name.strip()} (preset)",
            "semantic": dim_semantic.strip()
        })

    return dimensions_base


def extract_factors(markdown_text):
    # Expresion regular para encontrar los factores, sus descripciones y dimension
    factor_pattern = re.compile(r"### DQ Factor: (.+?)\n\*\*Semantic:\*\* (.+?)\n\*\*Facet of \(DQ Dimension\):\*\* (.+?)(?=\n###|$)", re.DOTALL)
    factors_matches = factor_pattern.findall(markdown_text)

    factors_base = []
    for factor_name, factor_semantic, dimension_name in factors_matches:
        factors_base.append({
            "name": f"{factor_name.strip()} (preset)",
            "semantic": factor_semantic.strip(),
            "dimension": f"{dimension_name.strip()} (preset)"
        })

    return factors_base


def extract_metrics(markdown_text):
    # Expresion regular para encontrar las metricas y sus atributos
    metric_pattern = re.compile(r"#### DQ Metric: (.+?)\n\*\*Purpose:\*\* (.+?)\n\*\*Granularity:\*\* (.+?)\n\*\*Result Domain:\*\* (.+?)\n\*\*Measures \(DQ Factor\):\*\* (.+?)(?=\n####|$)", re.DOTALL)
    metrics_matches = metric_pattern.findall(markdown_text)

    metrics_base = []
    for metric_name, purpose, granularity, result_domain, factor_name in metrics_matches:
        # Limpiar los valores de las metricas y asignar el formato
        metrics_base.append({
            "name": metric_name.strip(),
            "purpose": purpose.strip(),
            "granularity": granularity.strip(),
            "result_domain": result_domain.strip(),
            "factor": factor_name.strip()
        })

    return metrics_base
  
# Función para extraer métodos
def extract_methods(markdown_text):
    # Expresion regular ajustada para evitar capturar texto extra después de la metrica
    method_pattern = re.compile(r"##### DQ Method: (.+?)\n\*\*Name:\*\* (.+?)\n\*\*Input data type:\*\* (.+?)\n\*\*Output data type:\*\* (.+?)\n\*\*Algorithm:\*\*\s*```sql\n([\s\S]+?)\s*```.*?\n\*\*Implements \(DQ Metric\):\*\* (.+?)(?=\n#####|$)", re.DOTALL)
    methods_matches = method_pattern.findall(markdown_text)

    methods_base = []
    for method_name, name, input_data_type, output_data_type, algorithm, metric in methods_matches:
        # Limpiar los valores de los métodos y asignar el formato
        methods_base.append({
            "name": name.strip(),
            "input_data_type": input_data_type.strip(),
            "output_data_type": output_data_type.strip(),
            "algorithm": algorithm.strip(),
            "metric": metric.strip().split("\n")[0]  # Ajuste: toma solo la primera línea de la métrica
        })

    return methods_base


if __name__ == "__main__":
    # Ruta del archivo Markdown
    md_file_path = 'dqmodel_template_data.md'
    
    # Leer el archivo Markdown una vez
    markdown_text = read_markdown(md_file_path)
    
    # Obtener dimensiones, factores, métricas y métodos
    dimensions_base = extract_dimensions(markdown_text)
    factors_base = extract_factors(markdown_text)
    metrics_base = extract_metrics(markdown_text)
    methods_base = extract_methods(markdown_text)
    
    # Mostrar los resultados
    #print("dimensions_base =", dimensions_base)
    #print("factors_base =", factors_base)
    #print("metrics_base =", metrics_base)
    #print("methods_base =", methods_base)


