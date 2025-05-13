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
    """Ejecuta un método de calidad de datos con diferentes tipos de resultados"""
    params = get_connection_params()
    result = {
        "status": "success",
        "method": method_config["name"],
        "dimension": method_config["dimension"],
        "factor": method_config["factor"],
        "metric": method_config["metric"],
        "result_type": method_config["result_domain"]["type"],
        "results": None,
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
        
        # Procesar resultados según el tipo
        if method_config["result_domain"]["type"] == "boolean":
            # Para métodos que evalúan filas individualmente
            rows = cursor.fetchall()
            result["results"] = [{
                "row_id": idx + 1,
                "value": bool(row[0]),
                "condition_met": bool(row[0]) == method_config["result_domain"]["expected"]
            } for idx, row in enumerate(rows)]
            
            # Calcular porcentaje de cumplimiento
            total = len(result["results"])
            passed = sum(1 for r in result["results"] if r["condition_met"])
            result["summary"] = {
                "total_rows": total,
                "passed": passed,
                "failed": total - passed,
                "compliance_rate": passed / total if total > 0 else 0
            }
            
        elif method_config["result_domain"]["type"] == "percentage":
            # Métodos que devuelven un porcentaje [0, 1]
            dq_value = cursor.fetchone()[0]
            result["results"] = float(dq_value) if isinstance(dq_value, Decimal) else dq_value
            result["interpretation"] = f"{float(dq_value)*100:.2f}% de cumplimiento"
            
        elif method_config["result_domain"]["type"] == "count":
            # Métodos que devuelven conteos
            result["results"] = cursor.fetchone()[0]
            
        elif method_config["result_domain"]["type"] == "range":
            # Métodos con valores en un rango específico
            dq_value = cursor.fetchone()[0]
            result["results"] = float(dq_value) if isinstance(dq_value, Decimal) else dq_value
            min_val, max_val = method_config["result_domain"]["range"]
            if not (min_val <= float(dq_value) <= max_val):
                result["status"] = "warning"
                result["interpretation"] = f"Valor fuera del rango esperado [{min_val}, {max_val}]"
                
    except psycopg2.Error as e:
        result.update({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "results": None
        })
    except Exception as e:
        result.update({
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "results": None
        })
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return result

# Métodos predefinidos con diferentes tipos de resultados
DQ_METHODS = [
    # Método booleano (evalúa filas individualmente)
    {
        "name": "Validación Precios Positivos",
        "description": "Verifica que los primeros 15 precios sean positivos",
        "dimension": "Consistency",
        "factor": "Domain Integrity",
        "metric": "Value Validation",
        "table": "books_rating",
        "columns": ["price"],
        "algorithm": "SELECT price >= 0 FROM books_rating LIMIT 15",
        "result_domain": {
            "type": "boolean",
            "expected": True
        }
    },
    # Método de porcentaje [0, 1]
    {
        "name": "Completitud de Títulos",
        "description": "Porcentaje de libros con título no nulo",
        "dimension": "Completeness",
        "factor": "Density",
        "metric": "Null Value Percentage",
        "table": "books_data",
        "columns": ["title"],
        "algorithm": "SELECT 1 - (COUNT(*) FILTER (WHERE title IS NULL) * 1.0 / COUNT(*)) FROM books_data",
        "result_domain": {
            "type": "percentage",
            "range": [0, 1]
        }
    },
    # Método de conteo
    {
        "name": "Conteo de Reviews Recientes",
        "description": "Número de reviews en el último mes",
        "dimension": "Freshness",
        "factor": "Currency",
        "metric": "Recent Items Count",
        "table": "books_rating",
        "columns": ["review_time"],
        "algorithm": """
            SELECT COUNT(*) FROM books_rating 
            WHERE to_timestamp(review_time) > CURRENT_DATE - INTERVAL '1 month'
        """,
        "result_domain": {
            "type": "count"
        }
    },
    # Método con rango específico
    {
        "name": "Promedio de Ratings",
        "description": "Valor promedio de ratings (debe estar entre 2.5 y 4.5)",
        "dimension": "Accuracy",
        "factor": "Semantic Accuracy",
        "metric": "Average Value",
        "table": "books_rating",
        "columns": ["review_score"],
        "algorithm": "SELECT AVG(review_score) FROM books_rating",
        "result_domain": {
            "type": "range",
            "range": [2.5, 4.5]
        }
    }
]

def main():
    """Función principal para ejecutar todos los métodos DQ"""
    print("Ejecutando métricas de calidad de datos...\n")
    results = []
    
    for method in DQ_METHODS:
        result = execute_dq_method(method)
        results.append(result)
        print(f"\nMétodo: {result['method']}")
        print(f"Tipo: {result['result_type']}")
        
        if result['status'] == 'success':
            if result['result_type'] == 'boolean':
                print(f"Resumen: {result['summary']['passed']}/{result['summary']['total_rows']} cumplen")
                print(f"Tasa de cumplimiento: {result['summary']['compliance_rate']*100:.2f}%")
            elif 'interpretation' in result:
                print(result['interpretation'])
            print(f"Resultado: {result['results']}")
        else:
            print(f"Error: {result['error_message']}")
    
    # Exportar resultados
    with open("dq_results.json", "w") as f:
        json.dump(results, f, indent=2, cls=DecimalEncoder)
    print("\nResultados guardados en dq_results.json")

if __name__ == "__main__":
    main()