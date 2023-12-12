from django.db import models


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    report_media_id = models.CharField(max_length=255)
    report_metadata = models.TextField()
    meshes_metadata = models.TextField()
    original_report = models.TextField()
    simplified_reports = models.TextField()
    processing_status = models.TextField()
