from django.contrib import admin
from .models import Project, DataAtHand, DataSchema

admin.site.register(Project)
admin.site.register(DataAtHand)
admin.site.register(DataSchema)