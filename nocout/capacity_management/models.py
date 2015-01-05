from organization.models import Organization

from django.db import models

from inventory.models import get_default_org, Sector, BaseStation

# Create your models here.
class SectorCapacityStatus(models.Model):
    """
    Performance Metric Table columns declared
    """
    sector = models.ForeignKey(Sector)
    #static information so as to save another db call
    sector_sector_id = models.CharField('Sector ID', max_length=64, db_index=True, null=True, blank=True)
    # bs_alias = models.CharField('BaseStation Alias', max_length=64, db_index=True, null=True, blank=True)
    # city = models.CharField('City Name', max_length=64, db_index=True, null=True, blank=True)
    # state = models.CharField('State Name', max_length=64, db_index=True, null=True, blank=True)
    # device_name = models.CharField('Device Name', max_length=64, db_index=True, null=True, blank=True)
    # ip_address = models.CharField('IP Address', max_length=32, db_index=True, null=True, blank=True)
    # technology = models.CharField('technology', max_length=32, db_index=True, null=True, blank=True)
    #static information so as to save another db call

    #polled information to be updated
    sector_capacity = models.IntegerField('Sector Capacity',  default=0)
    #polled information to be updated
    current_in_per = models.IntegerField('IN Current Utilization Percentage',  default=0)
    current_in_val = models.IntegerField('IN Current Utilization Value',  default=0)
    avg_in_per = models.IntegerField('IN Current Utilization Average Percentage',  default=0)
    avg_in_val = models.IntegerField('IN Current Utilization Average Value',  default=0)
    peak_in_per = models.IntegerField('IN Peak Utilization Percentage',  default=0)
    peak_in_val = models.IntegerField('IN Peak Utilization Value',  default=0)
    peak_in_timestamp = models.IntegerField('Peak In Timestamp', default=0)

    #polled information to be updated
    current_out_per = models.IntegerField('OUT Current Utilization Percentage',  default=0)
    current_out_val = models.IntegerField('OUT Current Utilization Value',  default=0)
    avg_out_per = models.IntegerField('OUT Current Utilization Average Percentage',  default=0)
    avg_out_val = models.IntegerField('OUT Current Utilization Average Value',  default=0)
    peak_out_per = models.IntegerField('OUT Peak Utilization Percentage',  default=0)
    peak_out_val = models.IntegerField('OUT Peak Utilization Value',  default=0)
    peak_out_timestamp = models.IntegerField('Peak Out Timestamp', default=0)
    #polled information to be updated
    sys_timestamp = models.IntegerField('SYS Timestamp', db_index=True,  default=0)

    #static information to be updated
    organization = models.ForeignKey(Organization, default=get_default_org)

    #severity can be because of any of the KPI services
    severity = models.CharField('Severity', max_length=20, null=True, blank=True)

    #age of the column having a severity: priority to critical then warning then ok
    age = models.IntegerField('Status Age', default=0)

    def __unicode__(self):
        return self.sector_id

    class Meta:
        ordering = ['-sys_timestamp']
