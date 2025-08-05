import csv

from django.contrib import messages
from django.http import HttpResponse


class InfoMessageMixin:
    """
    Add a info message on a class.
    """

    info_message = ""

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        info_message = self.info_message
        if info_message:
            messages.info(self.request, info_message)
        return response


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export Selected"