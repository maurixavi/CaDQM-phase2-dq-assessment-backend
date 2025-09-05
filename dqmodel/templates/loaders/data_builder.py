from typing import Dict, List
from django.db import transaction
from dqmodel.models import (
    DQDimensionBase,
    DQFactorBase,
    DQMetricBase,
    DQMethodBase
)

class DQModelBuilder:
    def __init__(self, raw_data: Dict[str, List[Dict]]):
        self.raw_data = raw_data
        self.dimension_map = {}
        self.factor_map = {}
        self.metric_map = {}

    def build_all(self) -> Dict[str, List]:
        """Construye todas las instancias de modelos."""
        return {
            "dimensions": self._build_dimensions(),
            "factors": self._build_factors(),
            "metrics": self._build_metrics(),
            "methods": self._build_methods()
        }

    def _build_dimensions(self) -> List[DQDimensionBase]:
        """Construye instancias de DQDimensionBase."""
        self.dimension_map = {
            dim["name"]: DQDimensionBase(
                name=dim["name"],
                semantic=dim["semantic"]
            )
            for dim in self.raw_data["dimensions"]
        }
        return list(self.dimension_map.values())

    def _build_factors(self) -> List[DQFactorBase]:
        """Construye instancias de DQFactorBase."""
        self.factor_map = {
            factor["name"]: DQFactorBase(
                name=factor["name"],
                semantic=factor["semantic"],
                facetOf=self.dimension_map[factor["dimension"]]
            )
            for factor in self.raw_data["factors"]
        }
        return list(self.factor_map.values())

    def _build_metrics(self) -> List[DQMetricBase]:
        """Construye instancias de DQMetricBase."""
        self.metric_map = {
            metric["name"]: DQMetricBase(
                name=metric["name"],
                purpose=metric["purpose"],
                granularity=metric["granularity"],
                resultDomain=metric["resultDomain"],
                measures=self.factor_map[metric["factor"]]
            )
            for metric in self.raw_data["metrics"]
        }
        return list(self.metric_map.values())

    def _build_methods(self) -> List[DQMethodBase]:
        """Construye instancias de DQMethodBase."""
        return [
            DQMethodBase(
                name=method["name"],
                inputDataType=method["inputDataType"],
                outputDataType=method["outputDataType"],
                algorithm=method["algorithm"],
                implements=self.metric_map[method["metric"]]
            )
            for method in self.raw_data["methods"]
        ]