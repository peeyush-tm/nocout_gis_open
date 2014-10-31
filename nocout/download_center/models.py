from django.db import models

# Create your models here.

class ProcessedReportDetails(models.Model):
    """
    class for putting in processed data excel
    """
    report_name = models.CharField('Report Name', max_length=255)
    report_path = models.CharField('Report Path', max_length=512)
    created_on  = models.DateTimeField('Created On', auto_now=True, auto_now_add=True, blank=True)
    orgnization_id = models.IntegerField('Organization ID', default=1)

class ReportSettings(models.Model):
    """
    database table for report settings
    """
    page_name = models.CharField('Name of The Page for report', max_length=128)
    report_name = models.CharField('Report Name', max_length=255)
    report_frequency = models.CharField('Frequency of Report to be generated', max_length=128)