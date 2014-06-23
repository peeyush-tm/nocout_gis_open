import datetime
from django.db import models


# organization model
class Organization(models.Model):
    name = models.CharField('Name', max_length=250)
    city = models.CharField('City', max_length=200, null=True, blank=True)
    state = models.CharField('State', max_length=200, null=True, blank=True)
    country = models.CharField('Country', max_length=200, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    created_by = models.IntegerField()
    modified_by = models.IntegerField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

    # saving created_at & modified_at here
    def save(self, *args, **kwargs):
        today = datetime.datetime.today()
        if not self.id:
            if not self.created:
                self.created = today
            if not self.modified:
                self.modified = today
        else:
            self.modified = today
        super(Organization, self).save(*args, **kwargs)



