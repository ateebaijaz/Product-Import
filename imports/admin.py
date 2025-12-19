from django.contrib import admin
from imports.models import ImportJob
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'progress',
        'created_at',
        'updated_at',
    )
    list_filter = ('status',)
    readonly_fields = (
        'progress',
        'processed_rows',
        'total_rows',
        'created_at',
        'updated_at',
    )
admin.site.register(ImportJob, ImportJobAdmin)