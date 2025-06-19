from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configurar el cliente de Groq
#groq_api_key = "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"
#model = "llama3-8b-8192"
#model = "llama3-8b-8192"

# Configuración de Groq
GROQ_API_KEY = "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"
#MODEL_NAME = "llama-3.3-70b-versatile"
MODEL_NAME = "llama-3.1-8b-instant" 
#MODEL_NAME = "llama3-8b-8192"
#MODEL_NAME = "llama3-70b-8192"
#MODEL_NAME = "deepseek-r1-distill-llama-70b"

TEMPERATURE = 0.3
# Cliente LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE
)



prompt_template_complex = """
Please generate a data quality method based on the following metric. 
Return ONLY a valid JSON object without any additional text or explanation.

Input Metric:
- Name: {name}
- Purpose: {purpose}
- Granularity: {granularity}
- Result Domain: {resultDomain}

The name of the method should reflect the nature of the metric, based on its "purpose" or "granularity". For example, if the metric's purpose is to detect duplicates, the name could be something like "detectDuplicateEntries".

DQ Metric: It is an instrument to measure a certain DQ factor. For example, the ratio of system data that match real-world data is a metric for the factor "semantic accuracy". Metrics have an associated granularity (e.g. in the relational model, it could be table, attribute, tuple or value) and a result domain (e.g. Boolean or [0,1]). Types of parameters can also be specified (e.g. a consistency metric, checking the satisfaction of a functional dependency, should take a dependency as input).

DQ Method: It is a process that implements a DQ metric. In this case, input and output data types can also be specified. There might be several DQ methods to implement the same DQ metric.

The "algorithm" field must be an appropriate SQL query that matches the purpose of the metric. For example, if the metric is related to detecting duplicates, the SQL query should find duplicate entries.

The response must be a single JSON object with this exact structure:
{
    "name": "generated method name",
    "inputDataType": "appropriate input type",
    "outputDataType": "appropriate output type",
    "algorithm": "SQL query for the metric",
    "implements": {metric_id}
}
"""

prompt_template = """
Generate a data quality method based on the following metric. A data quality method is a process that implements a certain data quality metric.
Return ONLY a valid JSON object without any additional text or explanation.

Input Metric:
- Name: {name}
- Purpose: {purpose}
- Granularity: {granularity}
- Result Domain: {resultDomain}

The name of the method should reflect the nature of the metric, based on its purpose or granularity. For example, if the metric's purpose is to detect duplicates, the name could be something like detectDuplicateEntries.

The algorithm field must be an appropriate SQL query that matches the purpose of the metric. For example, if the metric is related to detecting duplicates, the SQL query should find duplicate entries.

The response must be a single JSON object with this exact structure:
{{
    "name": "generated method name",
    "inputDataType": "appropriate input type",
    "outputDataType": "appropriate output type",
    "algorithm": "SQL query for the metric",
    "implements": {metric_id}
}}

For the table and column generic names, please use table1, column1.
"""

prompt_template_simple = """
Please generate a data quality method based on the following metric. 
Return ONLY a valid JSON object without any additional text or explanation.

Input Metric:
- Name: {name}
- Purpose: {purpose}
- Granularity: {granularity}
- Result Domain: {resultDomain}

The response must be a single JSON object with this exact structure:
{{
    "name": "generated method name",
    "inputDataType": "appropriate input type",
    "outputDataType": "appropriate output type",
    "algorithm": "SQL query for the metric",
    "implements": {metric_id}
}}
"""

