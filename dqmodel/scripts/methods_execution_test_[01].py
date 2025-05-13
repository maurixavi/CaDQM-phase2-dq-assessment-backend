import psycopg2
import json
from typing import Dict, List, Union
import sys
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

def get_connection_params():
    return {
        'dbname': 'data_at_hand_v01',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432,
        'connect_timeout': 5
    }

def execute_dq_method(method_config: Dict) -> Dict:
    """
    Ejecuta un método de calidad de datos que devuelve un único dq_value
    
    Args:
        method_config: Diccionario con configuración del método DQ
    
    Returns:
        Diccionario con resultados de la evaluación DQ
    """
    params = get_connection_params()
    result = {
        "status": "success",
        "method": method_config["name"],
        "dimension": method_config["dimension"],
        "factor": method_config["factor"],
        "metric": method_config["metric"],
        "dq_value": None,
        "result_interpretation": "",
        "query_used": ""
    }
    
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        # Construir consulta
        query = method_config["algorithm"]
        query = query.replace('{table}', method_config["table"])
        for col in method_config.get("columns", []):
            query = query.replace(f'{{{col}}}', col)
        
        result["query_used"] = query
        
        cursor.execute(query)
        dq_value = cursor.fetchone()[0]
        
        # Validar rango del resultado
        min_val, max_val = method_config["result_domain"]
        if not (min_val <= float(dq_value) <= max_val):
            result["status"] = "warning"
            result["result_interpretation"] = f"Valor fuera del rango esperado [{min_val}, {max_val}]"

        result["dq_value"] = float(dq_value) if isinstance(dq_value, Decimal) else dq_value
        
        # Interpretación básica
        if not result["result_interpretation"]:
            if method_config["result_domain"] == [0, 1]:
                percentage = float(dq_value) * 100
                result["result_interpretation"] = f"{percentage:.2f}% de cumplimiento"
            else:
                result["result_interpretation"] = f"Valor obtenido: {dq_value}"
                
    except psycopg2.Error as e:
        result.update({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "dq_value": None
        })
    except Exception as e:
        result.update({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "dq_value": None
        })
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return result

# Métodos predefinidos para Amazon Books
DQ_METHODS = [
    {
        "name": "Completitud de Títulos",
        "description": "Porcentaje de libros con título no nulo",
        "dimension": "Completeness",
        "factor": "Density",
        "metric": "Null Value Percentage",
        "table": "books_data",
        "columns": ["title"],
        "algorithm": """
            SELECT 1 - (COUNT(*) FILTER (WHERE title IS NULL) * 1.0 / COUNT(*)) 
            FROM {table}
        """,
        "result_domain": [0, 1]
    },
    {
        "name": "Exactitud de Ratings",
        "description": "Porcentaje de ratings dentro del rango válido (1-5)",
        "dimension": "Accuracy",
        "factor": "Domain Integrity",
        "metric": "Range Conformance Ratio",
        "table": "books_rating",
        "columns": ["review_score"],
        "algorithm": """
            SELECT COUNT(*) FILTER (WHERE review_score BETWEEN 1 AND 5) * 1.0 / COUNT(*)
            FROM {table}
        """,
        "result_domain": [0, 1]
    },
    {
        "name": "Consistencia de Precios",
        "description": "Porcentaje de precios positivos",
        "dimension": "Consistency",
        "factor": "Domain Integrity",
        "metric": "Range Conformance Ratio",
        "table": "books_rating",
        "columns": ["price"],
        "algorithm": """
            SELECT COUNT(*) FILTER (WHERE price >= 0) * 1.0 / COUNT(*)
            FROM {table}
        """,
        "result_domain": [0, 1]
    },
    {
        "name": "Unicidad de Reviews",
        "description": "Porcentaje de reviews únicas por usuario-libro",
        "dimension": "Uniqueness",
        "factor": "No-duplication",
        "metric": "Unique Entry Ratio",
        "table": "books_rating",
        "columns": ["user_id", "title"],
        "algorithm": """
            WITH duplicates AS (
                SELECT user_id, title, COUNT(*) as cnt
                FROM books_rating
                GROUP BY user_id, title
                HAVING COUNT(*) > 1
            )
            SELECT 1 - (COALESCE(SUM(cnt), 0) * 1.0 / (SELECT COUNT(*) FROM books_rating))
            FROM duplicates
        """,
        "result_domain": [0, 1]
    },
    {
        "name": "Actualidad de Reviews",
        "description": "Porcentaje de reviews en el último año",
        "dimension": "Freshness",
        "factor": "Currency",
        "metric": "Data Age",
        "table": "books_rating",
        "columns": ["review_time"],
        "algorithm": """
            SELECT COUNT(*) FILTER (
                WHERE to_timestamp(review_time) > CURRENT_DATE - INTERVAL '1 year'
            ) * 1.0 / COUNT(*)
            FROM books_rating
        """,
        "result_domain": [0, 1]
    }
]

def main():
    """Función principal para ejecutar todos los métodos DQ"""
    print("Ejecutando métricas de calidad de datos...\n")
    
    results = []
    for method in DQ_METHODS:
        result = execute_dq_method(method)
        results.append(result)
        print(f"Método: {result['method']}")
        print(f"Dimensión: {result['dimension']} > {result['factor']} > {result['metric']}")
        if result['status'] == 'success':
            print(f"Resultado: {result['dq_value']} | {result['result_interpretation']}")
        else:
            print(f"Error: {result['error_message']}")
        print("----------------------------------------")
    
    # Exportar resultados completos
    with open("dq_results.json", "w") as f:
        json.dump(results, f, indent=2, cls=DecimalEncoder)
    
    print("\nResultados guardados en dq_results.json")

if __name__ == "__main__":
    main()