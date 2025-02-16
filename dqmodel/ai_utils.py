from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from .models import DQMetricBase, DQMethodBase
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configurar el cliente de Groq
groq_api_key = "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"
#model = "llama3-8b-8192"
model = "mixtral-8x7b-32768"

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name=model
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
Please generate a data quality method based on the following metric. A data quality method is a process that implements a certain data quality metric.
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

def generate_ai_suggestion(dq_metric: dict) -> dict:
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