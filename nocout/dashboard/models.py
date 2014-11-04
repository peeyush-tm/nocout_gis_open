from django.db import models

from device.models import DeviceTechnology
from dashboard.config import dashboards


PAGE_NAME_CHOICES = (
    ('rf_dashboard', 'RF Performance Dashboard'),
    ('sector_dashboard', 'Sector Dashboard'),
)


def get_dashboard_name_choices():
    return dict([(dashboard['dashboard_name'], dashboard['dashboard_name']) for dashboard in dashboards]).items()


class DashboardSetting(models.Model):
    """
    Store settings for dashboards.

    - Only Super Admin can create dashboard settings.
    - One dashboard will have just one dashboard setting.
    """

    page_name = models.CharField('Page Name', max_length=30, choices=PAGE_NAME_CHOICES)
    technology = models.ForeignKey(DeviceTechnology)
    is_bh = models.BooleanField(default=False)
    name = models.CharField('Dashboard Name', max_length=250, choices=get_dashboard_name_choices())
    dashboard_type = models.CharField('Dashboard Type', max_length=3, choices=(('INT', 'Numeric'), ('STR', 'String')))

    range1_start = models.CharField('Range1 Start', max_length=20, null=True, blank=True)
    range1_end = models.CharField('Range1 End', max_length=20, null=True, blank=True)
    range1_color_hex_value = models.CharField('Range-1 Color', max_length=100, null=True, blank=True)

    range2_start = models.CharField('Range2 Start', max_length=20, null=True, blank=True)
    range2_end = models.CharField('Range2 End', max_length=20, null=True, blank=True)
    range2_color_hex_value = models.CharField('Range-2 Color', max_length=100, null=True, blank=True)

    range3_start = models.CharField('Range3 Start', max_length=20, null=True, blank=True)
    range3_end = models.CharField('Range3 End', max_length=20, null=True, blank=True)
    range3_color_hex_value = models.CharField('Range-3 Color', max_length=100, null=True, blank=True)

    range4_start = models.CharField('Range4 Start', max_length=20, null=True, blank=True)
    range4_end = models.CharField('Range4 End', max_length=20, null=True, blank=True)
    range4_color_hex_value = models.CharField('Range-4 Color', max_length=100, null=True, blank=True)

    range5_start = models.CharField('Range5 Start', max_length=20, null=True, blank=True)
    range5_end = models.CharField('Range5 End', max_length=20, null=True, blank=True)
    range5_color_hex_value = models.CharField('Range-5 Color', max_length=100, null=True, blank=True)

    range6_start = models.CharField('Range6 Start', max_length=20, null=True, blank=True)
    range6_end = models.CharField('Range6 End', max_length=20, null=True, blank=True)
    range6_color_hex_value = models.CharField('Range-6 Color', max_length=100, null=True, blank=True)

    range7_start = models.CharField('Range7 Start', max_length=20, null=True, blank=True)
    range7_end = models.CharField('Range7 End', max_length=20, null=True, blank=True)
    range7_color_hex_value = models.CharField('Range-7 Color', max_length=100, null=True, blank=True)

    range8_start = models.CharField('Range8 Start', max_length=20, null=True, blank=True)
    range8_end = models.CharField('Range8 End', max_length=20, null=True, blank=True)
    range8_color_hex_value = models.CharField('Range-8 Color', max_length=100, null=True, blank=True)

    range9_start = models.CharField('Range9 Start', max_length=20, null=True, blank=True)
    range9_end = models.CharField('Range9 End', max_length=20, null=True, blank=True)
    range9_color_hex_value = models.CharField('Range-9 Color', max_length=100, null=True, blank=True)

    range10_start = models.CharField('Range10 Start', max_length=20, null=True, blank=True)
    range10_end = models.CharField('Range10 End', max_length=20, null=True, blank=True)
    range10_color_hex_value = models.CharField('Range-10 Color', max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'page_name', 'technology', 'is_bh')
        verbose_name = "dashboard setting"
        verbose_name_plural = "dashboard settings"

    def __unicode__(self):
        return self.name
