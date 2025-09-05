import re
from pathlib import Path
from typing import Dict, List

def read_markdown(md_path: str) -> str:
    """Lee el archivo Markdown y retorna su contenido como texto."""
    return Path(md_path).read_text(encoding='utf-8')

def normalize_sql_algorithm(sql_code):
    """
    Normaliza el código SQL para eliminar indentación y saltos de línea innecesarios
    Maneja múltiples casos borde
    """
    if not sql_code:
        return ""
    
    # Limpia el código SQL
    sql_code = sql_code.strip()
    
    # Remueve backticks y especificación de lenguaje
    if sql_code.startswith('```'):
        # Encuentra el final de los backticks
        end_index = sql_code.find('\n', 3) if '\n' in sql_code else len(sql_code)
        first_line = sql_code[3:end_index].strip()
        
        # Primera línea especifica el lenguaje (sql)
        if first_line and not first_line.startswith('SELECT') and not first_line.startswith('--'):
            sql_code = sql_code[end_index:].strip() if end_index < len(sql_code) else ""
        else:
            # Solo backticks sin especificación de lenguaje
            sql_code = sql_code[3:].strip()
    
    if sql_code.endswith('```'):
        sql_code = sql_code[:-3].strip()
    
    # Normaliza espacios y saltos de línea
    lines = []
    for line in sql_code.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):  # filtrar comentarios
            lines.append(line)
    
    # Para consultas simples, una línea; para complejas, comprime pero mantiene cierta legibilidad
    if len(lines) <= 3:
        normalized_sql = ' '.join(lines)
    else:
        # Une todo pero asegura espacios adecuados alrededor de operadores
        normalized_sql = ' '.join(lines)
        normalized_sql = re.sub(r'\s*([=+\-*/<>,;()])\s*', r' \1 ', normalized_sql)  # Espacios alrededor de operadores
        normalized_sql = re.sub(r'\s+', ' ', normalized_sql)  # Espacios múltiples a simples
    
    return normalized_sql.strip()

def extract_dimensions(markdown_text: str) -> List[Dict]:
    """Extrae dimensiones del texto Markdown."""
    pattern = re.compile(
        r"## DQ Dimension: (.+?)\n\*\*Semantic:\*\* (.+?)(?=\n##|$)", 
        re.DOTALL
    )
    return [
        {"name": name.strip(), "semantic": semantic.strip()}
        for name, semantic in pattern.findall(markdown_text)
    ]

def extract_factors(markdown_text: str) -> List[Dict]:
    """Extrae factores de calidad del texto Markdown."""
    pattern = re.compile(
        r"### DQ Factor: (.+?)\n\*\*Semantic:\*\* (.+?)\n\*\*Facet of \(DQ Dimension\):\*\* (.+?)(?=\n###|$)",
        re.DOTALL
    )
    return [
        {
            "name": name.strip(),
            "semantic": semantic.strip(),
            "dimension": dimension.strip()
        }
        for name, semantic, dimension in pattern.findall(markdown_text)
    ]

def extract_metrics(markdown_text: str) -> List[Dict]:
    """Extrae métricas del texto Markdown."""
    pattern = re.compile(
        r"#### DQ Metric: (.+?)\n\*\*Purpose:\*\* (.+?)\n\*\*Granularity:\*\* (.+?)\n\*\*Result Domain:\*\* (.+?)\n\*\*Measures \(DQ Factor\):\*\* (.+?)(?=\n####|\n###|\n##|$)",
        re.DOTALL
    )
    return [
        {
            "name": name.strip(),
            "purpose": purpose.strip(),
            "granularity": granularity.strip(),
            "resultDomain": result_domain.strip(),
            "factor": factor.strip()
        }
        for name, purpose, granularity, result_domain, factor in pattern.findall(markdown_text)
    ]

def extract_methods(markdown_text: str) -> List[Dict]:
    """Extrae métodos del texto Markdown."""
    pattern = re.compile(r"##### DQ Method: (.+?)\n\*\*Input data type:\*\* (.+?)\n\*\*Output data type:\*\* (.+?)\n\*\*Algorithm:\*\*\s*```sql\n([\s\S]+?)\s*```.*?\n\*\*Implements \(DQ Metric\):\*\* (.+?)(?=\n#####|$)", re.DOTALL)
    
    return [
        {
            "name": name.strip(),
            "inputDataType": input_type.strip(),
            "outputDataType": output_type.strip(),
            "algorithm": normalize_sql_algorithm(algorithm),
            "metric": metric.strip().split("\n")[0]
        }
        for name, input_type, output_type, algorithm, metric in pattern.findall(markdown_text)
    ]

def parse_markdown(md_path: str) -> Dict[str, List[Dict]]:
    """Orquesta todo el parsing del archivo Markdown."""
    md_text = read_markdown(md_path)
    return {
        "dimensions": extract_dimensions(md_text),
        "factors": extract_factors(md_text),
        "metrics": extract_metrics(md_text),
        "methods": extract_methods(md_text)
    }