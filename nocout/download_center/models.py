from django.db import models

# Create your models here.

class ProcessedReportDetails(models.Model):
    """
    class for putting in processed data excel
    """
    report_name = models.CharField('Report Name', max_length=255)
    report_path = models.CharField('Report Path', max_length=255)
    created_on  = models.DateTimeField('Created On', auto_now=True, auto_now_add=True, blank=True)

