from datetime import datetime
from django.db import models


class Downloader(models.Model):
    file_path = models.CharField('File', max_length=250, null=True, blank=True)
    file_type = models.CharField('File Type', max_length=20, null=True, blank=True)
    app_name = models.CharField('App Name', max_length=250, null=True, blank=True)
    headers_view = models.CharField('Headers View Name', max_length=250, null=True, blank=True)
    rows_view = models.CharField('View Name', max_length=250, null=True, blank=True)
    headers_data = models.TextField('Headers Data', null=True, blank=True)
    rows_data = models.TextField('Rows Data', null=True, blank=True)
    status = models.IntegerField('Status', null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    downloaded_by = models.CharField('Downloaded By', max_length=100, null=True, blank=True)
    requested_on = models.DateTimeField('Requested On', null=True, blank=True)
    request_completion_on = models.DateTimeField('Request Completion On', null=True, blank=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.requested_on = datetime.now()
        return super(Downloader, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.file_path or u''
