from django.db import models
from django.conf import settings

class ProcessedReportDetails(models.Model):
    """
    class for putting in processed data excel
    """
    report_name = models.CharField('Report Name', max_length=255)
    path = models.CharField('Report Path', max_length=512, default=settings.REPORT_PATH)
    created_on = models.DateTimeField('Created On', auto_now=True, auto_now_add=True, blank=True)
    report_date = models.DateTimeField('Report Date', blank=True, null=True)
    organization_id = models.IntegerField('Organization ID', default=1)


class ReportSettings(models.Model):
    """
    database table for report settings
    """
    page_name = models.CharField('Name of The Page for report', max_length=128)
    report_name = models.CharField('Report Name', max_length=255)
    report_frequency = models.CharField('Frequency of Report to be generated', max_length=128)


class CityCharter(models.Model):
    """
    City Charter Base CLass
    """
    circuit_id = models.CharField('Circuit ID', max_length=128, null=True, blank=True)
    city_name = models.CharField('City', max_length=128, null=True, blank=True)
    state_name = models.CharField('State', max_length=128, null=True, blank=True)
    customer_name = models.CharField('Customer', max_length=128, null=True, blank=True)
    bs_name = models.CharField('Base Station', max_length=128, null=True, blank=True)
    packetDrop = models.CharField('PD', max_length=128, null=True, blank=True)
    Latencydrop = models.CharField('RTA', max_length=128, null=True, blank=True)
    device_state = models.CharField('Device State', max_length=128, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=128, null=True, blank=True)
    ul = models.CharField('UL', max_length=128, null=True, blank=True)
    latency = models.CharField('Latency', max_length=128, null=True, blank=True)
    pd = models.CharField('Packet Drop', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class CityCharterSectors(CityCharter):
    """
    City Charter Sector Technology Base Class
    """
    vendor = models.CharField('Vendor', max_length=128, null=True, blank=True)
    ss_device_technology_name = models.CharField('SS Technology', max_length=128, null=True, blank=True)
    device_ss_ip_address = models.CharField('SS IP', max_length=128, null=True, blank=True)
    device_ss_mac_address = models.CharField('SS MAC', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('Near End IP', max_length=128, null=True, blank=True)
    sector_id = models.CharField('Sector ID', max_length=128, null=True, blank=True)
    dl_rssi_during_aceptance = models.CharField('DL RSSI Acceptance', max_length=128, null=True, blank=True)
    intrf = models.CharField('INTRF', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class CityCharterWiMAX(CityCharterSectors):
    """
    WiMAX City Charter Report
    """
    seg_wimax = models.CharField('Seg WiMAX', max_length=128, null=True, blank=True)
    pmp = models.CharField('PMP Port', max_length=128, null=True, blank=True)
    ul_cinr = models.CharField('UL CINR', max_length=128, null=True, blank=True)
    dl_cinr = models.CharField('DL CINR', max_length=128, null=True, blank=True)
    ptx = models.CharField('PTX', max_length=128, null=True, blank=True)


class CityCharterPMP(CityCharterSectors):
    """
    PMP City Charter Report
    """
    seg_pmp = models.CharField('Seg WiMAX', max_length=128, null=True, blank=True)
    ul_jitter = models.CharField('UL CINR', max_length=128, null=True, blank=True)
    dl_jitter = models.CharField('DL CINR', max_length=128, null=True, blank=True)
    rereg_count = models.CharField('INTRF', max_length=128, null=True, blank=True)
    reg_count = models.CharField('PTX', max_length=128, null=True, blank=True)


class CityCharterP2P(CityCharter):
    """
    P2P City Charter Report
    """
    seg_p2p = models.CharField('Seg P2P', max_length=128, null=True, blank=True)
    technology = models.CharField('Technology', max_length=128, null=True, blank=True)
    far_ip = models.CharField('UL CINR', max_length=128, null=True, blank=True)
    near_ip = models.CharField('DL CINR', max_length=128, null=True, blank=True)
    circuit_type = models.CharField('PTX', max_length=128, null=True, blank=True)
    far_device_ss_mac_address = models.CharField('INTRF', max_length=128, null=True, blank=True)
    near_sector_device_mac_address = models.CharField('PTX', max_length=128, null=True, blank=True)
    rssi_during_aceptance = models.CharField('PTX', max_length=128, null=True, blank=True)
    uas = models.CharField('PTX', max_length=128, null=True, blank=True)


class CityCharterCommon(models.Model):
    """
    Common for all technologies
    `city_name`  varchar(50),

    `wimax_los` varchar(50),
    `wimax_na` varchar(50),
    `wimax_rogue_ss` varchar(50),
    `wimax_ul` varchar(50),
    `wimax_pd` varchar(50),
    `wimax_latancy` varchar(50),
    `wimax_normal` varchar(50),

    `pmp_los` varchar(50),
    `pmp_na` varchar(50),
    `pmp_rogue_ss` varchar(50),
    `pmp_ul` varchar(50),
    `pmp_pd` varchar(50),
    `pmp_latancy` varchar(50),
    `pmp_normal` varchar(50),

    `p2p_los` varchar(50),
    `p2p_na` varchar(50),
    `p2p_rogue_ss` varchar(50),
    `p2p_pd` varchar(50),
    `p2p_latancy` varchar(50),
    `p2p_normal`  varchar(50).
    """
    city_name = models.CharField('City', max_length=128, null=True, blank=True)

    wimax_los = models.CharField('LOS WiMAX', max_length=128, null=True, blank=True)
    wimax_na = models.CharField('NA WiMAX', max_length=128, null=True, blank=True)
    wimax_rogue_ss = models.CharField('Rogue SS WiMAX', max_length=128, null=True, blank=True)
    wimax_ul = models.CharField('UL WiMAX', max_length=128, null=True, blank=True)
    wimax_pd = models.CharField('PD WiMAX', max_length=128, null=True, blank=True)
    wimax_latancy = models.CharField('Latency WiMAX', max_length=128, null=True, blank=True)
    wimax_normal = models.CharField('Normal WiMAX', max_length=128, null=True, blank=True)

    pmp_los = models.CharField('LOS PMP', max_length=128, null=True, blank=True)
    pmp_na = models.CharField('NA PMP', max_length=128, null=True, blank=True)
    pmp_rogue_ss = models.CharField('Rogue SS PMP', max_length=128, null=True, blank=True)
    pmp_ul = models.CharField('UL PMP', max_length=128, null=True, blank=True)
    pmp_pd = models.CharField('PD PMP', max_length=128, null=True, blank=True)
    pmp_latancy = models.CharField('Latency PMP', max_length=128, null=True, blank=True)
    pmp_normal = models.CharField('Normal PMP', max_length=128, null=True, blank=True)

    p2p_los = models.CharField('LOS P2P', max_length=128, null=True, blank=True)
    p2p_na = models.CharField('NA P2P', max_length=128, null=True, blank=True)
    p2p_rogue_ss = models.CharField('Rogue SS P2P', max_length=128, null=True, blank=True)
    p2p_pd = models.CharField('PD P2P', max_length=128, null=True, blank=True)
    p2p_latancy = models.CharField('Latency P2P', max_length=128, null=True, blank=True)
    p2p_normal = models.CharField('Normal P2P', max_length=128, null=True, blank=True)