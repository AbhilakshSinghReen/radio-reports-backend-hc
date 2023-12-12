from django.contrib import admin

from radio_reports_api.models import Report

admin.site.site_title = "Abnormal Docs Administration"
admin.site.site_header = "Abnormal Docs Administration"
admin.site.index_title = "Admin Home"

admin.site.register(Report)