def generate_ai_suggestion_withoutokensusage(dq_metric: dict) -> dict:
    """
    Generate a suggestion for a data quality method based on a DQMetric.
    """
    try:
        # Preparar el prompt
        formatted_prompt = prompt_template.format(
            name=dq_metric["name"],
            purpose=dq_metric["purpose"],
            granularity=dq_metric["granularity"],
            resultDomain=dq_metric["resultDomain"],
            metric_id=dq_metric["id"]
        )
        
        logger.debug(f"Formatted prompt: {formatted_prompt}")
        
        # Crear mensaje para el modelo
        message = HumanMessage(content=formatted_prompt)
        
        # Invocar el modelo
        response = llm.invoke([message])
        
        # Extraer y loggear la respuesta raw
        raw_content = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"Raw model response: {raw_content}")
        
        # Limpiar la respuesta
        cleaned_content = raw_content.strip()
        # Si la respuesta está envuelta en backticks, los removemos
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[:-3]
            
        cleaned_content = cleaned_content.strip()
        logger.debug(f"Cleaned content: {cleaned_content}")
        
        try:
            # Intentar parsear el JSON
            response_data = json.loads(cleaned_content)
            
            # Verificar campos requeridos
            required_fields = ["name", "inputDataType", "outputDataType", "algorithm"]
            if not all(field in response_data for field in required_fields):
                logger.error(f"Missing required fields. Got: {response_data.keys()}")
                return {
                    "error": "Missing required fields in model response",
                    "implements": dq_metric["id"]
                }
            
            # Asegurar que implements está presente y correcto
            response_data["implements"] = dq_metric["id"]
            
            return response_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Failed to parse content: {cleaned_content}")
            return {
                "error": f"Could not parse model response as JSON: {str(e)}",
                "implements": dq_metric["id"]
            }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "error": f"Error generating suggestion: {str(e)}",
            "implements": dq_metric["id"]
        }
    
 

def calculate_token_cost(model_name, input_tokens, output_tokens):
    model_name = model_name.lower()

    match model_name:
        case "llama-3.3-70b-versatile" | "llama3-70b-8192":
            input_price = 0.59 / 1_000_000
            output_price = 0.79 / 1_000_000

        case "llama-3.1-8b-instant" | "llama3-8b-8192":
            input_price = 0.05 / 1_000_000
            output_price = 0.08 / 1_000_000

        case _:
            raise ValueError(f"Modelo no reconocido para cálculo de costos: {model_name}")

    input_cost = input_tokens * input_price
    output_cost = output_tokens * output_price
    total_cost = input_cost + output_cost

    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6)
    }


def generate_ai_suggestion(dq_metric: dict) -> dict:
    """
    Generate a suggestion for a data quality method based on a DQMetric.
    Returns dict with method details and token usage information.
    """
    try:
        # Prepare prompt
        formatted_prompt = prompt_template.format(
            name=dq_metric["name"],
            purpose=dq_metric["purpose"],
            granularity=dq_metric["granularity"],
            resultDomain=dq_metric["resultDomain"],
            metric_id=dq_metric["id"]
        )
        
        logger.debug(f"Formatted prompt: {formatted_prompt}")
        
        # Create message and invoke model
        message = HumanMessage(content=formatted_prompt)
        response = llm.invoke([message])
        
        # Extract token usage metadata
        token_usage = response.response_metadata.get('token_usage', {})
        usage_metadata = getattr(response, 'usage_metadata', {})
        
        tokens_info = {
            "input_tokens": usage_metadata.get('input_tokens', token_usage.get('prompt_tokens', 0)),
            "output_tokens": usage_metadata.get('output_tokens', token_usage.get('completion_tokens', 0)),
            "total_tokens": usage_metadata.get('total_tokens', token_usage.get('total_tokens', 0))
        }
        
        # Clean response content
        raw_content = response.content
        cleaned_content = raw_content.strip()
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()
        
        # Parse JSON response
        response_data = json.loads(cleaned_content)
        
        # Validate required fields
        required_fields = ["name", "inputDataType", "outputDataType", "algorithm"]
        if not all(field in response_data for field in required_fields):
            raise ValueError(f"Missing required fields. Got: {response_data.keys()}")
        
        # Add metadata (sin cost info)
        response_data.update({
            "implements": dq_metric["id"],
            "token_usage": tokens_info
        })
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error generating suggestion: {str(e)}", exc_info=True)
        return {
            "error": f"Error generating suggestion: {str(e)}",
            "implements": dq_metric["id"]
        }

TEST_METRICS_2 = [
    {
        "id": 60,
        "name": "ValidScoreRange",
        "purpose": "Check if each review score is within expected range (1-5)",
        "granularity": "row",
        "resultDomain": "boolean"
    },
    {
        "id": 61,
        "name": "ValidScoreRange",
        "purpose": "Check if each review score is within expected range (1-5)",
        "granularity": "row",
        "resultDomain": "{0,1}"
    }
]

