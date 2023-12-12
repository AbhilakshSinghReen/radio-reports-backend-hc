from django.urls import path

from radio_reports_api.views import *


urlpatterns = [
    path('reports/add/', AddReportAPIView.as_view(), name='add_report'),
    path('reports/get-detail/', GetReportAPIView.as_view(), name='get_report_detail'),
]
