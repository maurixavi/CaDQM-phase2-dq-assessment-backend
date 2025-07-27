from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class MetadataRouter:
    
    metadata_models = {
        'dqmodelexecution',
        'dqmethodexecutionresult',
        'executiontableresult',
        'executioncolumnresult',
        'executionrowresult'
    }

    def db_for_read(self, model, **hints):
        if model._meta.model_name in self.metadata_models:
            return 'metadata_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.model_name in self.metadata_models:
            return 'metadata_db'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        # 1. Permitir relaciones entre modelos de metadata
        if (obj1._meta.model_name in self.metadata_models and 
            obj2._meta.model_name in self.metadata_models):
            return True
            
        # 2. Permitir relaciones con ContentType
        if isinstance(obj1, ContentType) or isinstance(obj2, ContentType):
            return True
            
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Migraciones solo para metadata_db
        if model_name in self.metadata_models:
            return db == 'metadata_db'
            
        # Evitar que los modelos de metadata migren a default DB
        if db == 'default' and model_name in self.metadata_models:
            return False
            
        # Otros modelos (default DB o apps de Django)
        return None