TEST_METRICS3 = [
    {
        "id": 502,
        "name": "TopRatedPremiumBooksRatio",
        "purpose": "Calculate the percentage of books with price greater than or equal to $100 and rating greater than or equal to 4",
        "granularity": "table",
        "resultDomain": "[0,1]"
    }
]

TEST_METRICS4 = [
    {
    "id": 504,
    "name": "HighlyRatedPopularBooksRatio",
    "purpose": "Calculate the percentage of books with more than 50 ratings and an average review score of at least 4.5",
    "granularity": "table",
    "resultDomain": "[0,1]",
    }
]

TEST_METRICS = [
    {
        "id": 601,
        "name": "SecureURLsRatio",
        "purpose": "Calculate the proportion of secure URLs (starting with 'https://') within a URL-type column",
        "granularity": "column",
        "resultDomain": "[0,1]"
    },
    {
        "id": 602,
        "name": "SecureURLsRatio",
        "purpose": "Measure the ratio of HTTPS links to total links in a column.",
        "granularity": "column",
        "resultDomain": "[0,1]"
    }
]





def main():
    # Casos de prueba
    test_metrics = TEST_METRICS

    # Initialize totals
    total_stats = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost_usd": 0.0,
        "method_count": 0
    }

    # Estructura para guardar todos los resultados
    output_data = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "model_used": "llama-3.3-70b-versatile",
            "temperature": TEMPERATURE,
            "total_metrics": len(test_metrics)
        },
        "results": []
    }

    print("=== Iniciando pruebas del generador de métodos DQ ===\n")
    
    for metric in test_metrics:
        metric_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost_usd": 0.0,
            "method_count": 0
        }
        
        metric_results = {
            "metric_id": metric["id"],
            "metric_name": metric["name"],
            "methods": [],
            "unique_methods": [],
            "token_usage": {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_usd": 0.0
            }
        }
        
        print(f"\n{'='*50}")
        print(f"Metric: {metric['name']} (ID: {metric['id']})")
        
        # 10 iteraciones por métrica
        for i in range(1, 11):
            iteration_result = {
                "iteration": i,
                "success": False
            }
            
            print(f"\n🌀 Iteración {i}:")
            result = generate_ai_suggestion(metric)
            
            if 'error' in result:
                iteration_result["error"] = result["error"]
                print(f"❌ Error: {result['error']}")
            else:
                # Calculate cost for this iteration
                cost_info = calculate_token_cost(
                    model_name="llama-3.3-70b-versatile",
                    input_tokens=result["token_usage"]["input_tokens"],
                    output_tokens=result["token_usage"]["output_tokens"]
                )
                
                # Add token and cost info to iteration result
                iteration_result.update({
                    "success": True,
                    "name": result["name"],
                    "inputDataType": result["inputDataType"],
                    "outputDataType": result["outputDataType"],
                    "algorithm": result["algorithm"],
                    "implements": result["implements"],
                    "token_usage": result["token_usage"],
                    "cost": cost_info  # Cost calculated in main
                })
                
                # Update metric-level totals
                metric_stats["input_tokens"] += result["token_usage"]["input_tokens"]
                metric_stats["output_tokens"] += result["token_usage"]["output_tokens"]
                metric_stats["total_cost_usd"] += cost_info["total_cost_usd"]
                metric_stats["method_count"] += 1
                
                # Update global totals
                total_stats["input_tokens"] += result["token_usage"]["input_tokens"]
                total_stats["output_tokens"] += result["token_usage"]["output_tokens"]
                total_stats["total_cost_usd"] += cost_info["total_cost_usd"]
                total_stats["method_count"] += 1
                
                print(f"🔹 Nombre: {result['name']}")
                print(f"🔸 SQL:\n{result['algorithm']}")
                print(f"🪙 Tokens: {result['token_usage']['input_tokens']} in, {result['token_usage']['output_tokens']} out")
                print(f"💵 Costo: ${cost_info['total_cost_usd']:.6f}\n")
            
            metric_results["methods"].append(iteration_result)
        
        # Update metric results with calculated totals
        metric_results["token_usage"] = {
            "total_input_tokens": metric_stats["input_tokens"],
            "total_output_tokens": metric_stats["output_tokens"],
            "total_cost_usd": round(metric_stats["total_cost_usd"], 6)
        }
        
        # Análisis de métodos únicos
        if metric_results["methods"]:
            successful_methods = [m for m in metric_results["methods"] if m["success"]]
            
            unique_methods = []
            seen_methods = []
            
            for method in successful_methods:
                method_signature = {k: v for k, v in method.items() 
                                  if k not in ['iteration', 'success', 'token_usage', 'cost']}
                
                if method_signature not in seen_methods:
                    seen_methods.append(method_signature)
                    unique_methods.append({
                        **method_signature,
                        "count": 1,
                        "iterations": [method["iteration"]],
                        "avg_tokens": {
                            "input_tokens": method["token_usage"]["input_tokens"],
                            "output_tokens": method["token_usage"]["output_tokens"]
                        },
                        "avg_cost": method["cost"]
                    })
                else:
                    for um in unique_methods:
                        um_signature = {k: v for k, v in um.items() 
                                      if k not in ['count', 'iterations', 'avg_tokens', 'avg_cost']}
                        if um_signature == method_signature:
                            um["count"] += 1
                            um["iterations"].append(method["iteration"])
                            # Update average token usage and cost
                            um["avg_tokens"]["input_tokens"] = (um["avg_tokens"]["input_tokens"] + method["token_usage"]["input_tokens"]) / 2
                            um["avg_tokens"]["output_tokens"] = (um["avg_tokens"]["output_tokens"] + method["token_usage"]["output_tokens"]) / 2
                            um["avg_cost"]["total_cost_usd"] = (um["avg_cost"]["total_cost_usd"] + method["cost"]["total_cost_usd"]) / 2
                            break
            
            metric_results["unique_methods"] = unique_methods
            
            metric_results["analysis"] = {
                "total_methods_generated": len(successful_methods),
                "unique_methods_count": len(unique_methods),
                "most_common_method": max(unique_methods, key=lambda x: x["count"]) if unique_methods else None,
                "input_data_types": list(set(m["inputDataType"] for m in successful_methods)),
                "output_data_types": list(set(m["outputDataType"] for m in successful_methods))
            }
        
        output_data["results"].append(metric_results)
    
    # Add global totals to metadata
    output_data["metadata"].update({
        "total_input_tokens": total_stats["input_tokens"],
        "total_output_tokens": total_stats["output_tokens"],
        "total_cost_usd": round(total_stats["total_cost_usd"], 6),
        "avg_cost_per_method": round(total_stats["total_cost_usd"] / total_stats["method_count"], 6) if total_stats["method_count"] > 0 else 0
    })
    
    # Guardar resultados en JSON
    output_file = f"ai_eval_methods/executions/dq_methods_test_{datetime.now().strftime('%Y%m%d_%H%M')}_{TEMPERATURE}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 Resultados guardados en {output_file}")
    print(f"📊 Totales globales:")
    print(f"  Total tokens entrada: {total_stats['input_tokens']}")
    print(f"  Total tokens salida: {total_stats['output_tokens']}")
    print(f"  Costo total: ${total_stats['total_cost_usd']:.6f}")
    print(f"  Costo promedio por método: ${output_data['metadata']['avg_cost_per_method']:.6f}")
  
    
