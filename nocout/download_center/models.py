from device.models import DeviceTechnology
from django.db import models
from django.conf import settings
import datetime
from django.db.models.signals import post_save
from download_center.tasks import scheduled_email_report
from django.dispatch import receiver
import signals as dc_signals


def uploaded_file_name(instance, filename):
    timestamp = time.time()
    year_month_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    # In fname variable date is attach to file name which should be removed
    # fname = "{}_{}".format(filename, year_month_date)
    # modified path where file is uploaded
    path = "uploaded/FaultReports"

    return '{}/{}/{}'.format(path, year_month_date, filename)


class ProcessedReportDetails(models.Model):
    """
    class for putting in processed data excel
    """
    report_name = models.CharField('Report Name', max_length=255)
    path = models.CharField('Report Path', max_length=512, default=settings.REPORT_PATH)
    created_on = models.DateTimeField('Created On', auto_now_add=True, blank=True)
    report_date = models.DateTimeField('Report Date', blank=True, null=True)
    organization_id = models.IntegerField('Organization ID', default=1)


class ReportSettings(models.Model):
    """
    database table for report settings
    """
    page_name = models.CharField('Name of The Page for report', max_length=128)
    report_name = models.CharField('Report Name', max_length=255)
    report_title = models.CharField('Report Title', max_length=255, null=True, blank=True)
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
    wimax_ss_count = models.IntegerField('Count of WiMAX SS', default=0)
    wimax_ss_percentage = models.FloatField('% of WiMAX SS Affected', default=0)

    pmp_los = models.CharField('LOS PMP', max_length=128, null=True, blank=True)

    # replace
    # pmp_na = models.CharField('NA PMP', max_length=128, null=True, blank=True)
    pmp_jitter = models.CharField('NA PMP', max_length=128, null=True, blank=True)

    # replace
    # pmp_rogue_ss = models.CharField('Rogue SS PMP', max_length=128, null=True, blank=True)
    pmp_rereg = models.CharField('Rogue SS PMP', max_length=128, null=True, blank=True)

    pmp_ul = models.CharField('UL PMP', max_length=128, null=True, blank=True)
    pmp_pd = models.CharField('PD PMP', max_length=128, null=True, blank=True)
    pmp_latancy = models.CharField('Latency PMP', max_length=128, null=True, blank=True)
    pmp_normal = models.CharField('Normal PMP', max_length=128, null=True, blank=True)
    pmp_ss_count = models.IntegerField('Count of PMP SS', default=0)
    pmp_ss_percentage = models.FloatField('% of PMP SS Affected', default=0)

    p2p_los = models.CharField('LOS P2P', max_length=128, null=True, blank=True)

    # replace
    # p2p_na = models.CharField('NA P2P', max_length=128, null=True, blank=True)
    p2p_uas = models.CharField('NA P2P', max_length=128, null=True, blank=True)

    # remove this
    # p2p_rogue_ss = models.CharField('Rogue SS P2P', max_length=128, null=True, blank=True)

    p2p_pd = models.CharField('PD P2P', max_length=128, null=True, blank=True)
    p2p_latancy = models.CharField('Latency P2P', max_length=128, null=True, blank=True)
    p2p_normal = models.CharField('Normal P2P', max_length=128, null=True, blank=True)
    p2p_ss_count = models.IntegerField('Count of P2P SS', default=0)
    p2p_ss_percentage = models.FloatField('% of P2P SS Affected', default=0)

    total_ss_count = models.IntegerField('Count of ALL SS', default=0)
    total_ss_percentage = models.FloatField('% of P2P SS Affected', default=0)


class CityCharterSettings(models.Model):
    """
    Model used to store city charter settings.
    One row for each technology exist in the table.
    """
    technology = models.ForeignKey(DeviceTechnology)
    los = models.CharField('Line of Sight', max_length=128, null=True, blank=True)
    n_align = models.CharField('Needs Alignment', max_length=128, null=True, blank=True)
    rogue_ss = models.CharField('Rogue', max_length=128, null=True, blank=True)
    jitter = models.CharField('Jitter', max_length=128, null=True, blank=True)
    rereg = models.CharField('ReReg Count', max_length=128, null=True, blank=True)
    uas = models.CharField('UAS', max_length=128, null=True, blank=True)
    pd = models.CharField('Packet Drop', max_length=128, null=True, blank=True)
    latency = models.CharField('Latency', max_length=128, null=True, blank=True)
    normal = models.CharField('Normal', max_length=128, null=True, blank=True)


# ### Report Common Parameters

