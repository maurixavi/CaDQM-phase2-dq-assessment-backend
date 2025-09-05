from django.db import transaction
from typing import Dict, List
from dqmodel.models import (
    DQDimensionBase,
    DQFactorBase,
    DQMetricBase,
    DQMethodBase
)


class DQModelLoader:
    def __init__(self):
        self.suffix = ""
        self.stats = {
            'dimensions': {'created': 0, 'existing': 0, 'errors': 0},
            'factors': {'created': 0, 'existing': 0, 'errors': 0},
            'metrics': {'created': 0, 'existing': 0, 'errors': 0},
            'methods': {'created': 0, 'existing': 0, 'errors': 0}
        }

    @transaction.atomic
    def load_all(self, instances: Dict[str, List]):
        """Persiste todas las instancias en la base de datos."""
        self._load_dimensions(instances["dimensions"])
        self._load_factors(instances["factors"])
        self._load_metrics(instances["metrics"])
        self._load_methods(instances["methods"])
        return self.stats

    def _with_suffix(self, name: str) -> str:
        """Agrega sufijo de carga para distinguir los nombres."""
        return f"{name}{self.suffix}"

    def _load_dimensions(self, dimensions: List[DQDimensionBase]):
        for dim in dimensions:
            try:
                _, created = DQDimensionBase.objects.get_or_create(
                    name=self._with_suffix(dim.name),
                    defaults={'semantic': dim.semantic}
                )
                self._update_stats('dimensions', created)
            except Exception as e:
                self.stats['dimensions']['errors'] += 1
                print(f"Error loading dimension {dim.name}: {str(e)}")

    def _load_factors(self, factors: List[DQFactorBase]):
        for factor in factors:
            try:
                parent_dim = DQDimensionBase.objects.get(
                    name=self._with_suffix(factor.facetOf.name)
                )
                _, created = DQFactorBase.objects.get_or_create(
                    name=self._with_suffix(factor.name),
                    defaults={
                        'semantic': factor.semantic,
                        'facetOf': parent_dim
                    }
                )
                self._update_stats('factors', created)
            except Exception as e:
                self.stats['factors']['errors'] += 1
                print(f"Error loading factor {factor.name}: {str(e)}")

    def _load_metrics(self, metrics: List[DQMetricBase]):
        for metric in metrics:
            try:
                parent_factor = DQFactorBase.objects.get(
                    name=self._with_suffix(metric.measures.name)
                )
                _, created = DQMetricBase.objects.get_or_create(
                    name=self._with_suffix(metric.name),
                    defaults={
                        'purpose': metric.purpose,
                        'granularity': metric.granularity,
                        'resultDomain': metric.resultDomain,
                        'measures': parent_factor
                    }
                )
                self._update_stats('metrics', created)
            except Exception as e:
                self.stats['metrics']['errors'] += 1
                print(f"Error loading metric {metric.name}: {str(e)}")

    def _load_methods(self, methods: List[DQMethodBase]):
        for method in methods:
            try:
                parent_metric = DQMetricBase.objects.get(
                    name=self._with_suffix(method.implements.name)
                )
                _, created = DQMethodBase.objects.get_or_create(
                    name=self._with_suffix(method.name),
                    defaults={
                        'inputDataType': method.inputDataType,
                        'outputDataType': method.outputDataType,
                        'algorithm': method.algorithm,
                        'implements': parent_metric
                    }
                )
                self._update_stats('methods', created)
            except Exception as e:
                self.stats['methods']['errors'] += 1
                print(f"Error loading method {method.name}: {str(e)}")

    def _update_stats(self, model_type: str, created: bool):
        if created:
            self.stats[model_type]['created'] += 1
        else:
            self.stats[model_type]['existing'] += 1