def main0():
    # Casos de prueba
    test_metrics = [
        {
            "id": 1,
            "name": "NullValueRatio",
            "purpose": "Medir el porcentaje de valores nulos en una columna",
            "granularity": "attribute",
            "resultDomain": "[0,1]"
        },
        {
            "id": 2,
            "name": "DuplicateDetection",
            "purpose": "Identificar registros duplicados basados en una clave",
            "granularity": "tuple",
            "resultDomain": "boolean"
        },
        {
            "id": 3,
            "name": "EmailFormatCompliance",
            "purpose": "Verificar si los valores siguen formato de email válido",
            "granularity": "attribute",
            "resultDomain": "boolean"
        },
        {
            "id": 4,
            "name": "ValueRangeCheck",
            "purpose": "Validar que los valores estén dentro de un rango numérico",
            "granularity": "attribute",
            "resultDomain": "boolean"
        }
    ]

    print("=== Iniciando pruebas del generador de métodos DQ ===\n")
    
    for metric in test_metrics:
        print(f"\n🔹 Métrica bajo prueba: {metric['name']}")
        print(f"Propósito: {metric['purpose']}")
        print(f"Granularidad: {metric['granularity']}")
        print(f"Dominio resultado: {metric['resultDomain']}\n")
        
        # Generar sugerencia
        result = generate_ai_suggestion(metric)
        
        if 'error' in result:
            print(f"❌ Error en generación: {result['error']}")
            continue
            
        # Análisis de resultados
        print("✅ Método generado:")
        print(f"Nombre: {result['name']}")
        print(f"Tipo entrada: {result['inputDataType']}")
        print(f"Tipo salida: {result['outputDataType']}")
        print(f"\nSQL generado:\n{result['algorithm']}\n")
        
        # Validaciones básicas
        print("🔍 Análisis:")
        
        # 1. Coherencia nombre-propósito
        if metric['purpose'].lower() in result['name'].lower():
            print("✔ Nombre refleja el propósito de la métrica")
        else:
            print("⚠ Nombre podría no reflejar completamente el propósito")
        
        # 2. Coherencia SQL-tipo salida
        if "SELECT" in result['algorithm']:
            if "boolean" in result['outputDataType'].lower() and "AS is_valid" in result['algorithm'].lower():
                print("✔ SQL adecuado para validación booleana")
            elif "float" in result['outputDataType'].lower() and ("COUNT(" in result['algorithm'] or "SUM(" in result['algorithm']):
                print("✔ SQL adecuado para cálculo numérico")
            else:
                print("⚠ Revisar correspondencia entre SQL y tipo de salida")
        
        # 3. Placeholders genéricos
        if "table1" in result['algorithm'] and "column1" in result['algorithm']:
            print("✔ Usa placeholders genéricos (table1/column1)")
        else:
            print("⚠ Podría contener nombres específicos no deseados")