class ReportCommonParameters(models.Model):
    """
    Common fields for all reports
    """
    vendor = models.CharField('Vendor', max_length=128, null=True, blank=True)
    city = models.CharField('City', max_length=128, null=True, blank=True)
    state = models.CharField('State', max_length=128, null=True, blank=True)
    technology = models.CharField('Technology', max_length=128, null=True, blank=True)
    bs_name = models.CharField('BS Name', max_length=128, null=True, blank=True)
    report_date = models.DateTimeField('Report Date Time', null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonUtilizationParameters(models.Model):
    """
    common fields for utilization
    """
    ul_utilization_max = models.CharField('UL MAX', max_length=128, null=True, blank=True)
    ul_utilization_min = models.CharField('UL MIN', max_length=128, null=True, blank=True)
    ul_utilization_avg = models.CharField('UL AVG', max_length=128, null=True, blank=True)
    dl_utilization_max = models.CharField('DL MAX', max_length=128, null=True, blank=True)
    dl_utilization_min = models.CharField('DL MIN', max_length=128, null=True, blank=True)
    dl_utilization_avg = models.CharField('DL AVG', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonWimaxBSParameters(models.Model):
    """
    WiMAX BS parameters
    """
    idu_ip = models.CharField('IDU IP', max_length=128, null=True, blank=True)
    pmp = models.CharField('PMP Port', max_length=128, null=True, blank=True)
    sector_id = models.CharField('Sector ID', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonWimaxParameters(ReportCommonWimaxBSParameters):
    """
    WiMAX Parameters
    """
    customer_name = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    circuit_id = models.CharField('Circuit ID', max_length=128, null=True, blank=True)
    ss_ip = models.CharField('SS IP', max_length=128, null=True, blank=True)
    ss_mac = models.CharField('SS MAC', max_length=128, null=True, blank=True)
    dl_rssi_during_acceptance = models.CharField('RSSI', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonPMPBSParameters(models.Model):
    """
    PMP BS PArameters
    """
    odu_ip = models.CharField('IDU IP', max_length=128, null=True, blank=True)
    sector_id = models.CharField('Sector ID', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonPMPParameters(ReportCommonPMPBSParameters):
    """
    PMP report parameters
    """
    customer_name = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    circuit_id = models.CharField('Circuit ID', max_length=128, null=True, blank=True)
    ss_ip = models.CharField('SS IP', max_length=128, null=True, blank=True)
    ss_mac = models.CharField('SS MAC', max_length=128, null=True, blank=True)
    dl_rssi_during_acceptance = models.CharField('RSSI', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonLatencyParameters(models.Model):
    """
    latency parameters common to PMP, WiMAX
    """
    latency_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    latency_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    latency_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)
    count = models.CharField('Count', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonTOTParameters(models.Model):
    """
    TOT Reports
    """
    ul_tot_minutes = models.CharField('UL TOT Minutes', max_length=128, null=True, blank=True)
    dl_tot_minutes = models.CharField('DL TOT Minutes', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonPolledParameters(models.Model):
    """
    WiMAX and PMP polled parameters
    """
    ul_rssi = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    dl_rssi = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    pd = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    latency = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    percentage_avaliability = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    upsince = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    device_uptime = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    device_state = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    ul_utilization = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    dl_utilization = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    dl_rssi_during_aceptance = models.CharField('RSSI DL', max_length=128, null=True, blank=True)

    system_uptime = models.CharField('System Uptime', max_length=128, null=True, blank=True)
    current_value = models.CharField('Current Value', max_length=128, null=True, blank=True)
    device_name = models.CharField('Device Name', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonDuplexParameters(models.Model):
    """
    PMP & Wimax duplex reports
    """
    auto_neg = models.CharField('auto_neg', max_length=128, null=True, blank=True)
    duplex = models.CharField('duplex', max_length=128, null=True, blank=True)
    speed = models.CharField('speed', max_length=128, null=True, blank=True)
    auto_neg_duplex_change_counter = models.CharField('auto_neg_duplex_change_counter', max_length=128, null=True, blank=True)
    duplexduplex_change_counter = models.CharField('duplexduplex_change_counter', max_length=128, null=True, blank=True)
    speedduplex_change_counter = models.CharField('speedduplex_change_counter', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True


class ReportCommonPTPParameters(models.Model):
    """
    PTP parameters
    """
    customer_name = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    circuit_id = models.CharField('Circuit ID', max_length=128, null=True, blank=True)

    far_end_ip = models.CharField('FE IP', max_length=128, null=True, blank=True)
    near_end_ip = models.CharField('NE IP', max_length=128, null=True, blank=True)

    circuit_type = models.CharField('circuit_type', max_length=128, null=True, blank=True)

    near_end_mac_address = models.CharField('near_end_mac_address', max_length=128, null=True, blank=True)
    far_end_mac_address = models.CharField('far_end_mac_address', max_length=128, null=True, blank=True)

    rssi_during_acceptance = models.CharField('rssi_during_acceptance', max_length=128, null=True, blank=True)

    class Meta:
        abstract = True

# ### Report Common Parameters

class UtilizationTOTPMP(ReportCommonParameters, ReportCommonUtilizationParameters,
                        ReportCommonPMPBSParameters, ReportCommonTOTParameters):
    """

    CREATE TABLE `dc_utilization_tot_pmp_table` ()
    """
    pass


class UtilizationTOTWimax(ReportCommonParameters, ReportCommonUtilizationParameters,
                          ReportCommonWimaxBSParameters, ReportCommonTOTParameters):
    """

    CREATE TABLE `dc_utilization_tot_wimax_table` ()
    """
    pass


class ModulationWimax(ReportCommonParameters, ReportCommonWimaxParameters):
    """
    CREATE TABLE `dc_modulation_wimax` ()
    """
    dl_modulation_change_count = models.CharField('DL Modulation Count', max_length=128, null=True, blank=True)
    modulation_logs = models.TextField('Modulation Logs', null=True, blank=True)


class SSDumpPMP(ReportCommonParameters, ReportCommonPolledParameters,
                ReportCommonPMPParameters, ReportCommonDuplexParameters):
    """
    CREATE TABLE `dc_ss_dump_pmp_table` ()
    """
    mac = models.CharField('mac', max_length=128, null=True, blank=True)

    device_ss_ip_address = models.CharField('device_ss_ip_address', max_length=128, null=True, blank=True)
    circuit_qos_bandwidth = models.CharField('circuit_qos_bandwidth', max_length=128, null=True, blank=True)
    sub_station_latitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_longitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_building_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_tower_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    beam_width = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_polarization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_mount_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_ethernet_extender = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    cabel_length = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_dl_rssi_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_dl_cinr_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    customer_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_date_of_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_reflector = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ap_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    vlan = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    bs_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    version = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    frequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    dl_jitter = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    ul_jitter = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    link = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    autom_nego = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    errors = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    rereg_count = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    reg_count = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class SSDumpWimax(ReportCommonParameters, ReportCommonPolledParameters,
                  ReportCommonWimaxParameters, ReportCommonDuplexParameters):
    """
    CREATE TABLE `dc_ss_dump_wimax_table` ()
    """

    circuit_qos_bandwidth = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_latitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_longitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    mac = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_building_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_tower_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_polarization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ss_antena_mount_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sub_station_ethernet_extender = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    cabel_length = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_dl_rssi_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_dl_cinr_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    customer_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_date_of_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_ss_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    vlan = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    sector_id_polled = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    version = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    frequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    dl_cinr = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    ul_cinr = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ptx = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    inrf_ul = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    inrf_dl = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    session_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    ul_fec = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dl_fec = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    link = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    autom_nego = models.CharField('circuit_id', max_length=128, null=True, blank=True)

    errors = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dl_modulation = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ul_qos = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dl_qos = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class HealthPTP(ReportCommonParameters):
    """
    CREATE TABLE `dc_health_ptp_table` ()
    """
    circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    customer_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_end_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_end_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_end_mac_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_end_mac_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    rssi_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    throughput_during_acceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endchannel_bw = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endactual_throughput = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_enddevice_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endfrequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endeth_port_setting = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_enduas = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endhop_length = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endrssi = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endpd = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endlatency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_endpercentage_availbility = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_end_ul_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_end_dl_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endchannel_bw = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endactual_throughput = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_enddevice_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endfrequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endeth_port_setting = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_enduas = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endhop_length = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endrssi = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endpd = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endlatency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_endpercentage_availbility = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_end_ul_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_end_dl_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class RectificationSegmentPTP(ReportCommonParameters):
    """
    CREATE TABLE `dc_sp_rectification_segment_p2p` ()
    """
    seg_p2p = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    customer_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_device_ss_mac_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_sector_device_mac_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    rssi_during_aceptance = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_rssi = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_pd = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_latency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_percentage_availability = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    near_end_rectification = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_rssi = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_pd = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_latency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_percentage_availability = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    far_end_rectification = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class RectificationSegmentPMP(ReportCommonParameters, ReportCommonPMPParameters, ReportCommonPolledParameters):
    """
    CREATE TABLE `dc_sp_rectification_segment_pmp` ()
    """
    seg_pmp = models.CharField('Seg PMP', max_length=128, null=True, blank=True)
    ss_device_technology_name = models.CharField('SS Tech', max_length=128, null=True, blank=True)

    device_ss_ip_address = models.CharField('SS IP', max_length=128, null=True, blank=True)
    device_ss_mac_address = models.CharField('SS MAC', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('Sector IP', max_length=128, null=True, blank=True)


class RectificationSegmentWimax(ReportCommonParameters, ReportCommonWimaxParameters, ReportCommonPolledParameters):
    """
    CREATE TABLE `dc_sp_rectification_segment_wimax` ()
    """
    seg_wimax = models.CharField('Seg WiMAX', max_length=128, null=True, blank=True)

    ss_device_technology_name = models.CharField('ss_device_technology_name', max_length=128, null=True, blank=True)

    device_ss_ip_address = models.CharField('device_ss_ip_address', max_length=128, null=True, blank=True)

    device_ss_mac_address = models.CharField('device_ss_mac_address', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('sector_device_ip_address', max_length=128, null=True, blank=True)

    ul_cinr = models.CharField('ul_cinr', max_length=128, null=True, blank=True)
    dl_cinr = models.CharField('dl_cinr', max_length=128, null=True, blank=True)

    ul_intrf = models.CharField('ul_intrf', max_length=128, null=True, blank=True)
    dl_intrf = models.CharField('dl_intrf', max_length=128, null=True, blank=True)
    ptx = models.CharField('ptx', max_length=128, null=True, blank=True)


class DuplexReportPTP(ReportCommonParameters, ReportCommonPTPParameters):
    """
    CREATE TABLE `dc_duplex_report_ptp_table` ()
    """
    neport_autonegotiation = models.CharField('neport_autonegotiation', max_length=128, null=True, blank=True)
    feport_autonegotiation = models.CharField('feport_autonegotiation', max_length=128, null=True, blank=True)
    neport_autonegotiationduplex_change_counter = models.CharField('neport_autonegotiationduplex_change_counter', max_length=128, null=True, blank=True)
    feport_autonegotiationduplex_change_counter = models.CharField('feport_autonegotiationduplex_change_counter', max_length=128, null=True, blank=True)


class DuplexReportPMP(ReportCommonParameters, ReportCommonPMPParameters, ReportCommonDuplexParameters):
    """
    CREATE TABLE `dc_duplex_report_pmp_table` ()
    """
    pass


class DuplexReportWimax(ReportCommonParameters, ReportCommonWimaxParameters, ReportCommonDuplexParameters):
    """
    CREATE TABLE `dc_duplex_report_wimax_table` ()
    """
    pass


class PTPDump(ReportCommonParameters):
    """
    CREATE TABLE `dc_ptp_dump_table` ()
    """
    circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    circuit_type = models.CharField('circuit_type', max_length=128, null=True, blank=True)
    customer_name = models.CharField('customer_name', max_length=128, null=True, blank=True)
    bs_address = models.CharField('bs_address', max_length=128, null=True, blank=True)
    circuit_qos_bandwidth_ss = models.CharField('circuit_qos_bandwidth_ss', max_length=128, null=True, blank=True)
    bs_latitude = models.CharField('bs_latitude', max_length=128, null=True, blank=True)
    bs_longitude = models.CharField('bs_longitude', max_length=128, null=True, blank=True)
    mimo_diversity = models.CharField('mimo_diversity', max_length=128, null=True, blank=True)
    antena_height = models.CharField('antena_height', max_length=128, null=True, blank=True)
    polarization = models.CharField('polarization', max_length=128, null=True, blank=True)
    antenna_type = models.CharField('antenna_type', max_length=128, null=True, blank=True)
    gain = models.CharField('gain', max_length=128, null=True, blank=True)
    mount_type = models.CharField('mount_type', max_length=128, null=True, blank=True)
    sub_station_ethernet_extender_ss = models.CharField('sub_station_ethernet_extender_ss', max_length=128, null=True, blank=True)
    building_height = models.CharField('building_height', max_length=128, null=True, blank=True)
    tower_height = models.CharField('tower_height', max_length=128, null=True, blank=True)
    bs_cable_length_ss = models.CharField('bs_cable_length_ss', max_length=128, null=True, blank=True)
    circuit_dl_rssi_during_acceptance_ss = models.CharField('circuit_dl_rssi_during_acceptance_ss', max_length=128, null=True, blank=True)
    circuit_throughput_during_acceptance_ss = models.CharField('circuit_throughput_during_acceptance_ss', max_length=128, null=True, blank=True)
    circuit_date_of_acceptance_ss = models.CharField('circuit_date_of_acceptance_ss', max_length=128, null=True, blank=True)
    bh_bso = models.CharField('bh_bso', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('sector_device_ip_address', max_length=128, null=True, blank=True)
    sector_device_mac_address = models.CharField('sector_device_mac_address', max_length=128, null=True, blank=True)
    hssu_used = models.CharField('hssu_used', max_length=128, null=True, blank=True)
    hssu_port = models.CharField('hssu_port', max_length=128, null=True, blank=True)
    device_bs_switch_ip_address = models.CharField('device_bs_switch_ip_address', max_length=128, null=True, blank=True)
    device_bh_aggregator_ip_address = models.CharField('device_bh_aggregator_ip_address', max_length=128, null=True, blank=True)
    aggregator_switch_port_name = models.CharField('aggregator_switch_port_name', max_length=128, null=True, blank=True)
    bs_convertor_ip = models.CharField('bs_convertor_ip', max_length=128, null=True, blank=True)
    pop_convertor_ip = models.CharField('pop_convertor_ip', max_length=128, null=True, blank=True)
    convertor_type = models.CharField('convertor_type', max_length=128, null=True, blank=True)
    device_bh_configured_ip_address = models.CharField('device_bh_configured_ip_address', max_length=128, null=True, blank=True)
    bh_switch_port_name = models.CharField('bh_switch_port_name', max_length=128, null=True, blank=True)
    bh_capacity = models.CharField('bh_capacity', max_length=128, null=True, blank=True)
    offnet_onnet = models.CharField('offnet_onnet', max_length=128, null=True, blank=True)
    bh_circuit_id = models.CharField('bh_circuit_id', max_length=128, null=True, blank=True)
    pe_hostname = models.CharField('pe_hostname', max_length=128, null=True, blank=True)
    pe_ip = models.CharField('pe_ip', max_length=128, null=True, blank=True)
    ss_city_ss = models.CharField('ss_city_ss', max_length=128, null=True, blank=True)
    ss_state = models.CharField('ss_state', max_length=128, null=True, blank=True)
    circuit_name = models.CharField('circuit_name', max_length=128, null=True, blank=True)
    customer_name_ss = models.CharField('customer_name_ss', max_length=128, null=True, blank=True)
    customer_address = models.CharField('customer_address', max_length=128, null=True, blank=True)
    bs_name_ss = models.CharField('bs_name_ss', max_length=128, null=True, blank=True)
    circuit_qos_bandwidth = models.CharField('circuit_qos_bandwidth', max_length=128, null=True, blank=True)
    sub_station_latitude = models.CharField('sub_station_latitude', max_length=128, null=True, blank=True)
    sub_station_longitude = models.CharField('sub_station_longitude', max_length=128, null=True, blank=True)
    ss_antena_height = models.CharField('ss_antena_height', max_length=128, null=True, blank=True)
    ss_antena_polarization = models.CharField('ss_antena_polarization', max_length=128, null=True, blank=True)
    ss_antena_type = models.CharField('ss_antena_type', max_length=128, null=True, blank=True)
    ss_antena_mount_type = models.CharField('ss_antena_mount_type', max_length=128, null=True, blank=True)
    sub_station_ethernet_extender = models.CharField('sub_station_ethernet_extender', max_length=128, null=True, blank=True)
    sub_station_building_height = models.CharField('sub_station_building_height', max_length=128, null=True, blank=True)
    sub_station_tower_height = models.CharField('sub_station_tower_height', max_length=128, null=True, blank=True)
    ss_cabel_length = models.CharField('ss_cabel_length', max_length=128, null=True, blank=True)
    circuit_dl_rssi_during_acceptance = models.CharField('circuit_dl_rssi_during_acceptance', max_length=128, null=True, blank=True)
    circuit_throughput_during_acceptance = models.CharField('circuit_throughput_during_acceptance', max_length=128, null=True, blank=True)
    circuit_date_of_acceptance = models.CharField('circuit_date_of_acceptance', max_length=128, null=True, blank=True)
    ss_bh_bso = models.CharField('ss_bh_bso', max_length=128, null=True, blank=True)
    ss_ip = models.CharField('ss_ip', max_length=128, null=True, blank=True)
    MAC = models.CharField('MAC', max_length=128, null=True, blank=True)
    product_type = models.CharField('product_type', max_length=128, null=True, blank=True)
    ssid = models.CharField('ssid', max_length=128, null=True, blank=True)
    master_slave = models.CharField('master_slave', max_length=128, null=True, blank=True)
    frequency = models.CharField('frequency', max_length=128, null=True, blank=True)
    uas = models.CharField('uas', max_length=128, null=True, blank=True)
    rssi = models.CharField('rssi', max_length=128, null=True, blank=True)
    estimated_throuput = models.CharField('estimated_throuput', max_length=128, null=True, blank=True)
    ul_utilization = models.CharField('ul_utilization', max_length=128, null=True, blank=True)
    dl_utilization = models.CharField('dl_utilization', max_length=128, null=True, blank=True)
    uptime = models.CharField('uptime', max_length=128, null=True, blank=True)
    link_distance = models.CharField('link_distance', max_length=128, null=True, blank=True)
    cbw = models.CharField('cbw', max_length=128, null=True, blank=True)
    latency = models.CharField('latency', max_length=128, null=True, blank=True)
    pd = models.CharField('pd', max_length=128, null=True, blank=True)
    auto_negotitaion = models.CharField('auto_negotitaion', max_length=128, null=True, blank=True)
    duplex = models.CharField('duplex', max_length=128, null=True, blank=True)
    speed = models.CharField('speed', max_length=128, null=True, blank=True)
    link = models.CharField('link', max_length=128, null=True, blank=True)
    idusn = models.CharField('idusn', max_length=128, null=True, blank=True)
    odusn = models.CharField('odusn', max_length=128, null=True, blank=True)
    ss_product_type = models.CharField('ss_product_type', max_length=128, null=True, blank=True)
    ss_ssid = models.CharField('ss_ssid', max_length=128, null=True, blank=True)
    ss_master_slave = models.CharField('ss_master_slave', max_length=128, null=True, blank=True)
    ss_frequency = models.CharField('ss_frequency', max_length=128, null=True, blank=True)
    ss_uas = models.CharField('ss_uas', max_length=128, null=True, blank=True)
    ss_rssi = models.CharField('ss_rssi', max_length=128, null=True, blank=True)
    ss_estimated_throuput = models.CharField('ss_estimated_throuput', max_length=128, null=True, blank=True)
    ss_ul_utilization = models.CharField('ss_ul_utilization', max_length=128, null=True, blank=True)
    ss_dl_utilization = models.CharField('ss_dl_utilization', max_length=128, null=True, blank=True)
    ss_uptime = models.CharField('ss_uptime', max_length=128, null=True, blank=True)
    ss_link_distance = models.CharField('ss_link_distance', max_length=128, null=True, blank=True)
    ss_cbw = models.CharField('ss_cbw', max_length=128, null=True, blank=True)
    ss_latency = models.CharField('ss_latency', max_length=128, null=True, blank=True)
    ss_pd = models.CharField('ss_pd', max_length=128, null=True, blank=True)
    ss_auto_negotitaion = models.CharField('ss_auto_negotitaion', max_length=128, null=True, blank=True)
    ss_speed = models.CharField('ss_speed', max_length=128, null=True, blank=True)
    ss_link = models.CharField('ss_link', max_length=128, null=True, blank=True)
    ss_idusn = models.CharField('ss_idusn', max_length=128, null=True, blank=True)
    ss_odusn = models.CharField('ss_odusn', max_length=128, null=True, blank=True)


class BSDumpPMP(ReportCommonParameters):
    """
    CREATE TABLE `dc_bs_dump_pmp_table` ()
    """
    bs_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_site_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    infra_provider = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_site_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    building_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tower_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_latitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_longitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_alias = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    make_of_antenna = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    polarization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tilt = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    antena_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    beam_width = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    azimuth_angle = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sync_splitter_used = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    gps_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_bs_switch_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_bh_aggregator_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    aggregator_switch_port_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_convertor_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pop_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    convertor_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_config_on_switch_convertor = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_port_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_capacity = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    offnet_onnet = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pe_hostname = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pe_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ttsl_circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dr_site = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_ul_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_dl_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    polled_sector_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    frequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tx_power = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    commanded_rx_power = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    rf_bandwidth = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    odu_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    system_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    cell_radius = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    modulation = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    master_slave = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sn_odu = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class BSDumpWimax(ReportCommonParameters):
    """
    CREATE TABLE `dc_bs_dump_wimax_table` ()
    """
    bs_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_device_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_site_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    infra_provider = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_site_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    building_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tower_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_latitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_longitude = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_alias = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    PMP = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    make_of_antenna = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    polarization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tilt = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    antena_height = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    beam_width = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    azimuth_angle = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    splitter_installed = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    gps_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_bs_switch_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    device_bh_aggregator_ip_address = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    aggregator_port_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bs_convertor_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pop_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    convertor_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_config_on_switch_convertor = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_port_name = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_capacity = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    offnet_onnet = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    bh_circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pe_hostname = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    pe_ip = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dr_site = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    ttsl_circuit_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    dr_master_slave = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    mrc = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_id = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_ul_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sector_dl_utilization = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    temp_sector_color = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    frequency = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    tx_power = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    commanded_rx_power = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    rf_bandwidth = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    idu_type = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    system_uptime = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    sn_odu = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    idu_serial_chassis_board = models.CharField('circuit_id', max_length=128, null=True, blank=True)
    idu_serial_carrier_board = models.CharField('circuit_id', max_length=128, null=True, blank=True)


class CustomerPTP(ReportCommonParameters, ReportCommonPTPParameters):
    """
    CREATE TABLE `dc_customer_ptp_table` ()
    """
    throughput_during_acceptance = models.CharField('throughput_during_acceptance', max_length=128, null=True, blank=True)

    far_endchannel_bw = models.CharField('far_endchannel_bw', max_length=128, null=True, blank=True)
    far_endactual_throughput = models.CharField('far_endactual_throughput', max_length=128, null=True, blank=True)
    far_enddevice_uptime = models.CharField('far_enddevice_uptime', max_length=128, null=True, blank=True)
    far_endfrequency = models.CharField('far_endfrequency', max_length=128, null=True, blank=True)
    far_endeth_port_setting = models.CharField('far_endeth_port_setting', max_length=128, null=True, blank=True)
    far_enduas = models.CharField('far_enduas', max_length=128, null=True, blank=True)
    far_endhop_length = models.CharField('far_endhop_length', max_length=128, null=True, blank=True)
    far_endrssi = models.CharField('far_endrssi', max_length=128, null=True, blank=True)
    far_endpd = models.CharField('far_endpd', max_length=128, null=True, blank=True)
    far_endlatency = models.CharField('far_endlatency', max_length=128, null=True, blank=True)
    far_endpercentage_availbility = models.CharField('far_endpercentage_availbility', max_length=128, null=True, blank=True)
    far_end_ul_utilization = models.CharField('far_end_ul_utilization', max_length=128, null=True, blank=True)
    far_end_dl_utilization = models.CharField('far_end_dl_utilization', max_length=128, null=True, blank=True)

    near_endchannel_bw = models.CharField('near_endchannel_bw', max_length=128, null=True, blank=True)
    near_endactual_throughput = models.CharField('near_endactual_throughput', max_length=128, null=True, blank=True)
    near_enddevice_uptime = models.CharField('near_enddevice_uptime', max_length=128, null=True, blank=True)
    near_endfrequency = models.CharField('near_endfrequency', max_length=128, null=True, blank=True)
    near_endeth_port_setting = models.CharField('near_endeth_port_setting', max_length=128, null=True, blank=True)
    near_enduas = models.CharField('near_enduas', max_length=128, null=True, blank=True)
    near_endhop_length = models.CharField('near_endhop_length', max_length=128, null=True, blank=True)
    near_endrssi = models.CharField('near_endrssi', max_length=128, null=True, blank=True)
    near_endpd = models.CharField('near_endpd', max_length=128, null=True, blank=True)
    near_endlatency = models.CharField('near_endlatency', max_length=128, null=True, blank=True)
    near_endpercentage_availbility = models.CharField('near_endpercentage_availbility', max_length=128, null=True, blank=True)
    near_end_ul_utilization = models.CharField('near_end_ul_utilization', max_length=128, null=True, blank=True)
    near_end_dl_utilization = models.CharField('near_end_dl_utilization', max_length=128, null=True, blank=True)


class CustomerPMP(ReportCommonParameters, ReportCommonPMPParameters, ReportCommonPolledParameters):
    """
    Customer PMP reports
    """
    jitter_ul = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    jitter_dl = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    rereg_count = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    reg_count = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    crc_error = models.CharField('Customer Name', max_length=128, null=True, blank=True)


class CustomerWimax(ReportCommonParameters, ReportCommonWimaxParameters, ReportCommonPolledParameters):
    """
    Customer WiMAX Reports
    """

    ul_cinr = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    dlcinr = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    intrf_ul = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    intrf_dl = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    ptx = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    vlan = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    polled_frequency = models.CharField('Customer Name', max_length=128, null=True, blank=True)

    ul_fec = models.CharField('Customer Name', max_length=128, null=True, blank=True)
    dl_fec = models.CharField('Customer Name', max_length=128, null=True, blank=True)


class LatencyReportPTP(ReportCommonParameters, ReportCommonPTPParameters):
    """
    CREATE TABLE `dc_latency_report_ptp_table` ()
    """

    near_endlatency_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    near_endlatency_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    near_endlatency_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)

    far_endlatency_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    far_endlatency_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    far_endlatency_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)

    near_endul_utilization_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    near_endul_utilization_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    near_endul_utilization_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)
    near_enddl_utilization_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    near_enddl_utilization_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    near_enddl_utilization_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)

    far_endul_utilization_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    far_endul_utilization_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    far_endul_utilization_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)
    far_enddl_utilization_max = models.CharField('Latency MAX', max_length=128, null=True, blank=True)
    far_enddl_utilization_min = models.CharField('Latency MIN', max_length=128, null=True, blank=True)
    far_enddl_utilization_avg = models.CharField('Latency AVG', max_length=128, null=True, blank=True)

    near_end_count = models.CharField('Count', max_length=128, null=True, blank=True)
    far_end_count = models.CharField('Count', max_length=128, null=True, blank=True)


class LatencyReportPMP(ReportCommonParameters, ReportCommonUtilizationParameters,
                       ReportCommonPMPParameters, ReportCommonLatencyParameters):
    """
    CREATE TABLE `dc_latency_report_pmp_table` ()
    """
    pass


class LatencyReportWimax(ReportCommonParameters, ReportCommonUtilizationParameters,
                         ReportCommonWimaxParameters, ReportCommonLatencyParameters):
    """
    CREATE TABLE `dc_latency_report_wimax_table` ()
    """
    pass


class TemperatureWimax(ReportCommonParameters):
    """
    CREATE TABLE `dc_temperature_wimax` ()
    """
    sector_device_ip_address = models.CharField('Sector IP', max_length=128, null=True, blank=True)
    pmp = models.CharField('PMP Port', max_length=128, null=True, blank=True)
    sector_name = models.CharField('Sector Name', max_length=128, null=True, blank=True)
    sector_id = models.CharField('Sector ID', max_length=128, null=True, blank=True)
    temp_max = models.CharField('Temparature MAX', max_length=128, null=True, blank=True)
    temp_min = models.CharField('Temparature MIN', max_length=128, null=True, blank=True)
    temp_avg = models.CharField('Temparature AVG', max_length=128, null=True, blank=True)
    temp_timeDiff = models.CharField('temp time Diff', max_length=128, null=True, blank=True)


class BSOutageReports(models.Model):
    """
    Upload model for BS Outage
    """

    name = models.CharField('Report Name', max_length=128)
    is_processed = models.IntegerField('Report Processing Details', default=0)
    process_for = models.DateField('User Tagged Report Date or Month', blank=True, default=datetime.datetime.now)
    upload_to = models.FileField('Uploaded File', upload_to=uploaded_file_name, max_length=512)
    absolute_path = models.TextField('Absolute File Path on OS')

    def __unicode__(self):
        return self.name


class BSOutageMasterStructure(models.Model):
    """

    """
    # report_id = models.ForeignKey(BSOutageReports)
    # organization = models.CharField('Organization', max_length=128)
    s_no = models.CharField('S. No.', max_length=128, null=True, blank=True)
    processed_report = models.ForeignKey(ProcessedReportDetails, null=True, blank=True)
    week_number = models.CharField('Week of the Year', max_length=128)
    ticket_number = models.CharField('Trouble Ticket Number', max_length=128)
    total_affected_bs = models.CharField('Number of BS Affected', max_length=128)
    city = models.CharField('City', max_length=256)
    type_of_city = models.CharField('Type of City', max_length=128)
    bs_name = models.CharField('BaseStation Name', max_length=256)
    bs_type = models.CharField('BaseStation Type', max_length=128)
    fault_type = models.CharField('Type of Fault', max_length=128)
    bs_ip = models.CharField('BS IP Address', max_length=128)
    bs_sw_version = models.CharField('BS Software Version', max_length=128)
    total_affected_sector = models.CharField('Number of Sectors Affected', max_length=128)
    switch_reachability = models.CharField('Switch Reachability', max_length=128)
    outage_timestamp = models.CharField('Outage Date And Time', max_length=128, null=True, blank=True)
    restored_timestamp = models.CharField('Restored Date And Time', max_length=128, null=True, blank=True)
    alarm_restored_timestamp = models.CharField('Alarm Restored Date And Time', max_length=128, null=True, blank=True)
    outage_min_per_site = models.CharField('Outage Per Site(Min.)', max_length=128)
    mttr_hrs = models.CharField('MTTR Hrs', max_length=128)
    mttr = models.CharField('MTTR', max_length=128)
    outage_total_min = models.CharField('Outage Total(Min.)', max_length=128)
    alarm_outage_min = models.CharField('Alarm Outage(Min.)', max_length=128)
    total_affected_enterprise_ss = models.CharField('Number of Enterprise SS Affected', max_length=128)
    total_affected_retail_ss = models.CharField('Number of Retail SS Affected', max_length=128)
    l1_engg_name = models.CharField('Name of L1 Engineer', max_length=256)
    l2_engg_name = models.CharField('Name of L2 Engineer', max_length=256)
    call_assigned_to = models.CharField('Call Assigned To', max_length=256)
    last_modified_by = models.CharField('Last Modified By', max_length=256)
    tac_tt_number = models.CharField('Tac TT Number', max_length=128)
    cause_code = models.CharField('Cause Code', max_length=128)
    sub_cause_code = models.CharField('Sub Cause Code', max_length=128)
    unit_replaced = models.CharField('Unit Replaced', max_length=128)
    equipment_replaced = models.CharField('Equipment Replaced', max_length=128)
    old_sr_number = models.CharField('Old Sno.', max_length=128)
    new_sr_number = models.CharField('New Sno.', max_length=128)
    alarm_observer = models.CharField('Alarm Observed', max_length=256)
    delay = models.CharField('Delay', max_length=128)
    delay_reason = models.CharField('Delay Reason', max_length=256)
    restore_action = models.CharField('Action Taken to Restore the BS', max_length=256)
    fault_description = models.CharField('Remark/Detail Fault Description', max_length=256, null=True, blank=True)
    status = models.CharField('Status', max_length=128)
    infra_provider = models.CharField('INFRA Provider', max_length=128)
    site_id = models.CharField('Site ID', max_length=128)
    spot_cases = models.CharField('Spot Cases', max_length=128)
    fault_history = models.CharField('Fault History', max_length=256, null=True, blank=True)
    rfo = models.CharField('RFO', max_length=256)
    uploaded_at = models.DateTimeField('Uploaded At', auto_now_add=True, blank=True)

    class Meta:
        abstract = True    

class BSOutageMasterDaily(BSOutageMasterStructure):
    """

    """
    pass


class BSOutageMasterWeekly(BSOutageMasterStructure):
    """

    """
    pass


class BSOutageMasterMonthly(BSOutageMasterStructure):
    """

    """
    pass


# class BSOutageFaultStructure(models.Model):
#     """

#     """
#     # report_id = models.ForeignKey(BSOutageReports)
#     organization = models.CharField('Organization', max_length=128)
#     city = models.CharField('City', max_length=256)
#     fault_type = models.CharField('Type of Fault', max_length=128)
#     outage_min_per_site = models.CharField('Outage Per Site(Min.)', max_length=128)
#     outage_count = models.CharField('Outage Count', max_length=128)
#     uploaded_at = models.DateTimeField('Uploaded At', auto_now_add=True, blank=True)

#     class Meta:
#         abstract = True

# class BSOutageFaultDaily(BSOutageFaultStructure):
#     """

#     """
#     pass


# class BSOutageFaultWeekly(BSOutageFaultStructure):
#     """

#     """
#     pass


# class BSOutageFaultMonthly(BSOutageFaultStructure):
#     """

#     """
#     pass


# class BSOutageMTTRProcessed(models.Model):
#     """
#     BSOutage Processed Report Details
#     """
#     # report_id = models.ForeignKey(BSOutageReports)
#     organization = models.CharField('Organization', max_length=128)
#     city = models.CharField('City', max_length=256)
#     bs_name = models.CharField('BaseStation Name', max_length=256)
#     rfo = models.CharField('RFO', max_length=256, null=True, blank=True)
#     processed_on = models.CharField('Processed Date and Time', max_length=128)
#     time_frame = models.CharField('4-8 or Greater than 8 hrs', max_length=128)
#     processed_key = models.CharField('Key for Processing', max_length=128)
#     processed_value = models.CharField('Value of Processing', max_length=64)


# class BSOutageUptimeReport(models.Model):
#     """

#     """
#     # report_id = models.ForeignKey(BSOutageReports)
#     organization = models.CharField('Organization', max_length=128)
#     city = models.CharField('City', max_length=256)
#     bs_name = models.CharField('BaseStation Name', max_length=256)
#     bs_uptime = models.CharField('BS Uptime', max_length=128)
#     total_uptime_min = models.CharField('Total Uptime(Min.)', max_length=128)
#     total_uptime_percent = models.CharField('Uptime in %', max_length=128)

class EmailReport(models.Model):
    report_name= models.ForeignKey(ReportSettings)
    email_list = models.TextField()

# Post Singnal call triggers to initiate email report.
# post_save.connect(dc_signals.send_mail_on_report_generation, sender=ProcessedReportDetails)

class Customer_Count_Sector(models.Model):
	sector_id = models.CharField('Sector ID', max_length=55, null=True)
	sector_config_ip = models.CharField('Sector Config IP', max_length=55, null=True)
	bs_name = models.CharField('BS Name', max_length=55, null=True)
	count_of_customer = models.CharField('Count Of Customer', max_length=55, null=True)
	technology = models.CharField('Technology', max_length=55, null=True)

class Customer_Count_BSname(models.Model):
	base_station_name = models.CharField('Base Station Name', max_length=55, null=True)
	bs_converter = models.CharField('BS Converter', max_length=55, null=True)
	bs_switch = models.CharField('BS Switch', max_length=45, null=True)
	pop_converter = models.CharField('POP Converter', max_length=45, null=True)
	count_of_customer = models.CharField('Count Of Customer', max_length=45, null=True)
	technology = models.CharField('Technology', max_length=45, null=True)

class Customer_Count_IPaddress(models.Model):
	sector_config_ip = models.CharField('Sector Config IP', max_length=55, null=True)
	bs_name = models.CharField('BS Name', max_length=55, null=True)
	count_of_customer = models.CharField('Count Of Customer', max_length=55, null=True)
	technology = models.CharField('Technology', max_length=55, null=True)