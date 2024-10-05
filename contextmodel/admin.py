from django.contrib import admin
from .models import ContextModel, ApplicationDomain, BusinessRule, UserType, TaskAtHand, DQRequirement, DataFiltering, SystemRequirement, DQMetadata, OtherMetadata, OtherData

admin.site.register(ContextModel)
admin.site.register(ApplicationDomain)
admin.site.register(BusinessRule)
admin.site.register(UserType)
admin.site.register(TaskAtHand)
admin.site.register(DQRequirement)
admin.site.register(DataFiltering)
admin.site.register(SystemRequirement)
admin.site.register(DQMetadata)
admin.site.register(OtherMetadata)
admin.site.register(OtherData)