test_metrics_en = [
        {
            "id": 1,
            "name": "NullValueRatio",
            "purpose": "Measure percentage of null values in a column",
            "granularity": "attribute",
            "resultDomain": "[0,1]"
        },
        {
            "id": 2,
            "name": "DuplicateDetection",
            "purpose": "Identify duplicate records based on a key",
            "granularity": "tuple",
            "resultDomain": "boolean"
        },
        {
            "id": 3,
            "name": "EmailFormatCompliance",
            "purpose": "Verify if values follow valid email format",
            "granularity": "attribute",
            "resultDomain": "boolean"
        },
        {
            "id": 4,
            "name": "ValueRangeCheck",
            "purpose": "Validate values fall within numerical range",
            "granularity": "attribute",
            "resultDomain": "boolean"
        }
    ]

test_metrics_es = [
        {
            "id": 1,
            "name": "NullValueRatio",
            "purpose": "Medir el porcentaje de valores nulos en una columna",
            "granularity": "column",
            "resultDomain": "[0,1]"
        },
        {
            "id": 2,
            "name": "DuplicateDetection",
            "purpose": "Identificar registros duplicados basados en una clave",
            "granularity": "tuple",
            "resultDomain": "boolean"
        },
        {
            "id": 3,
            "name": "EmailFormatCompliance",
            "purpose": "Verificar si los valores siguen formato de email válido",
            "granularity": "attribute",
            "resultDomain": "boolean"
        }
    ]

