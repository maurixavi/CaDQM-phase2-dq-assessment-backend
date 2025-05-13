import re
from typing import List, Dict

def extract_dimensions(markdown_text: str) -> List[Dict]:
    pattern = re.compile(r"## DQ Dimension: (.+?)\n\*\*Semantic:\*\* (.+?)(?=\n##|$)", re.DOTALL)
    return [{"name": f"{m[0].strip()} (preset)", "semantic": m[1].strip()} for m in pattern.findall(markdown_text)]

def extract_factors(markdown_text: str) -> List[Dict]:
    pattern = re.compile(r"### DQ Factor: (.+?)\n\*\*Semantic:\*\* (.+?)\n\*\*Facet of \(DQ Dimension\):\*\* (.+?)(?=\n###|$)", re.DOTALL)
    return [{"name": f"{m[0].strip()} (preset)", "semantic": m[1].strip(), "dimension": f"{m[2].strip()} (preset)"} for m in pattern.findall(markdown_text)]

def extract_metrics(markdown_text: str) -> List[Dict]:
    pattern = re.compile(r"#### DQ Metric: (.+?)\n\*\*Purpose:\*\* (.+?)\n\*\*Granularity:\*\* (.+?)\n\*\*Result Domain:\*\* (.+?)\n\*\*Measures \(DQ Factor\):\*\* (.+?)(?=\n####|$)", re.DOTALL)
    return [{"name": m[0].strip(), "purpose": m[1].strip(), "granularity": m[2].strip(), "result_domain": m[3].strip(), "factor": f"{m[4].strip()} (preset)"} for m in pattern.findall(markdown_text)]

def extract_methods(markdown_text: str) -> List[Dict]:
    pattern = re.compile(r"##### DQ Method: (.+?)\n\*\*Name:\*\* (.+?)\n\*\*Input data type:\*\* (.+?)\n\*\*Output data type:\*\* (.+?)\n\*\*Algorithm:\*\*\s*```(?:sql)?\n([\s\S]+?)\s*```.*?\n\*\*Implements \(DQ Metric\):\*\* (.+?)(?=\n#####|$)", re.DOTALL)
    return [{"name": m[1].strip(), "input_data_type": m[2].strip(), "output_data_type": m[3].strip(), "algorithm": m[4].strip(), "metric": m[5].strip().split("\n")[0]} for m in pattern.findall(markdown_text)]