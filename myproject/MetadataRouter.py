from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class MetadataRouter:
    
    def db_for_read(self, model, **hints):
        if model._meta.model_name in {'dqmodelexecution', 'dqmethodexecutionresult'}:
            return 'metadata_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.model_name in {'dqmodelexecution', 'dqmethodexecutionresult'}:
            return 'metadata_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir relaciones entre:
        # 1. Modelos de metadata_db entre sí
        # 2. Cualquier modelo con ContentType
        metadata_models = {'dqmodelexecution', 'dqmethodexecutionresult'}
        
        if (obj1._meta.model_name in metadata_models and 
            obj2._meta.model_name in metadata_models):
            return True
            
        if isinstance(obj1, ContentType) or isinstance(obj2, ContentType):
            return True
            
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in {'dqmodelexecution', 'dqmethodexecutionresult'}:
            return db == 'metadata_db'
        return None