TEST_METRICS_inf = [
        {
            "id": 1,
            "name": "NullValueRatio",
            "purpose": "Measure percentage of null values in a column",
            "granularity": "column",
            "resultDomain": "[0,1]"
        },
        {
            "id": 2,
            "name": "DuplicateTuples",
            "purpose": "Identify duplicate records in a table",
            "granularity": "tuple",
            "resultDomain": "boolean"
        },
        {
            "id": 3,
            "name": "CellFormatValidation",
            "purpose": "Verify individual cell format compliance",
            "granularity": "cell",
            "resultDomain": "boolean"
        },
        {
            "id": 4,
            "name": "ValueRangeCompliance",
            "purpose": "Check numeric values fall within specified range",
            "granularity": "column",
            "resultDomain": "[0,1]"
        }
    ]


def main0():
    # Casos de prueba
    test_metrics = TEST_METRICS

    # Estructura para guardar todos los resultados
    output_data = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "model_used": "llama-3.3-70b-versatile",
            "temperature": TEMPERATURE,
            "total_metrics": len(test_metrics)
        },
        "results": []
    }

    print("=== Iniciando pruebas del generador de métodos DQ ===\n")
    
    for metric in test_metrics:
        metric_results = {
            "metric_id": metric["id"],
            "metric_name": metric["name"],
            "methods": [],
            "unique_methods": []
        }
        
        print(f"\n{'='*50}")
        print(f"Metric: {metric['name']} (ID: {metric['id']})")
        
        # 5 iteraciones por métrica
        for i in range(1, 11):
            iteration_result = {
                "iteration": i,
                "success": False
            }
            
            print(f"\n🌀 Iteración {i}:")
            result = generate_ai_suggestion(metric)
            
            if 'error' in result:
                iteration_result["error"] = result["error"]
                print(f"❌ Error: {result['error']}")
            else:
                iteration_result.update({
                    "success": True,
                    "name": result["name"],
                    "inputDataType": result["inputDataType"],
                    "outputDataType": result["outputDataType"],
                    "algorithm": result["algorithm"],
                    "implements": result["implements"]
                })
                
                print(f"🔹 Nombre: {result['name']}")
                print(f"🔸 SQL:\n{result['algorithm']}\n")
            
            metric_results["methods"].append(iteration_result)
        
        # Análisis de métodos únicos
        if metric_results["methods"]:
            # Get all successful methods
            successful_methods = [m for m in metric_results["methods"] if m["success"]]
            
            # Find unique methods by comparing all fields except iteration
            unique_methods = []
            seen_methods = []
            
            for method in successful_methods:
                # Create a comparable dict without iteration number
                method_signature = {k: v for k, v in method.items() 
                                  if k not in ['iteration', 'success']}
                
                if method_signature not in seen_methods:
                    seen_methods.append(method_signature)
                    unique_methods.append({
                        **method_signature,
                        "count": 1,
                        "iterations": [method["iteration"]]
                    })
                else:
                    # Find and update existing unique method
                    for um in unique_methods:
                        um_signature = {k: v for k, v in um.items() 
                                      if k not in ['count', 'iterations']}
                        if um_signature == method_signature:
                            um["count"] += 1
                            um["iterations"].append(method["iteration"])
                            break
            
            metric_results["unique_methods"] = unique_methods
            
            # Análisis de variabilidad
            metric_results["analysis"] = {
                "total_methods_generated": len(successful_methods),
                "unique_methods_count": len(unique_methods),
                "most_common_method": max(unique_methods, key=lambda x: x["count"]) if unique_methods else None,
                "input_data_types": list(set(m["inputDataType"] for m in successful_methods)),
                "output_data_types": list(set(m["outputDataType"] for m in successful_methods))
            }
        
        output_data["results"].append(metric_results)
    
    # Guardar resultados en JSON
    output_file = f"ai_eval_methods/executions/dq_methods_test_{datetime.now().strftime('%Y%m%d_%H%M')}_{TEMPERATURE}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 Resultados guardados en {output_file}")
    
    

def main2():
    # Casos de prueba
    test_metrics = TEST_METRICS

    print("=== Iniciando pruebas del generador de métodos DQ ===\n")
    print("🔻 Se ejecutarán 5 iteraciones por métrica para evaluar consistencia\n")
    
    for metric in test_metrics:
        print(f"\n{'='*50}")
        print(f"Metric: {metric['name']} (ID: {metric['id']})")
        print(f"Purpose: {metric['purpose']}")
        print(f"Granularity: {metric['granularity']}")
        print(f"Result Domain: {metric['resultDomain']}")
        print(f"{'='*50}\n")
        
        results = []
        
        # 5 iteraciones por métrica
        for i in range(1, 6):
            print(f"\n🌀 Iteración {i}:")
            result = generate_ai_suggestion(metric)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
                
            results.append(result)
            
            print(f"🔹 Nombre: {result['name']}")
            print(f"🔸 SQL:\n{result['algorithm']}\n")
        
        # Análisis comparativo
        if results:
            print("\n📌 Análisis comparativo:")
            
            # 1. Variabilidad de nombres
            unique_names = len(set(r['name'] for r in results))
            print(f"- Variación en nombres: {unique_names} nombres distintos en {len(results)} iteraciones")
            
            # 2. Estructura SQL comparada
            first_sql_structure = results[0]['algorithm'].split()[0].lower()
            consistent_sql = all(r['algorithm'].split()[0].lower() == first_sql_structure for r in results)
            print(f"- Consistencia en estructura SQL: {'✅' if consistent_sql else '⚠'} ({'similar' if consistent_sql else 'variable'} entre iteraciones)")
            
            # 3. Tipos de datos
            input_types = set(r['inputDataType'] for r in results)
            output_types = set(r['outputDataType'] for r in results)
            print(f"- Tipos entrada: {input_types}")
            print(f"- Tipos salida: {output_types}")
            
            # 4. Ejemplo de diferencias
            if unique_names > 1:
                print("\n🔎 Diferencias encontradas en nombres:")
                for i, r in enumerate(results, 1):
                    print(f"Iteración {i}: {r['name']}")
            

import json
from datetime import datetime

def main1():
    # Casos de prueba
    test_metrics = TEST_METRICS

    # Estructura para guardar todos los resultados
    output_data = {
        "metadata": {
            "test_date": datetime.now().isoformat(),
            "model_used": "llama-3.3-70b-versatile",
            "total_metrics": len(test_metrics)
        },
        "results": []
    }

    print("=== Iniciando pruebas del generador de métodos DQ ===\n")
    
    for metric in test_metrics:
        metric_results = {
            "metric_id": metric["id"],
            "metric_name": metric["name"],
            "methods": []
        }
        
        print(f"\n{'='*50}")
        print(f"Metric: {metric['name']} (ID: {metric['id']})")
        
        # 5 iteraciones por métrica
        for i in range(1, 11):
            iteration_result = {
                "iteration": i,
                "success": False
            }
            
            print(f"\n🌀 Iteración {i}:")
            result = generate_ai_suggestion(metric)
            
            if 'error' in result:
                iteration_result["error"] = result["error"]
                print(f"❌ Error: {result['error']}")
            else:
                iteration_result.update({
                    "success": True,
                    "name": result["name"],
                    "inputDataType": result["inputDataType"],
                    "outputDataType": result["outputDataType"],
                    "algorithm": result["algorithm"],
                    "implements": result["implements"]
                })
                
                print(f"🔹 Nombre: {result['name']}")
                print(f"🔸 SQL:\n{result['algorithm']}\n")
            
            metric_results["methods"].append(iteration_result)
        
        # Análisis de variabilidad
        successful_runs = [r for r in metric_results["methods"] if r["success"]]
        if successful_runs:
            unique_names = len(set(r["name"] for r in successful_runs))
            sql_structures = [r["algorithm"].split()[0].lower() for r in successful_runs]
            
            metric_results["analysis"] = {
                "unique_names_count": unique_names,
                "sql_consistency": all(s == sql_structures[0] for s in sql_structures),
                "input_data_types": list(set(r["inputDataType"] for r in successful_runs)),
                "output_data_types": list(set(r["outputDataType"] for r in successful_runs))
            }
        
        output_data["results"].append(metric_results)
    
    # Guardar resultados en JSON
    output_file = f"ai_eval_methods/executions/dq_methods_test_{datetime.now().strftime('%Y%m%d_%H%M')}_{TEMPERATURE}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 Resultados guardados en {output_file}")




if __name__ == "__main__":
    main()
    
