from string import digits
import types
from celery import task, group
from dateutil.parser import *
from models import GISInventoryBulkImport
from django.contrib.auth.models import User
from machine.models import Machine
import requests
from site_instance.models import SiteInstance
from device.models import Device, DeviceTechnology, DevicePort, DeviceFrequency, DeviceType, ModelType, VendorModel, \
    Country, TechnologyVendor, DeviceVendor, DeviceModel
from inventory.models import Antenna, Backhaul, BaseStation, Sector, Customer, SubStation, Circuit, GISExcelDownload
from organization.models import Organization
from device.models import State, City
from nocout.settings import MEDIA_ROOT, TRAPS_DATABASE
from nocout.tasks import cache_clear_task
from performance.models import InventoryStatus, NetworkStatus, ServiceStatus, Status
from alert_center.models import CurrentAlarms, ClearAlarms
from performance.formulae import display_time
from django.http import HttpRequest
from django.db.models import Q
from IPy import IP
import ipaddr
import shutil
from decimal import *
import os
import re
import time
import xlrd
import xlwt
import datetime
import logging
import copy

# logger = logging.getLogger(__name__)

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task()
def update_sector_frequency_per_day():
    """ Update all sectors/(sector configured on) frequency once a day (daily)

    """
    # fetch all sectors
    sectors = Sector.objects.all()

    # loop through all sectors for updating their frequencies
    for sector in sectors:
        # sector configured on device
        sector_configured_on = sector.sector_configured_on

        # sector configured on device machine name
        machine_name = ""
        try:
            machine_name = sector_configured_on.machine.name
        except Exception as e:
            continue
            # logger.info("Sector configured on machine not found. Exception: ", e.message)

        # polled frequency
        polled_frequency = None
        port_based_frequency = False
        service_name = 'wimax_pmp1_frequency_invent'
        try:
            if sector.sector_configured_on_port and sector.sector_configured_on_port.name:
                port_based_frequency = True
            else:
                port_based_frequency = False

            if port_based_frequency:
                if 'pmp1' in sector.sector_configured_on_port.name.strip().lower():
                    service_name = 'wimax_pmp1_frequency_invent'
                elif 'pmp2' in sector.sector_configured_on_port.name.strip().lower():
                    service_name = 'wimax_pmp2_frequency_invent'

                polled_frequency = InventoryStatus.objects.filter(device_name=sector_configured_on.device_name,
                                                              service_name=service_name,
                                                              data_source='frequency').using(
                                                              alias=machine_name)[0].current_value
            else:
                polled_frequency = InventoryStatus.objects.filter(device_name=sector_configured_on.device_name,
                                                              data_source='frequency').using(
                                                              alias=machine_name)[0].current_value
        except Exception as e:
            # logger.exception("Frequency not exist for sector configured on device ({}).".format(sector_configured_on,
            #                                                                                e.message))
            continue

        frequency_obj = None
        if polled_frequency:
            try:
                # get frequency object
                frequency_obj = DeviceFrequency.objects.filter(value=str(polled_frequency))[0]

                # update sector frequency
                if frequency_obj:
                    sector.frequency = frequency_obj
                    sector.save()
            except:
                # logger.exception("No Frequency Found ({})".format(frequency_obj))
                continue
        else:
            continue

    return True


def get_organization_from_sheet(organization_str):
    """
    This function generates the Organization class object as per the row value
    """
    organization = ''
    try:
        organization = Organization.objects.get(name__iexact=str(organization_str))
    except Exception, e:
        try:
            organization = Organization.objects.get(name__iexact='tcl')
        except Exception, e:
            total_organization = Organization.objects.all().count()
            if total_organization:
                organization = Organization.objects.all()[0]

    return organization


@task()
def validate_gis_inventory_excel_sheet(gis_obj_id, complete_d, sheet_name, keys_list, full_time, filename):
    """ Validate and upload GIS inventory excel workbook for PTP, PMP and WiMAX technologies

        Args:
            gis_obj_id (long) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                                    i.e. 108
            complete_d (str) - list of rows (as dictionary with column name as key and row value as value)
                               from excel sheet i.e.
                               [
                                    {
                                        'City': u'Hyderabad',
                                        'SSBSName': u'ApLodge',
                                        'BSAddress': u'Nampally-AP,
                                        Lodage,
                                        Nampally,
                                        Hyderabad',
                                        'AntennaHeight': '',
                                        'SSRSSIDuringAcceptance': '',
                                        'SSCity': u'Hyderabad',
                                        'PEIP': u'192.168.208.135',
                                        'SSCircuitID': u'091HYDE030007077237',
                                        'Polarization': '',
                                        'SSPolarization': '',
                                        'State': u'AndhraPradesh'
                                    },
                                    {
                                        'City': u'Hyderabad',
                                        'SSBSName': u'ApLodge',
                                        'BSAddress': u'Nampally-AP,
                                        Lodage,
                                        Nampally,
                                        Hyderabad',
                                        'AntennaHeight': '',
                                        'SSRSSIDuringAcceptance': '',
                                        'SSCity': u'Hyderabad',
                                        'PEIP': u'192.168.208.135',
                                        'SSCircuitID': u'091HYDE030007077237',
                                        'Polarization': '',
                                        'SSPolarization': '',
                                        'State': u'AndhraPradesh'
                                    }

                                ]
            sheet_name (unicode) - name of sheet from uploaded excel workbook i.e. u'PTP'
            keys_list (list) - list of columns in excel sheet i.e
                           ['City', 'State', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address',
                           'BS Name', 'QOS (BW)', 'Latitude', 'Longitude', 'MIMO/Diversity', 'Antenna Height',
                           'Polarization', 'Antenna Type', 'Antenna Gain', 'Antenna Mount Type',
                           'Ethernet Extender', 'Building Height', 'Tower/Pole Height', 'Cable Length',
                           'RSSI During Acceptance', 'Throughput During Acceptance', 'Date Of Acceptance',
                           'BH BSO', 'IP', 'MAC', 'HSSU used', 'HSSU Port', 'BS Switch IP', 'Aggregation Switch',
                           'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP', 'Converter Type',
                           'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity',
                           'BH Offnet/Onnet', 'Backhaul Type', 'BSO Circuit ID', 'PE Hostname', 'PE IP',
                           'SS City', 'SS State', 'SS Circuit ID', 'SS Customer Name', 'SS Customer Address',
                           'SS BS Name', 'SS QOS (BW)', 'SS Latitude', 'SS Longitude', 'SS Antenna Height',
                           'SS Polarization', 'SS Antenna Type', 'SS Antenna Mount Type', 'SS Ethernet Extender',
                           'SS Building Height', 'SS Tower/Pole Height', 'SS Cable Length', 'SS RSSI During Acceptance',
                           'SS Throughput During Acceptance', 'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC']

            full_time (str) - timestamp to append in filename i.e. '2014-12-10-13-12-01'
            filename (unicode) - name of uploaded file i.e. u'PTP Few Rows.xls'

        Returns:
            gis_bulk_obj.original_filename (unicode) - name of orinal uploaded file
                                                e.g. u'inventory_files/original/2014-12-10-14-41-52_PTP Few Rows.xls'

    """

    valid_rows_dicts = []
    invalid_rows_dicts = []
    valid_rows_lists = []
    invalid_rows_lists = []
    sheetname = sheet_name
    filename = filename.split(".")[0]
    states_list = [str(state.state_name) for state in State.objects.all()]
    cities_list = [str(city.city_name) for city in City.objects.all()]

    try:
        for d in complete_d:
            # wimax bs and pmp common fields
            if 'City' in d.keys():
                city = d['City']

            if 'State' in d.keys():
                state = d['State']

            if 'Address' in d.keys():
                address = d['Address']

            if 'BS Name' in d.keys():
                bs_name = d['BS Name']

            if 'Type Of BS (Technology)' in d.keys():
                type_of_bs = d['Type Of BS (Technology)']

            if 'Site Type' in d.keys():
                site_type = d['Site Type']

            if 'Infra Provider' in d.keys():
                infra_provider = d['Infra Provider']

            if 'Site ID' in d.keys():
                site_id = str(int(d['Site ID'])) if isinstance(d['Site ID'], float) else str(d['Site ID'])

            if 'Building Height' in d.keys():
                building_height = d['Building Height']

            if 'Tower Height' in d.keys():
                tower_height = d['Tower Height']

            if 'Latitude' in d.keys():
                latitude = d['Latitude']

            if 'Longitude' in d.keys():
                longitude = d['Longitude']

            if 'Sector Name' in d.keys():
                sector_name = d['Sector Name']

            if 'Make Of Antenna' in d.keys():
                if isinstance(d['Make Of Antenna'], int):
                    d['Make Of Antenna'] = "NA"
                    make_of_antenna = "NA"
                else:
                    make_of_antenna = d['Make Of Antenna']

            if 'Polarization' in d.keys():
                polarization = d['Polarization']

            if 'Antenna Tilt' in d.keys():
                antenna_tilt = int(d['Antenna Tilt']) if isinstance(d['Antenna Tilt'], float) else d['Antenna Tilt']

            if 'Antenna Height' in d.keys():
                antenna_height = d['Antenna Height']

            if 'Antenna Beamwidth' in d.keys():
                antenna_beamwidth = int(d['Antenna Beamwidth']) if isinstance(d['Antenna Beamwidth'], float) else d['Antenna Beamwidth']

            if 'Azimuth' in d.keys():
                azimuth = d['Azimuth']

            if 'Installation Of Splitter' in d.keys():
                installation_of_splitter = d['Installation Of Splitter']

            if 'Type Of GPS' in d.keys():
                type_of_gps = d['Type Of GPS']

            if 'BS Switch IP' in d.keys():
                bs_switch_ip = d['BS Switch IP']

            if 'Aggregation Switch' in d.keys():
                aggregation_switch = d['Aggregation Switch']

            if 'Aggregation Switch Port' in d.keys():
                aggregation_switch_port = d['Aggregation Switch Port']

            if 'BS Converter IP' in d.keys():
                bs_converter_ip = d['BS Converter IP']

            if 'POP Converter IP' in d.keys():
                pop_converter_ip = d['POP Converter IP']

            if 'Converter Type' in d.keys():
                converter_type = d['Converter Type']

            if 'BH Configured On Switch/Converter' in d.keys():
                bh_configured_on = d['BH Configured On Switch/Converter']

            if 'Switch/Converter Port' in d.keys():
                switch_or_converter_port = d['Switch/Converter Port']

            if 'BH Capacity' in d.keys():
                bh_capacity = int(d['BH Capacity']) if isinstance(d['BH Capacity'], float) else d['BH Capacity']

            if 'BH Offnet/Onnet' in d.keys():
                bh_off_or_onnet = d['BH Offnet/Onnet']

            if 'Backhaul Type' in d.keys():
                backhaul_type = d['Backhaul Type']

            if 'BH Circuit ID' in d.keys():
                bh_circuit_id = d['BH Circuit ID']

            if 'PE Hostname' in d.keys():
                pe_hostname = d['PE Hostname']

            if 'PE IP' in d.keys():
                pe_ip = d['PE IP']

            if 'BSO Circuit ID' in d.keys():
                bso_circuit_id = d['BSO Circuit ID']

            if 'DR Site' in d.keys():
                dr_site = d['DR Site']

            # wimax fields
            if 'IDU IP' in d.keys():
                idu_ip = d['IDU IP']

            if 'PMP' in d.keys():
                pmp = int(d['PMP']) if isinstance(d['PMP'], float) else d['PMP']

            # pmp bs fields
            if 'Sync Splitter Used' in d.keys():
                sync_splitter_used = d['Sync Splitter Used']

            if 'ODU IP' in d.keys():
                odu_ip = d['ODU IP']

            # ptp bs fields
            if 'Circuit ID' in d.keys():
                ckt_id = d['Circuit ID']

            if 'Circuit Type' in d.keys():
                circuit_type = d['Circuit Type']

            if 'Customer Name' in d.keys():
                customer_name = d['Customer Name']

            if 'BS Address' in d.keys():
                bs_address = d['BS Address']

            if 'QOS (BW)' in d.keys():
                qos_bw = d['QOS (BW)']

            if 'Antenna Type' in d.keys():
                antenna_type = d['Antenna Type']

            if 'Antenna Gain' in d.keys():
                antenna_gain = d['Antenna Gain']

            if 'Antenna Mount Type' in d.keys():
                antenna_mount_type = d['Antenna Mount Type']

            if 'Ethernet Extender' in d.keys():
                ethernet_extender = d['Ethernet Extender']

            if 'Tower/Pole Height' in d.keys():
                tower_pole_height = d['Tower/Pole Height']

            if 'Cable Length' in d.keys():
                cable_length = d['Cable Length']

            if 'RSSI During Acceptance' in d.keys():
                rssi_during_acceptance = d['RSSI During Acceptance']

            if 'Throughput During Acceptance' in d.keys():
                throughput_during_acceptance = d['Throughput During Acceptance']

            if 'Date Of Acceptance' in d.keys():
                date_of_acceptance = d['Date Of Acceptance']

            if 'BH BSO' in d.keys():
                bh_bso = d['BH BSO']

            if 'IP' in d.keys():
                ip = d['IP']

            if 'MAC' in d.keys():
                mac = d['MAC']

            if 'HSSU Used' in d.keys():
                hssu_used = d['HSSU Used']

            if 'HSSU Port' in d.keys():
                hssu_port = d['HSSU Port']

            # pmp sm fields
            if 'SS Mount Type' in d.keys():
                ss_mount_type = d['SS Mount Type']

            if 'CINR During Acceptance' in d.keys():
                cinr_during_acceptance = d['CINR During Acceptance']

            if 'Customer Address' in d.keys():
                customer_address = d['Customer Address']

            if 'Lens/Reflector' in d.keys():
                lens_or_reflector = d['Lens/Reflector']

            if 'Vendor' in d.keys():
                vendor = d['Vendor']

            # errors field for excel sheet validation errors
            errors = ""

            # dropdown lists
            types_of_bs_list = ['WiMAX', 'PTP', 'PMP', 'UBR PMP']
            site_types_list = ['GBT', 'RTT', 'POLE']
            sectors_list = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8']
            antenna_mount_types_list = ['GBT', 'RTT', 'POLE']
            infra_provider_list = ['TVI', 'VIOM', 'INDUS', 'ATC', 'IDEA', 'QUIPPO', 'SPICE', 'TTML', 'TCL', 'TOWER VISION', 'RIL', 'WTTIL', 'OTHER']
            make_of_antenna_list = ['MTI H Pol', 'Xhat', 'Andrew', 'MTI', 'Twin', 'Proshape', 'Integrated']
            antenna_polarisation_list = ['Vertical', 'Horizontal', 'Cross', 'Dual']
            antenna_tilt_list = range(1, 11)           # 1.....10
            antenna_type_list = ['Narrow Beam', 'External', 'Normal', 'Internal', 'Integrated']
            types_of_gps_list = ['PCTEL', 'AQTIME']
            ss_mount_type_list = ['Wall mount', 'Pole mount', 'Mast', 'Window Mount', 'Grill Mount', 'Pole']
            bh_off_or_onnet_list = ['OFFNET', 'ONNET', 'OFFNET+ONNET', 'OFFNET+ONNET UBR', 'ONNET+UBR', 'ONNET COLO', 'ONNET COLO+UBR']
            backhaul_type_list = ['SDH', 'Ethernet', 'E1', 'EoSDH', 'Dark Fibre', 'UBR']
            pmp_list = [1, 2]
            circuit_types_list = ['BH', 'Customer']
            converter_types_list = ['RICI', 'PINE']
            azimuth_angles_list = range(0, 361)                 # 0.......360
            building_height_list = range(0, 100)                # 0.......99
            tower_height_list = range(0, 100)                   # 0.......99
            antenna_height_list = range(0, 100)                 # 0.......99
            yes_or_no = ['Yes', 'No', 'Y', 'N']
            lens_or_reflectors_list = ['Lens', 'Reflector']
            dr_site_list = ['Yes', 'No', 'Y', 'N']

            # regex for checking whether string contains only numbers and .(dot)
            regex_numbers_and_single_dot = '^[0-9]*\\.?[0-9]*$'
            # regex_upto_two_dec_places = '^\d{1,9}($|\.\d{1,2}$)'
            regex_upto_two_dec_places = '^\d+($|\.\d{1,2}$)'
            regex_ip_address = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
            regex_alnum_comma_hyphen_fslash_underscore_space = '^[a-zA-Z0-9\s,_/-]+$'
            regex_alnum_comma_fslash = '^[a-zA-Z0-9,/]+$'
            regex_alnum_pipe_fslash = '^[a-zA-Z0-9|/]+$'
            regex_alnum_pipe = '^[a-zA-Z0-9|]+$'
            regex_alnum_underscore = '^[a-zA-Z0-9_]+$'
            regex_alnum_comma_underscore_space = '^[a-zA-Z0-9,\s_]+$'
            regex_alpha_underscore = '^[a-zA-Z_]+$'
            regex_alpha_space = '^[a-zA-Z\s]+$'
            regex_alnum_comma_underscore_space = '^[a-zA-Z0-9\s,_]+$'
            regex_alnum_comma_underscore_space_asterisk = '^[a-zA-Z0-9\s,\*_]+$'
            regex_alnum_hyphen = '^[a-zA-Z0-9-]+$'
            regex_alnum_space = '^[a-zA-Z0-9\s]+$'
            regex_mac = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            regex_lat_long = '^[-+]?\d*\.\d+|\d+'

            # wimax bs and pmp common fields validations
            # 'city' validation (must be alphabetical and can contain space)
            try:
                if city:
                    if str(city).strip() not in cities_list:
                        errors += '{} is not valid option for city.\n'.format(city)
                else:
                    errors += 'City must not be empty.\n'
            except Exception as e:
                pass

            # 'state' validation (must be alphabetical and can contain space)
            try:
                if state:
                    if str(state).strip() not in states_list:
                        errors += '{} is not valid option for state.\n'.format(state)
                else:
                    errors += 'State must not be empty.\n'
            except Exception as e:
                pass

            # 'address' must not be empty
            try:
                if address:
                    if not address:
                        errors += 'Address must not be empty.\n'
            except Exception as e:
                pass

            # 'bs name' must not be empty
            try:
                if bs_name:
                    if not bs_name:
                        errors += 'BS Name must not be empty.\n'
            except Exception as e:
                pass

            # 'type of bs' validation (must be from provided list)
            try:
                if type_of_bs:
                    if str(type_of_bs).strip().lower() not in [x.lower() for x in types_of_bs_list]:
                        errors += '{} is not valid option for bs type.\n'.format(type_of_bs)
                else:
                    errors += 'Type of BS must not be empty.\n'
            except Exception as e:
                pass

            # 'site type' validation (must be from provided list)
            try:
                if site_type:
                    if str(site_type).strip().lower() not in [x.lower() for x in site_types_list]:
                        errors += '{} is not a valid option for site type.\n'.format(site_type)
                else:
                    errors += 'Site type must not be empty.\n'
            except Exception as e:
                pass

            # 'infra provider' validation (must be from provided list)
            try:
                if infra_provider:
                    if str(infra_provider).strip().lower() not in [x.lower() for x in infra_provider_list]:
                        errors += '{} is not a valid option for infra provider.\n'.format(infra_provider)
                else:
                    errors += 'Infra provider must not be empty.\n'
            except Exception as e:
                pass

            # 'site id' must not be empty
            try:
                if site_id:
                    if not site_id:
                        errors += 'Site ID must not be empty.\n'
            except Exception as e:
                pass

            # 'building height' validation (must be in range 0-99)
            try:
                if isinstance(building_height, int) or isinstance(building_height, float):
                    if int(building_height) not in building_height_list:
                        errors += 'Building Height must be in range 0-99.\n'
                elif isinstance(building_height, str):
                    errors += 'Building height must be a number.\n'
                else:
                    errors += 'Building Height must not be empty.\n'
            except Exception as e:
                pass

            # 'tower height' validation (must be in range 0-99)
            try:
                if isinstance(tower_height, int) or isinstance(tower_height, float):
                    if int(tower_height) not in tower_height_list:
                        errors += 'Tower Height must be in range 0-99.\n'
                elif isinstance(tower_height, str):
                    errors += 'Tower Height must be a number.\n'
                else:
                    errors += 'Tower Height must not be empty.\n'
            except Exception as e:
                pass

            # 'latitude' validation
            try:
                if latitude:
                    if not re.match(regex_lat_long, str(latitude).strip()):
                        errors += 'Latitude value is wrong.\n'
                else:
                    errors += 'Latitude must not be empty.\n'
            except Exception as e:
                pass

            # 'longitude' validation
            try:
                if longitude:
                    if not re.match(regex_lat_long, str(longitude).strip()):
                        errors += 'Longitude value is wrong.\n'
                else:
                    errors += 'Longitude must not be empty.\n'
            except Exception as e:
                pass

            # 'sector name' validation (must be from provided list)
            try:
                if sector_name:
                    if str(sector_name).strip().lower() not in [x.lower() for x in sectors_list]:
                        errors += '{} is not a valid option for sector name.\n'.format(sector_name)
                else:
                    errors += 'Sector Name must not be empty.\n'
            except Exception as e:
                pass

            # 'make of antenna' validation (must be form provided list)
            try:
                if make_of_antenna:
                    if str(make_of_antenna).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if str(make_of_antenna).strip().lower() not in [x.lower() for x in make_of_antenna_list]:
                            errors += '{} is not a valid option for make of antenna.\n'.format(make_of_antenna)
            except Exception as e:
                pass

            # 'polarization' validation (must be from provided list)
            try:
                if polarization:
                    if str(polarization).strip().lower() not in [x.lower() for x in antenna_polarisation_list]:
                        errors += '{} is not a valid option for polarization.\n'.format(polarization)
                else:
                    errors += 'Antenna polarization must not be empty.\n'
            except Exception as e:
                pass

            # 'antenna tilt' validation (must be from 1-10)
            try:
                if isinstance(antenna_tilt, int) or isinstance(antenna_tilt, float):
                    if int(antenna_tilt) not in [x for x in antenna_tilt_list]:
                        errors += 'Antenna Tilt must be in range from 1-10.\n'
                else:
                    errors += 'Antenna Tilt must not be empty.\n'
            except Exception as e:
                pass

            # 'antenna height' validation (must be in range 0-99)
            try:
                if isinstance(antenna_height, int) or isinstance(antenna_height, float):
                    if int(antenna_height) not in antenna_height_list:
                        errors += 'Antenna Height must be in range 0-99.\n'
                elif isinstance(antenna_height, str):
                    errors += "Antenna Height must be a number.\n"
                else:
                    errors += 'Antenna Height must not be empty.\n'
            except Exception as e:
                pass

            # 'antenna beamwidth' validation (must be numeric)
            try:
                if isinstance(antenna_beamwidth, int) or isinstance(antenna_beamwidth, float):
                    if not re.match(regex_upto_two_dec_places, str(antenna_beamwidth).strip()):
                        errors += 'Antenna Beamwidth must be a number.\n'
                elif isinstance(antenna_beamwidth, str):
                    errors += 'Antenna Beamwidth must be a number.\n'
                else:
                    errors += 'Antenna Beamwidth must not be empty.\n'
            except Exception as e:
                pass

            # 'azimuth' validation (must be in range 0-360)
            try:
                if isinstance(azimuth, int) or isinstance(azimuth, float):
                    if int(azimuth) not in azimuth_angles_list:
                        errors += 'Azimuth must be in range 0-360.\n'
                else:
                    errors += 'Azimuth must not be empty.\n'
            except Exception as e:
                pass

            # 'installation of splitter' validation (must be 'Yes' or 'No')
            try:
                if installation_of_splitter:
                    if str(installation_of_splitter).strip().lower() not in [x.lower() for x in yes_or_no]:
                        errors += 'Installation of splitter must be from \'Yes\' or \'No\'.\n'
                else:
                    errors += 'Installation of splitter must not be empty.\n'
            except Exception as e:
                pass

            # 'types of gps' validation (must be form provided list)
            try:
                if type_of_gps:
                    if str(bs_switch_ip).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if str(type_of_gps).strip().lower() not in [x.lower() for x in types_of_gps_list]:
                            errors += '{} is not a valid option for type of gps.\n'.format(type_of_gps)
            except Exception as e:
                pass

            # 'bs switch ip' validation (must be an ip address)
            try:
                if bs_switch_ip:
                    if str(bs_switch_ip).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_ip_address, bs_switch_ip.strip()):
                            errors += 'BS Switch IP {} must be an ip address.\n'.format(bs_switch_ip)
                else:
                    errors += 'BS switch IP must not be empty.\n'
            except Exception as e:
                pass

            # 'aggregation switch' validation (must be an ip address)
            try:
                if aggregation_switch:
                    if str(aggregation_switch).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_ip_address, aggregation_switch.strip()):
                            errors += 'Aggregation Switch must be an ip address.\n'
            except Exception as e:
                pass

            # 'aggregation switch port' validation (can only contains alphanumeric, comma, forward slash)
            try:
                if aggregation_switch_port:
                    if str(aggregation_switch_port).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_alnum_pipe, aggregation_switch_port.strip()):
                            errors += 'Aggregation Switch Port can only contains alphanumeric, comma, forward slash.\n'
            except Exception as e:
                pass

            # 'bs converter ip' validation (must be an ip address)
            try:
                if bs_converter_ip:
                    if str(bs_converter_ip).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_ip_address, bs_converter_ip.strip()):
                            errors += 'BS Converter IP must be an ip address.\n'
                else:
                    errors += 'BS Converter IP must not be empty.\n'
            except Exception as e:
                pass

            # 'pop conveter ip' validation (must be an ip address)
            try:
                if pop_converter_ip:
                    if str(pop_converter_ip).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_ip_address, pop_converter_ip.strip()):
                            errors += 'POP Converter IP must be an ip address.\n'
            except Exception as e:
                pass

            # 'converter type' validation (must be form provided list)
            try:
                if converter_type:
                    if str(converter_type).strip().lower() not in [x.lower() for x in converter_types_list]:
                        errors += '{} is not a valid option for converter type.\n'.format(converter_type)
                else:
                    errors += 'Converter Type must not be empty.\n'
            except Exception as e:
                pass

            # 'bh configured on' validation (must be an ip address)
            try:
                if bh_configured_on:
                    if not re.match(regex_ip_address, bh_configured_on.strip()):
                        errors += 'BH Configured On must be an ip address.\n'
                else:
                    errors += 'BH Configured On must not be empty.\n'
            except Exception as e:
                pass

            # 'switch or converter port' validation (can only contains alphanumeric, comma, forward slash)
            try:
                if switch_or_converter_port:
                    if not re.match(regex_alnum_pipe, switch_or_converter_port.strip()):
                        errors += 'Switch/Converter Port {} can only contains alphanumeric, comma, forward slash.\n'.format(switch_or_converter_port)
                else:
                    errors += 'Switch/Converter Port must not be empty.\n'
            except Exception as e:
                pass

            # 'bh capacity' validation (must be numeric)
            try:
                if isinstance(bh_capacity, int) or isinstance(bh_capacity, float):
                    if not re.match(regex_upto_two_dec_places, str(bh_capacity).strip()):
                        errors += 'BH Capacity must be a number.\n'
                elif isinstance(bh_capacity, str) or isinstance(bh_capacity, unicode):
                    errors += 'BH Capactiy must be a number.\n'
                else:
                    errors += 'BH Capactiy must not be empty.\n'
            except Exception as e:
                pass

            # 'bh off or onnet' validation (must be from provided list)
            try:
                if bh_off_or_onnet:
                    if str(bh_off_or_onnet).strip().lower() not in [x.lower() for x in bh_off_or_onnet_list]:
                        errors += '{} is not a valid option for bh off or onnet.\n'.format(bh_off_or_onnet)
                else:
                    errors += 'BH Offnet/Onnet must not be empty.\n'
            except Exception as e:
                pass

            # 'backhaul type' validation (must be from provided list)
            try:
                if backhaul_type:
                    if str(backhaul_type).strip().lower() not in [x.lower() for x in backhaul_type_list]:
                        errors += '{} is not a valid option for backhaul type.\n'.format(backhaul_type)
            except Exception as e:
                pass

            # 'pe hostname' validation (can only contains alphanumerics and hyphen)
            try:
                if pe_hostname:
                    if not re.match(regex_alnum_hyphen, pe_hostname.strip()):
                        errors += 'PE Hostname can only contains alphanumerics and hyphen.\n'
                else:
                    errors += 'PE Hostname must not be empty.\n'
            except Exception as e:
                pass

            # 'pe ip' validation (must be an ip address)
            try:
                if pe_ip:
                    if not re.match(regex_ip_address, pe_ip.strip()):
                        errors += 'PE IP must be an ip address.\n'
                else:
                    errors += 'PE IP must not be empty.\n'
            except Exception as e:
                pass

            # 'dr site' validation (must be 'Yes' or 'No')
            try:
                if dr_site:
                    if str(dr_site).strip().lower() not in [x.lower() for x in dr_site_list]:
                        errors += 'DR Site {} must be from \'Yes\' or \'No\'.\n'.format(dr_site)
            except Exception as e:
                pass

            # wimax fields validations ****************************************************
            # 'idu ip' validation (must be an ip address)
            try:
                if idu_ip:
                    if not re.match(regex_ip_address, idu_ip.strip()):
                        errors += 'IDU IP must be an ip address.\n'
                else:
                    errors += 'IDU IP must not be empty.\n'
            except Exception as e:
                pass

            # 'pmp' validation (must be from provided list)
            try:
                if pmp and isinstance(pmp, int):
                    if pmp not in pmp_list:
                        errors += '{} is not a valid option for pmp.\n'.format(pmp)
                else:
                    errors += 'PMP must not be empty.\n'
            except Exception as e:
                pass

            # pmp fields validations *********************************************************
            # 'sync splitter used' validation (must be 'Yes' or 'No')
            try:
                if sync_splitter_used:
                    if str(sync_splitter_used).strip().lower() not in [x.lower() for x in yes_or_no]:
                        errors += 'Sync splitter used must be from \'Yes\' or \'No\'.\n'
                else:
                    errors += 'Sync splitter used must not be empty.\n'
            except Exception as e:
                pass

            # 'odu ip' validation (must be an ip address)
            try:
                if odu_ip:
                    if not re.match(regex_ip_address, odu_ip.strip()):
                        errors += 'ODU IP must be an ip address.\n'
                else:
                    errors += 'ODU IP must not be empty.\n'
            except Exception as e:
                pass

            # ptp bs fields validations *******************************************************
            # 'ckt id' validation (can only contains alphanumeric, underscore)
            try:
                if ckt_id:
                    if str(ckt_id).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_alnum_underscore, ckt_id.strip()):
                            errors += 'Circuit ID can only contains alphanumerics and underscore.\n'
            except Exception as e:
                pass

            # 'circuit type' validation (must be from provided list)
            try:
                if circuit_type:
                    if str(circuit_type).strip().lower() not in [x.lower() for x in circuit_types_list]:
                        errors += '{} is not a valid option for circuit type.\n'.format(circuit_type)
                else:
                    errors += 'Polarization must not be empty.\n'
            except Exception as e:
                pass

            # 'customer name' must not be empty
            try:
                if customer_name:
                    if not customer_name:
                        errors += 'Customer Name must not be empty.\n'
            except Exception as e:
                pass

            # 'bs address' must not be empty
            try:
                if bs_address:
                    if not bs_address:
                        errors += 'BS Address must not be empty.\n'
            except Exception as e:
                pass

            # 'qos_bw' validation (must be numeric)
            try:
                if isinstance(qos_bw, int) or isinstance(qos_bw, float):
                    pass
                elif isinstance(qos_bw, str) or isinstance(qos_bw, unicode):
                    errors += 'QOS (BW) must be a number.\n'
                else:
                    errors += 'QOS (BW) must not be empty.\n'
            except Exception as e:
                pass

            # 'antenna type' validation (must be from provided list)
            try:
                if antenna_type:
                    if str(antenna_type).strip().lower() not in [x.lower() for x in antenna_type_list]:
                        errors += '{} is not a valid option for antenna type.\n'.format(antenna_type)
            except Exception as e:
                pass

            # 'antenna gain' validation (must be a number)
            try:
                if isinstance(antenna_gain, int) or isinstance(antenna_gain, float):
                    pass
                elif isinstance(antenna_gain, str) or isinstance(antenna_gain, unicode):
                    errors += 'Antenna Gain must be a number.\n'
                else:
                    pass
            except Exception as e:
                pass

            # 'antenna mount type' validation (must be from provided list)
            try:
                if antenna_mount_type:
                    if str(antenna_mount_type).strip().lower() not in [x.lower() for x in antenna_mount_types_list]:
                        errors += '{} is not a valid option for antenna mount type.\n'.format(antenna_mount_type)
            except Exception as e:
                pass

            # 'ethernet extender' validation (must be 'Yes' or 'No')
            try:
                if ethernet_extender:
                    if str(ethernet_extender).strip().lower() not in [x.lower() for x in yes_or_no]:
                        errors += 'Ethernet extender must be from \'Yes\' or \'No\'.\n'
            except Exception as e:
                pass

            # 'tower/pole height' validation (must be in range 0-99)
            try:
                if isinstance(tower_pole_height, int) or isinstance(tower_pole_height, float):
                    if int(tower_pole_height) not in tower_height_list:
                        errors += 'Tower/Pole Height must be in range 0-99.\n'
                elif isinstance(tower_pole_height, str):
                    errors += "Tower/Pole Height must be a number.\n"
                else:
                    errors += 'Tower/Pole Height must not be empty.\n'
            except Exception as e:
                pass

            # 'cable length' validation (must be upto 2 decimal places)
            try:
                if isinstance(cable_length, int) or isinstance(cable_length, float):
                    if not re.match(regex_upto_two_dec_places, str(cable_length).strip()):
                        errors += 'Cable Length must be a number.\n'
                elif cable_length:
                    if not re.match(regex_upto_two_dec_places, str(cable_length).strip()):
                        errors += 'Cable Length must be a number.\n'
                else:
                    errors += 'Cable Length must not be empty.\n'
            except Exception as e:
                pass

            # 'rssi during acceptance' validation (must be a -ve number)
            try:
                if rssi_during_acceptance:
                    if rssi_during_acceptance > 0:
                        errors += 'RSSI During Acceptance must be a negative number.\n'.format(rssi_during_acceptance)
            except Exception as e:
                pass

            # 'throughput during acceptance' validation (must be a +ve number)
            try:
                if throughput_during_acceptance:
                    if throughput_during_acceptance < 0:
                        errors += 'Throughput During Acceptance must be a positive number.\n'.format(throughput_during_acceptance)
            except Exception as e:
                pass

            # 'date of acceptance' validation (must be like '15-Aug-2014')
            try:
                if date_of_acceptance:
                    try:
                        datetime.datetime.strptime(date_of_acceptance, '%d-%b-%Y')
                    except Exception as e:
                        errors += 'Date Of Acceptance must be like (15-Aug-2014).\n'
            except Exception as e:
                pass

            # 'ip' validation (must be an ip address)
            try:
                if ip:
                    if not re.match(regex_ip_address, ip.strip()):
                        errors += 'IP must be an ip address.\n'
                else:
                    errors += 'IP must not be empty.\n'
            except Exception as e:
                pass

            # 'mac' validation
            try:
                if mac:
                    if not re.match(regex_mac, str(mac).strip()):
                        errors += 'MAC must be a mac address.\n'
                else:
                    errors += 'MAC must not be empty.\n'
            except Exception as e:
                pass

            # 'hssu used' validation (must be from provided list)
            try:
                if hssu_used:
                    if str(hssu_used).strip().lower() not in [x.lower() for x in yes_or_no]:
                        errors += '{} is not a valid option for hssu used.\n'.format(hssu_used)
            except Exception as e:
                pass

            # 'hssu port' validation (can only contains alphanumeric, comma, forward slash)
            try:
                if hssu_port:
                    if str(hssu_port).strip().lower() not in [x.lower() for x in 'NA', 'N/A']:
                        if not re.match(regex_alnum_pipe, hssu_port.strip()):
                            errors += 'HSSU Port can only contains alphanumeric, comma, forward slash.\n'
            except Exception as e:
                pass

            # pmp sm fields validations ****************************************************
            # 'ss_mount_type' validation (must be from provided list)
            try:
                if ss_mount_type:
                    if str(ss_mount_type).strip().lower() not in [x.lower() for x in ss_mount_type_list]:
                        errors += '{} is not a valid option for ss mount type.\n'.format(ss_mount_type)
            except Exception as e:
                pass

            # 'cinr during acceptance' validation (must be a +ve number)
            try:
                if cinr_during_acceptance:
                    if cinr_during_acceptance < 0:
                        errors += 'CINR During Acceptance must be a positive number.\n'.format(cinr_during_acceptance)
            except Exception as e:
                pass

            # 'customer address' must not be empty
            try:
                if customer_address:
                    if not customer_address:
                        errors += 'Customer Address must not be empty.\n'
            except Exception as e:
                pass

            # 'lens or reflector' validation (must be from provided list)
            try:
                if lens_or_reflector:
                    if str(lens_or_reflector).strip().lower() not in [x.lower() for x in lens_or_reflectors_list]:
                        errors += '{} is not a valid option for lens/reflector.\n'.format(lens_or_reflector)
            except Exception as e:
                pass

            # 'vendor' validation
            try:
                if vendor:
                    if not re.match(regex_alpha_space, str(vendor).strip()):
                        errors += 'Vendor must be alphabetical and can contain spaces.\n'
            except Exception as e:
                pass

            # ptp ss validation
            if sheet_name == "PTP":
                if 'SS City' in d.keys():
                    ss_city = d['SS City']

                if 'SS State' in d.keys():
                    ss_state = d['SS State']

                if 'SS Circuit ID' in d.keys():
                    ss_ckt_id = d['SS Circuit ID']

                if 'SS Customer Name' in d.keys():
                    ss_customer_name = d['SS Customer Name']

                if 'SS Customer Address' in d.keys():
                    ss_customer_address = d['SS Customer Address']

                if 'SS BS Name' in d.keys():
                    ss_bs_name = d['SS BS Name']

                if 'SS QOS (BW)' in d.keys():
                    ss_qos_bw = d['SS QOS (BW)']

                if 'SS Latitude' in d.keys():
                    ss_latitude = d['SS Latitude']

                if 'SS Longitude' in d.keys():
                    ss_longitude = d['SS Longitude']

                if 'SS Antenna Height' in d.keys():
                    ss_antenna_height = d['SS Antenna Height']

                if 'SS Polarisation' in d.keys():
                    ss_polarization = d['SS Polarisation']

                if 'SS Antenna Type' in d.keys():
                    ss_antenna_type = d['SS Antenna Type']

                if 'SS Antenna Gain' in d.keys():
                    ss_antenna_gain = d['SS Antenna Gain']

                if 'SS Antenna Mount Type' in d.keys():
                    ss_antenna_mount_type = d['SS Antenna Mount Type']

                if 'SS Ethernet Extender' in d.keys():
                    ss_ethernet_extender = d['SS Ethernet Extender']

                if 'SS Building Height' in d.keys():
                    ss_building_height = d['SS Building Height']

                if 'SS Tower/Pole Height' in d.keys():
                    ss_tower_pole_height = d['SS Tower/Pole Height']

                if 'SS Cable Length' in d.keys():
                    ss_cable_length = d['SS Cable Length']

                if 'SS RSSI During Acceptance' in d.keys():
                    ss_rssi_during_acceptance = d['SS RSSI During Acceptance']

                if 'SS Throughput During Acceptance' in d.keys():
                    ss_throughput_during_acceptance = d['SS Throughput During Acceptance']

                if 'SS Date Of Acceptance' in d.keys():
                    ss_date_of_acceptance = d['SS Date Of Acceptance']

                if 'SS BH BSO' in d.keys():
                    ss_bh_bso = d['SS BH BSO']

                if 'SS IP' in d.keys():
                    ss_ip = d['SS IP']

                if 'SS MAC' in d.keys():
                    ss_mac = d['MAC']

                if 'SS MIMO/Diversity' in d.keys():
                    ss_mimo = d['SS MIMO/Diversity']

                # 'ss city' validation (must be alphabetical and can contain space)
            try:
                if ss_city:
                    if str(ss_city).strip() not in cities_list:
                        errors += '{} is not valid option for ss city.\n'.format(ss_city)
                else:
                    errors += 'SS City must not be empty.\n'
            except Exception as e:
                pass

                # 'ss state' validation (must be alphabetical and can contain space)
                try:
                    if ss_state:
                        if str(ss_state).strip() not in states_list:
                            errors += '{} is not valid option for ss state.\n'.format(ss_state)
                    else:
                        errors += 'SS State must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss circuit id' must not be empty
                try:
                    if ss_ckt_id:
                        if not ss_ckt_id:
                            errors += 'SS Circuit ID must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss customer name' must not be empty
                try:
                    if ss_customer_name:
                        if not ss_customer_name:
                            errors += 'SS Customer Name must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss customer address' must not be empty
                try:
                    if ss_customer_address:
                        if not ss_customer_address:
                            errors += 'SS Customer Address must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss bs name' must not be empty
                try:
                    if ss_bs_name:
                        if not ss_bs_name:
                            errors += 'SS BS Name must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss qos bw' validation (must be numeric)
                try:
                    if isinstance(ss_qos_bw, int) or isinstance(ss_qos_bw, float):
                        pass
                    elif ss_qos_bw:
                        if not re.match(regex_upto_two_dec_places, str(ss_qos_bw).strip()):
                            errors += 'SS QOS (BW) must be a number.\n'
                    else:
                        errors += 'SS QOS (BW) must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss latitude' validation
                try:
                    if ss_latitude:
                        if not re.match(regex_lat_long, str(ss_latitude).strip()):
                            errors += 'SS Latitude value is wrong.\n'
                    else:
                        errors += 'SS Latitude must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss longitude' validation
                try:
                    if ss_longitude:
                        if not re.match(regex_lat_long, str(ss_longitude).strip()):
                            errors += 'SS Longitude value is wrong.\n'
                    else:
                        errors += 'SS Longitude must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss antenna height' validation (must be in range 0-99)
                try:
                    if isinstance(ss_antenna_height, int) or isinstance(ss_antenna_height, float):
                        if int(ss_antenna_height) not in antenna_height_list:
                            errors += 'SS Antenna Height must be in range 0-99.\n'
                    elif isinstance(ss_antenna_height, str):
                        errors += "SS Antenna Height must be a number.\n"
                    else:
                        errors += 'SS Antenna Height must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss antenna polarisation' validation (must be from provided list)
                try:
                    if ss_polarization:
                        if str(ss_polarization).strip().lower() not in [x.lower() for x in antenna_polarisation_list]:
                            errors += '{} is not a valid option for ss polarization.\n'.format(ss_polarization)
                    else:
                        errors += 'SS Polarization must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss antenna type' validation (must be from provided list)
                try:
                    if ss_antenna_type:
                        if str(ss_antenna_type).strip().lower() not in [x.lower() for x in antenna_type_list]:
                            errors += '{} is not a valid option for ss antenna type.\n'.format(ss_antenna_type)
                except Exception as e:
                    pass

                # 'ss antenna gain' validation (must be a number)
                try:
                    if ss_antenna_gain:
                        if isinstance(ss_antenna_gain, int) or isinstance(ss_antenna_gain, float):
                            pass
                        else:
                            errors += 'SS Antenna Gain must be a number.\n'
                except Exception as e:
                    pass

                # 'ss antenna mount type' validation (must be from provided list)
                try:
                    if ss_antenna_mount_type:
                        if str(ss_antenna_mount_type).strip().lower() not in [x.lower() for x in antenna_mount_types_list]:
                            errors += '{} is not a valid option for ss antenna mount type.\n'.format(ss_antenna_mount_type)
                except Exception as e:
                    pass

                # 'ss ethernet extender' validation (must be 'Yes' or 'No')
                try:
                    if ss_ethernet_extender:
                        if str(ss_ethernet_extender).strip().lower() not in [x.lower() for x in yes_or_no]:
                            errors += 'SS Ethernet extender must be from \'Yes\' or \'No\'.\n'
                except Exception as e:
                    pass

                # 'ss building height' validation (must be in range 0-99)
                try:
                    if isinstance(ss_building_height, int) or isinstance(ss_building_height, float):
                        if int(ss_building_height) not in building_height_list:
                            errors += 'SS Building Height must be in range 0-99.\n'
                    elif isinstance(ss_building_height, str):
                        errors += 'SS Building Height must be a number.\n'
                    else:
                        errors += 'SS Building Height must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss tower or pole height' validation (must be in range 0-99)
                try:
                    if isinstance(ss_tower_pole_height, int) or isinstance(ss_tower_pole_height, float):
                        if int(ss_tower_pole_height) not in tower_height_list:
                            errors += 'SS Tower/Pole Height must be in range 0-99.\n'
                    elif isinstance(ss_tower_pole_height, str):
                        errors += 'SS Tower/Pole Height must be a number.\n'
                    else:
                        errors += 'SS Tower/Pole Height must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss cable length' validation (must be upto 2 decimal places)
                try:
                    if isinstance(ss_cable_length, int) or isinstance(ss_cable_length, float):
                        pass
                    elif isinstance(ss_cable_length, str) or isinstance(ss_cable_length, unicode):
                        errors += 'SS Cable Length must be a number.\n'
                    else:
                        errors += 'SS Cable Length must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss rssi during acceptance' validation (must be -ve number)
                try:
                    if ss_rssi_during_acceptance:
                        if ss_rssi_during_acceptance > 0:
                            errors += 'SS RSSI During Acceptance must be negative number.\n'.format(ss_rssi_during_acceptance)
                except Exception as e:
                    pass

                # 'ss throughput during acceptance' validation (must be +ve number)
                try:
                    if ss_throughput_during_acceptance:
                        if ss_throughput_during_acceptance < 0:
                            errors += 'SS Throughput During Acceptance must be a positive number.\n'.format(ss_throughput_during_acceptance)
                except Exception as e:
                    pass

                # # 'ss date of acceptance' validation (must be like '15-Aug-2014')
                # try:
                #     if ss_date_of_acceptance:
                #         try:
                #             datetime.datetime.strptime(ss_date_of_acceptance, '%d-%b-%Y')
                #         except Exception as e:
                #             errors += 'SS Date Of Acceptance must be like (15-Aug-2014).\n'
                # except Exception as e:
                #     pass

                # 'ss ip' validation (must be an ip address)
                try:
                    if ss_ip:
                        if not re.match(regex_ip_address, ss_ip.strip()):
                            errors += 'SS IP must be an ip address.\n'
                    else:
                        errors += 'SS IP must not be empty.\n'
                except Exception as e:
                    pass

                # 'ss mac' validation
                try:
                    if ss_mac:
                        if not re.match(regex_mac, str(ss_mac).strip()):
                            errors += 'SS MAC must be a mac address.\n'
                    else:
                        errors += 'SS MAC must not be empty.\n'
                except Exception as e:
                    pass

            # insert key 'errors' in dict 'd'
            d['Errors'] = errors

            # check whether there are errors exist or not
            try:
                if not errors:
                    valid_rows_dicts.append(d)
                else:
                    invalid_rows_dicts.append(d)
            except Exception as e:
                pass

        # append errors key in keys_list
        keys_list.append('Errors')
        for val in valid_rows_dicts:
            temp_list = list()
            for key in keys_list:
                temp_list.append(val[key])
            valid_rows_lists.append(temp_list)

        for val in invalid_rows_dicts:
            temp_list = list()
            for key in keys_list:
                temp_list.append(val[key])
            invalid_rows_lists.append(temp_list)

        headers = keys_list

        wb_valid = xlwt.Workbook()
        ws_valid = wb_valid.add_sheet(sheetname)

        wb_invalid = xlwt.Workbook()
        ws_invalid = wb_invalid.add_sheet(sheetname)

        style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')
        style_errors = xlwt.easyxf('pattern: pattern solid, fore_colour red;' 'font: colour white, bold True;')

        try:
            for i, col in enumerate(headers):
                if col != 'Errors':
                    ws_valid.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
                else:
                    ws_valid.write(0, i, col.decode('utf-8', 'ignore').strip(), style_errors)
        except Exception as e:
            pass

        try:
            for i, l in enumerate(valid_rows_lists):
                i += 1
                for j, col in enumerate(l):
                    ws_valid.write(i, j, col)
        except Exception as e:
            pass

        try:
            for i, col in enumerate(headers):
                if col != 'Errors':
                    ws_invalid.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
                else:
                    ws_invalid.write(0, i, col.decode('utf-8', 'ignore').strip(), style_errors)
        except Exception as e:
            pass

        try:
            for i, l in enumerate(invalid_rows_lists):
                i += 1
                for j, col in enumerate(l):
                    ws_invalid.write(i, j, col)
        except Exception as e:
            pass

        # if directory for valid excel sheets didn't exist than create one
        if not os.path.exists(MEDIA_ROOT + 'inventory_files/valid'):
            os.makedirs(MEDIA_ROOT + 'inventory_files/valid')

        # if directory for invalid excel sheets didn't exist than create one
        if not os.path.exists(MEDIA_ROOT + 'inventory_files/invalid'):
            os.makedirs(MEDIA_ROOT + 'inventory_files/invalid')

        wb_valid.save(MEDIA_ROOT + 'inventory_files/valid/{}_valid_{}.xls'.format(full_time, filename))
        wb_invalid.save(MEDIA_ROOT + 'inventory_files/invalid/{}_invalid_{}.xls'.format(full_time, filename))
        gis_bulk_obj = GISInventoryBulkImport.objects.get(pk=gis_obj_id)
        try:
            gis_bulk_obj.valid_filename = 'inventory_files/valid/{}_valid_{}.xls'.format(full_time, filename)
            gis_bulk_obj.invalid_filename = 'inventory_files/invalid/{}_invalid_{}.xls'.format(full_time, filename)
        except Exception as e:
            logger.info(e.message)
        gis_bulk_obj.status = 1
        gis_bulk_obj.save()
        return gis_bulk_obj.original_filename
    except Exception as e:
        gis_bulk_obj = GISInventoryBulkImport.objects.get(pk=gis_obj_id)
        gis_bulk_obj.status = 2
        gis_bulk_obj.save()
        logger.info(e.message)


@task()
def bulk_upload_ptp_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading PTP inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """

    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] in ["Date Of Acceptance", "SS Date Of Acceptance"]:
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get 'pub' machine and associated sites details in dictionary
    # pass machine name as argument
    pub_machine_and_site_info = get_machine_details('pub')

    # get 'vrfprv' machine and associated sites details in dictionary
    # pass machine name as argument
    vrfprv_machine_and_site_info = get_machine_details('vrfprv')

    # get 'ospf5' machine and associated sites in a dictionary
    # pass machine name and list of machines postfix i.e [1, 3, 4, 5] for 'ospf1' and 'ospf5' as argument
    ospf1_machine_and_site_info = get_machine_details('ospf', [1])
    ospf4_ospf3_machine_and_site_info = get_machine_details('ospf', [4, 3])
    ospf4_ospf5_machine_and_site_info = get_machine_details('ospf', [4, 5])
    ospf5_machine_and_site_info = get_machine_details('ospf', [5])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:
            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            bs_switch_tech = 7
            bs_switch_vendor = 9
            bs_switch_model = 12
            bs_switch_type = 12
            if 'BS Switch Vendor' in row:
                bs_switch_tech = 2
                try:
                    bs_switch_vendor = DeviceVendor.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_model = DeviceModel.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_type = DeviceType.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass

            aggregation_switch_tech = 7
            aggregation_switch_vendor = 9
            aggregation_switch_model = 12
            aggregation_switch_type = 12
            if 'Aggregation Switch Vendor' in row:
                aggregation_switch_tech = 2
                try:
                    aggregation_switch_vendor = DeviceVendor.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_model = DeviceModel.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_type = DeviceType.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass

            # increment counter by 1
            counter += 1

            logger.info("********************* PTP - Row: {}".format(counter))

            # errors in this row
            errors = ""

            # initialize variables
            base_station = ""
            sub_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            substation_antenna = ""
            backhaul = ""
            basestation = ""
            sector = ""
            customer = ""
            circuit = ""

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START PTP ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'ptp')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END PTP ERROR LOGGER *********************************

            # if bs ip and ss ip are same in inventory then skip it's insertion in database
            if all(k in row for k in ("IP", "SS IP")):
                if row['IP'] and row['SS IP']:
                    if ip_sanitizer(row['IP']) == ip_sanitizer(row['SS IP']):
                        continue

            try:
                # ----------------------------- Base Station Device ---------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # get device ip network i.e 'public' or 'private'
                device_ip_network = get_ip_network(row['IP'] if 'IP' in row.keys() else "")

                # get machine
                machine = ""

                # get site
                site = ""

                if device_ip_network == "public":
                    machine_name = "pub"

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(pub_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in pub_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)
                elif device_ip_network == "private":
                    machine_name = "vrfprv"

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(vrfprv_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in vrfprv_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)
                else:
                    machine_name = ""

                # device name
                name = device_latest_id

                # device alias
                alias = '{}_NE'.format(circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                if ip_sanitizer(row['IP']):

                    # base station data
                    base_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 2,
                        'device_vendor': 2,
                        'device_model': 2,
                        'device_type': 3,
                        'ip': row['IP'] if 'IP' in row.keys() else "",
                        'mac': row['MAC'] if 'MAC' in row.keys() else "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'Base Station created on {}.'.format(full_time)
                    }
                    # base station object
                    base_station = create_device(base_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    base_station = ""
            except Exception as e:
                base_station = ""

            try:
                # ----------------------------- Sub Station Device ---------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # get device ip network i.e 'public' or 'private'
                device_ip_network = get_ip_network(row['SS IP'] if 'SS IP' in row.keys() else "")

                # get machine
                machine = ""

                # get site
                site = ""

                if device_ip_network == "public":
                    machine_name = "pub"

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(pub_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in pub_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)
                elif device_ip_network == "private":
                    machine_name = "vrfprv"

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(vrfprv_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in vrfprv_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)
                else:
                    machine_name = ""

                # device name
                name = device_latest_id

                # device alias
                alias = '{}'.format(circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                if ip_sanitizer(row['SS IP']):
                    # sub station data
                    sub_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 2,
                        'device_vendor': 2,
                        'device_model': 2,
                        'device_type': 2,
                        'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                        'mac': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                        'state': row['SS State'] if 'SS State' in row.keys() else "",
                        'city': row['SS City'] if 'SS City' in row.keys() else "",
                        'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                        'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                        'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                        'description': 'Sub Station created on {}.'.format(full_time)
                    }
                    # sub station object
                    sub_station = create_device(sub_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------ Create BS Switch -----------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf1_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf1_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Switch IP']):

                    # bs switch data
                    bs_switch_data = {
                        # 'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bs_switch_tech,
                        'device_vendor': bs_switch_vendor,
                        'device_model': bs_switch_model,
                        'device_type': bs_switch_type,
                        'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Switch created on {}.'.format(full_time)
                    }
                    # bs switch object
                    bs_switch = create_device(bs_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['Aggregation Switch']):
                    # aggregation switch data
                    aggregation_switch_data = {
                        # 'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': aggregation_switch_tech,
                        'device_vendor': aggregation_switch_vendor,
                        'device_model': aggregation_switch_model,
                        'device_type': aggregation_switch_type,
                        'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'Aggregation Switch created on {}.'.format(full_time)
                    }
                    # aggregation switch object
                    aggregation_switch = create_device(aggregation_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf3_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf3_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Converter IP']):

                    # bs converter data
                    bs_converter_data = {
                        # 'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Converter created on {}.'.format(full_time)
                    }
                    # bs converter object
                    bs_converter = create_device(bs_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['POP Converter IP']):

                    # pop converter data
                    pop_converter_data = {
                        # 'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'POP Converter created on {}.'.format(full_time)
                    }
                    # pop converter object
                    pop_converter = create_device(pop_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}_ne'.format(special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                # antenna alias
                alias = '{}_NE'.format(circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                # sector antenna data
                sector_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['IP'] if 'IP' in row.keys() else "",
                    'antenna_type': row['Antenna Type'] if 'Antenna Type' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'gain': row['Antenna Gain'] if 'Antenna Gain' in row.keys() else "",
                    'mount_type': row['Antenna Mount Type'] if 'Antenna Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sector antenna object
                sector_antenna = create_antenna(sector_antenna_data)

                # ------------------------------- Sub Station Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}'.format(special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                # antenna alias
                alias = '{}'.format(circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "")

                # sub station antenna data
                substation_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                    'antenna_type': row['SS Antenna Type'] if 'SS Antenna Type' in row.keys() else "",
                    'height': row['SS Antenna Height'] if 'SS Antenna Height' in row.keys() else "",
                    'polarization': row['SS Polarization'] if 'SS Polarization' in row.keys() else "",
                    'gain': row['SS Antenna Gain'] if 'SS Antenna Gain' in row.keys() else "",
                    'mount_type': row['SS Antenna Mount Type'] if 'SS Antenna Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sub station antenna object
                substation_antenna = create_antenna(substation_antenna_data)
            except Exception as e:
                substation_antenna = ""

            try:
                # ------------------------------- Backhaul -------------------------------
                # bh configured on
                bh_configured_on = ""
                try:
                    bh_configured_on = Device.objects.get(ip_address=row['BH Configured On Switch/Converter'])
                except Exception as e:
                    logger.info(e.message)

                if 'BH Configured On Switch/Converter' in row.keys():
                    if ip_sanitizer(row['BH Configured On Switch/Converter']):
                        # backhaul data
                        backhaul_data = {
                            'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                            'bh_configured_on': bh_configured_on,
                            'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                            'bh_port': 0,
                            'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                            'bh_switch': bs_converter,
                            'pop': pop_converter,
                            'aggregator': aggregation_switch,
                            'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                            'aggregator_port': 0,
                            'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                            'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                            'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                            'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                            'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                            'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                            'description': 'Backhaul created on {}.'.format(full_time)
                        }

                        # backhaul object
                        backhaul = ""
                        if row['BH Configured On Switch/Converter']:
                            if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                                backhaul = create_backhaul(backhaul_data)
                    else:
                        backhaul = ""
                else:
                    backhaul = ""
            except Exception as e:
                backhaul = ""

            try:
                # ------------------------------- Base Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                # bs alias
                alias = row['BS Name'] if 'BS Name' in row.keys() else ""

                # base station data
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'organization': organization,
                    'bs_switch': bs_switch,
                    'backhaul': backhaul,
                    'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
                    'hssu_port': row['HSSU Port'] if 'HSSU Port' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }

                # base station object
                basestation = ""
                if name and alias:
                    basestation = create_basestation(basestation_data)
            except Exception as e:
                basestation = ""

            try:
                # ---------------------------------- Sector ---------------------------------
                # initialize name
                name = ""

                # sector name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                if 'SS Circuit ID' in row.keys():
                    # sector data
                    sector_data = {
                        'name': name,
                        'alias': circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "",
                        'base_station': basestation,
                        'bs_technology': 2,
                        'sector_configured_on': base_station,
                        'antenna': sector_antenna,
                        'description': 'Sector created on {}.'.format(full_time)
                    }
                    # sector object
                    sector = create_sector(sector_data)
                else:
                    sector = ""
            except Exception as e:
                sector = ""

            try:
                # ------------------------------- Sub Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                alias = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""

                # sub station data
                substation_data = {
                    'name': name,
                    'alias': alias,
                    'device': sub_station,
                    'antenna': substation_antenna,
                    'building_height': row['SS Building Height'] if 'SS Building Height' in row.keys() else "",
                    'tower_height': row['SS Tower/Pole Height'] if 'SS Tower/Pole Height' in row.keys() else "",
                    'ethernet_extender': row['SS Ethernet Extender'] if 'SS Ethernet Extender' in row.keys() else "",
                    'cable_length': row['SS Cable Length'] if 'SS Cable Length' in row.keys() else "",
                    'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                    'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                    'mac_address': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                    'state': row['SS State'] if 'SS State' in row.keys() else "",
                    'city': row['SS City'] if 'SS City' in row.keys() else "",
                    'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                    'description': 'Sub Station created on {}.'.format(full_time)
                }
                # sub station object
                substation = ""
                if name and alias:
                    substation = create_substation(substation_data)
            except Exception as e:
                substation = ""

            try:
                # ------------------------------- Customer -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize customer name
                name = "{}_{}".format(special_chars_name_sanitizer_with_lower_case(row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""),
                                      special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""))
                alias = row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""

                try:
                    if 'SS Circuit ID' in row.keys():
                        # concatinate city and state in bs name
                        name = "{}_{}".format(name, special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID']))
                except Exception as e:
                    logger.info(e.message)

                # customer data
                customer_data = {
                    'name': name,
                    'alias': alias,
                    'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                    'description': 'SS Customer created on {}.'.format(full_time)
                }
                # customer object
                customer = ""
                if name:
                    customer = create_customer(customer_data)
            except Exception as e:
                customer = ""

            try:
                # ------------------------------- Circuit -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize circuit name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'SS Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['SS Date Of Acceptance'])
                else:
                    date_of_acceptance = ""
                # circuit data
                alias = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "",
                    'circuit_type': 'Customer',
                    'sector': sector,
                    'customer': customer,
                    'sub_station': substation,
                    'qos_bandwidth': row['SS QOS (BW)'] if 'SS QOS (BW)' in row.keys() else "",
                    'dl_rssi_during_acceptance': row['SS RSSI During Acceptance'] if 'SS RSSI During Acceptance' in row.keys() else "",
                    'throughput_during_acceptance': row['SS Throughput During Acceptance'] if 'SS Throughput During Acceptance' in row.keys() else "",
                    'date_of_acceptance': date_of_acceptance,
                    'description': 'Circuit created on {}.'.format(full_time)
                }
                # circuit object
                circuit = ""
                if name and alias:
                    circuit = create_circuit(circuit_data)
            except Exception as e:
                circuit = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'PTP',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()
        logger.info(e.message)


@task()
def bulk_upload_ptp_bh_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading PTP BH (PTP Backhaul) inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """

    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] in ["Date Of Acceptance", "SS Date Of Acceptance"]:
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get 'ospf5' machine and associated sites in a dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    ospf2_machine_and_site_info = get_machine_details('ospf', [2])
    
    ospf1_machine_and_site_info = get_machine_details('ospf', [1])
    ospf4_ospf3_machine_and_site_info = get_machine_details('ospf', [4, 3])
    ospf4_ospf5_machine_and_site_info = get_machine_details('ospf', [4, 5])
    ospf5_machine_and_site_info = get_machine_details('ospf', [5])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* PTP BH - Row: {}".format(counter))

            bs_switch_tech = 7
            bs_switch_vendor = 9
            bs_switch_model = 12
            bs_switch_type = 12
            if 'BS Switch Vendor' in row:
                bs_switch_tech = 2
                try:
                    bs_switch_vendor = DeviceVendor.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_model = DeviceModel.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_type = DeviceType.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass

            aggregation_switch_tech = 7
            aggregation_switch_vendor = 9
            aggregation_switch_model = 12
            aggregation_switch_type = 12
            if 'Aggregation Switch Vendor' in row:
                aggregation_switch_tech = 2
                try:
                    aggregation_switch_vendor = DeviceVendor.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_model = DeviceModel.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_type = DeviceType.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass

            # errors in this row
            errors = ""

            # initialize variables
            base_station = ""
            sub_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            substation_antenna = ""
            backhaul = ""
            basestation = ""
            sector = ""
            customer = ""
            circuit = ""

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START PTP BH ERROR LOGGER *********************************
            errors = bulk_upload_error_logger(row, 'ptp_bh')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END PTP BH ERROR LOGGER *********************************

            # if bs ip and ss ip are same in inventory then skip it's insertion in database
            if all(k in row for k in ("IP", "SS IP")):
                if row['IP'] and row['SS IP']:
                    if ip_sanitizer(row['IP']) == ip_sanitizer(row['SS IP']):
                        continue

            try:
                # ----------------------------- Base Station Device ---------------------------
                # initialize name
                name = ""

                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf2_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf2_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                # device name
                name = device_latest_id
                # name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                if 'IP' in row.keys():
                    if ip_sanitizer(row['IP']):

                        # Fetch parent ip, port & type from sheet row
                        ne_parent_ip = ip_sanitizer(row.get('NE Parent IP', ''))
                        ne_parent_type = row.get('NE Parent Type', '')
                        ne_parent_port = row.get('NE Parent Port', '')

                        # base station data
                        base_station_data = {
                            'device_name': name,
                            'device_alias': circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "",
                            'organization': organization,
                            'machine': machine,
                            'site': site,
                            'device_technology': 2,
                            'device_vendor': 2,
                            'device_model': 2,
                            'device_type': 3,
                            'ip': row['IP'] if 'IP' in row.keys() else "",
                            'mac': row['MAC'] if 'MAC' in row.keys() else "",
                            'state': row['State'] if 'State' in row.keys() else "",
                            'city': row['City'] if 'City' in row.keys() else "",
                            'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                            'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                            'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                            'description': 'Base Station created on {}.'.format(full_time),
                            'parent_ip': ne_parent_ip,
                            'parent_type': ne_parent_type,
                            'parent_port': ne_parent_port

                        }
                        # base station object
                        base_station = create_device(base_station_data)

                        # increment device latest id by 1
                        device_latest_id += 1
                    else:
                        base_station = ""
                else:
                    base_station = ""
            except Exception as e:
                base_station = ""

            try:
                # ----------------------------- Sub Station Device ---------------------------
                # initialize name
                name = ""

                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf2_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf2_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                # device name
                name = device_latest_id

                if ip_sanitizer(row['SS IP']):
                    # sub station data
                    sub_station_data = {
                        'device_name': name,
                        'device_alias': circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "",
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 2,
                        'device_vendor': 2,
                        'device_model': 2,
                        'device_type': 2,
                        'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                        'mac': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                        'state': row['SS State'] if 'SS State' in row.keys() else "",
                        'city': row['SS City'] if 'SS City' in row.keys() else "",
                        'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                        'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                        'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                        'description': 'Sub Station created on {}.'.format(full_time)
                    }
                    # sub station object
                    sub_station = create_device(sub_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------ Create BS Switch -----------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf1_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf1_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Switch IP']):
                    # bs switch data
                    bs_switch_data = {
                        # 'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bs_switch_tech,
                        'device_vendor': bs_switch_vendor,
                        'device_model': bs_switch_model,
                        'device_type': bs_switch_type,
                        'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Switch created on {}.'.format(full_time)
                    }
                    # bs switch object
                    bs_switch = create_device(bs_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['Aggregation Switch']):
                    # aggregation switch data
                    aggregation_switch_data = {
                        # 'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': aggregation_switch_tech,
                        'device_vendor': aggregation_switch_vendor,
                        'device_model': aggregation_switch_model,
                        'device_type': aggregation_switch_type,
                        'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'Aggregation Switch created on {}.'.format(full_time)
                    }
                    # aggregation switch object
                    aggregation_switch = create_device(aggregation_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf3_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf3_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Converter IP']):
                    # bs converter data
                    bs_converter_data = {
                        # 'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Converter created on {}.'.format(full_time)
                    }
                    # bs converter object
                    bs_converter = create_device(bs_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['POP Converter IP']):
                    # pop converter data
                    pop_converter_data = {
                        # 'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'POP Converter created on {}.'.format(full_time)
                    }
                    # pop converter object
                    pop_converter = create_device(pop_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                # antenna alias
                alias = circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else ""

                # sector antenna data
                sector_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['IP'] if 'IP' in row.keys() else "",
                    'antenna_type': row['Antenna Type'] if 'Antenna Type' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'gain': row['Antenna Gain'] if 'Antenna Gain' in row.keys() else "",
                    'mount_type': row['Antenna Mount Type'] if 'Antenna Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sector antenna object
                sector_antenna = create_antenna(sector_antenna_data)

                # ------------------------------- Sub Station Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                # antenna alias
                alias = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""

                # sub station antenna data
                substation_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                    'antenna_type': row['SS Antenna Type'] if 'SS Antenna Type' in row.keys() else "",
                    'height': row['SS Antenna Height'] if 'SS Antenna Height' in row.keys() else "",
                    'polarization': row['SS Polarization'] if 'SS Polarization' in row.keys() else "",
                    'gain': row['SS Antenna Gain'] if 'SS Antenna Gain' in row.keys() else "",
                    'mount_type': row['SS Antenna Mount Type'] if 'SS Antenna Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sub station antenna object
                substation_antenna = create_antenna(substation_antenna_data)
            except Exception as e:
                substation_antenna = ""

            try:
                # ------------------------------- Backhaul -------------------------------
                # bh configured on
                bh_configured_on = ""
                try:
                    bh_configured_on = Device.objects.get(ip_address=row['BH Configured On Switch/Converter'])
                except Exception as e:
                    logger.info(e.message)

                if 'BH Configured On Switch/Converter' in row.keys():
                    if ip_sanitizer(row['BH Configured On Switch/Converter']):
                        # backhaul data
                        backhaul_data = {
                            'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                            'bh_configured_on': bh_configured_on,
                            'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                            'bh_port': 0,
                            'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                            'bh_switch': bs_converter,
                            'pop': pop_converter,
                            'aggregator': aggregation_switch,
                            'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                            'aggregator_port': 0,
                            'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                            'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                            'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                            'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                            'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                            'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                            'description': 'Backhaul created on {}.'.format(full_time)
                        }

                        # backhaul object
                        backhaul = ""
                        if row['BH Configured On Switch/Converter']:
                            if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                                backhaul = create_backhaul(backhaul_data)
                    else:
                        backhaul = ""
                else:
                    backhaul = ""
            except Exception as e:
                backhaul = ""

            try:
                # ------------------------------- Base Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # base station data
                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                alias = row['BS Name'] if 'BS Name' in row.keys() else ""
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'organization': organization,
                    'bs_switch': bs_switch,
                    'backhaul': backhaul,
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                    'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
                    'hssu_port': row['HSSU Port'] if 'HSSU Port' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }
                # base station object
                basestation = ""
                if name and alias:
                    basestation = create_basestation(basestation_data)
            except Exception as e:
                basestation = ""

            try:
                # ---------------------------------- Sector ---------------------------------
                # initialize name
                name = ""

                # sector name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                if 'IP' in row.keys():
                    if ip_sanitizer(row['IP']):
                        # sector data
                        sector_data = {
                            'name': name,
                            'alias': circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else "",
                            'base_station': basestation,
                            'bs_technology': 2,
                            'sector_configured_on': base_station,
                            'antenna': sector_antenna,
                            'description': 'Sector created on {}.'.format(full_time)
                        }
                        # sector object
                        sector = create_sector(sector_data)
                    else:
                        sector = ""
                else:
                    sector = ""
            except Exception as e:
                sector = ""

            try:
                # ------------------------------- Sub Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                alias = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""

                # sub station data
                substation_data = {
                    'name': name,
                    'alias': alias,
                    'device': sub_station,
                    'antenna': substation_antenna,
                    'building_height': row['SS Building Height'] if 'SS Building Height' in row.keys() else "",
                    'tower_height': row['SS Tower/Pole Height'] if 'SS Tower/Pole Height' in row.keys() else "",
                    'ethernet_extender': row['SS Ethernet Extender'] if 'SS Ethernet Extender' in row.keys() else "",
                    'cable_length': row['SS Cable Length'] if 'SS Cable Length' in row.keys() else "",
                    'longitude': row['SS Longitude'] if 'SS Longitude' in row.keys() else "",
                    'latitude': row['SS Latitude'] if 'SS Latitude' in row.keys() else "",
                    'mac_address': row['SS MAC'] if 'SS MAC' in row.keys() else "",
                    'state': row['SS State'] if 'SS State' in row.keys() else "",
                    'city': row['SS City'] if 'SS City' in row.keys() else "",
                    'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                    'description': 'Sub Station created on {}.'.format(full_time)
                }
                # sub station object
                substation = ""
                if name and alias:
                    substation = create_substation(substation_data)
            except Exception as e:
                logger.info(e.message)
                substation = ""

            try:
                # ------------------------------- Customer -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # customer data
                # sanitize customer name
                name = "{}_{}".format(special_chars_name_sanitizer_with_lower_case(row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""),
                                      special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""))
                alias = row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""

                try:
                    if 'SS Circuit ID' in row.keys():
                        # concatinate city and state in bs name
                        name = "{}_{}".format(name, special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID']))
                except Exception as e:
                    logger.info(e.message)

                customer_data = {
                    'name': name,
                    'alias': alias,
                    'address': row['SS Customer Address'] if 'SS Customer Address' in row.keys() else "",
                    'description': 'SS Customer created on {}.'.format(full_time)
                }
                # customer object
                customer = ""
                if name:
                    customer = create_customer(customer_data)
            except Exception as e:
                customer = ""

            try:
                # ------------------------------- Circuit -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize circuit name
                name = special_chars_name_sanitizer_with_lower_case(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'SS Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['SS Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # concatinating bs circuit id and ss circuit id
                if all(k in row for k in ("Circuit ID", "SS Circuit ID")):
                    circuit_id = "{}#{}".format(circuit_id_sanitizer(row['SS Circuit ID']), circuit_id_sanitizer(row['Circuit ID']))
                else:
                    circuit_id = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""

                # circuit alias
                alias = circuit_id_sanitizer(row['SS Circuit ID']) if 'SS Circuit ID' in row.keys() else ""

                # circuit alias
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': circuit_id,
                    'circuit_type': 'Backhaul',
                    'sector': sector,
                    'customer': customer,
                    'sub_station': substation,
                    'qos_bandwidth': row['SS QOS (BW)'] if 'SS QOS (BW)' in row.keys() else "",
                    'dl_rssi_during_acceptance': row['SS RSSI During Acceptance'] if 'SS RSSI During Acceptance' in row.keys() else "",
                    'throughput_during_acceptance': row['SS Throughput During Acceptance'] if 'SS Throughput During Acceptance' in row.keys() else "",
                    'date_of_acceptance': date_of_acceptance,
                    'description': 'Circuit created on {}.'.format(full_time)
                }
                # circuit object
                circuit = ""
                if name and alias:
                    circuit = create_circuit(circuit_data)
            except Exception as e:
                circuit = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'PTP BH',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_pmp_bs_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading PMP BS inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """
    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if isinstance(sheet.cell(row_index, col_index).value, str):
                d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
            elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
            else:
                d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get machine and associated sites details in dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    machine_and_site_info = get_machine_details('ospf', [2])

    # get 'ospf5' machine and associated sites in a dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    ospf2_machine_and_site_info = get_machine_details('ospf', [2])

    ospf1_machine_and_site_info = get_machine_details('ospf', [1])
    ospf4_ospf3_machine_and_site_info = get_machine_details('ospf', [4, 3])
    ospf4_ospf5_machine_and_site_info = get_machine_details('ospf', [4, 5])
    ospf5_machine_and_site_info = get_machine_details('ospf', [5])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* PMP BS - Row: {}".format(counter))

            bs_switch_tech = 7
            bs_switch_vendor = 9
            bs_switch_model = 12
            bs_switch_type = 12
            if 'BS Switch Vendor' in row:
                bs_switch_tech = 4
                try:
                    bs_switch_vendor = DeviceVendor.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_model = DeviceModel.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_type = DeviceType.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass

            aggregation_switch_tech = 7
            aggregation_switch_vendor = 9
            aggregation_switch_model = 12
            aggregation_switch_type = 12
            if 'Aggregation Switch Vendor' in row:
                aggregation_switch_tech = 4
                try:
                    aggregation_switch_vendor = DeviceVendor.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_model = DeviceModel.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_type = DeviceType.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass

            # errors in this row
            errors = ""

            # initialize variables
            base_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            backhaul = ""
            basestation = ""
            sector = ""

            # BS device vendor.
            bs_device_vendor = 4

            # BS device model.
            bs_device_model = 4

            # BS device type
            bs_device_type = 6

            if 'Vendor' in row.keys():
                if row['Vendor'] == 'Radwin5K':
                    bs_device_vendor = 11
                    bs_device_model = 14
                    bs_device_type = 16

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START PMP BS ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'pmp_bs')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END PMP BS ERROR LOGGER *********************************

            # ********************************* START PTP ERROR LOGGER *********************************
            errors = bulk_upload_error_logger(row, 'ptp')

            try:
                # ----------------------------- Base Station Device ---------------------------
                if ip_sanitizer(row['ODU IP']):

                    # Fetch parent ip, port & type from sheet row
                    parent_ip = ip_sanitizer(row.get('Parent IP', ''))
                    parent_type = row.get('Parent Type', '')
                    parent_port = row.get('Parent Port', '')

                    # initialize name
                    name = ""

                    # initialize alias
                    alias = ""

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # device name
                    name = device_latest_id

                    # device alias
                    alias = circuit_id_sanitizer(row['Sector ID']) if 'Sector ID' in row.keys() else ""

                    # base station data
                    base_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 4,
                        'device_vendor': bs_device_vendor,
                        'device_model': bs_device_model,
                        'device_type': bs_device_type,
                        'ip': row['ODU IP'] if 'ODU IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'Base Station created on {}.'.format(full_time),
                        'parent_ip': parent_ip,
                        'parent_type': parent_type,
                        'parent_port': parent_port
                    }
                    # base station object
                    base_station = create_device(base_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    base_station = ""
            except Exception as e:
                base_station = ""

            try:
                # ------------------------------ BS Switch -----------------------------
                if ip_sanitizer(row['BS Switch IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf1_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf1_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # base station data
                    bs_switch_data = {
                        # 'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bs_switch_tech,
                        'device_vendor': bs_switch_vendor,
                        'device_model': bs_switch_model,
                        'device_type': bs_switch_type,
                        'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'BS Switch created on {}.'.format(full_time)
                    }
                    # base station object
                    bs_switch = create_device(bs_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                if ip_sanitizer(row['Aggregation Switch']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf5_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf5_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # aggregation switch data
                    aggregation_switch_data = {
                        # 'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': aggregation_switch_tech,
                        'device_vendor': aggregation_switch_vendor,
                        'device_model': aggregation_switch_model,
                        'device_type': aggregation_switch_type,
                        'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'Aggregation Switch created on {}.'.format(full_time)
                    }
                    #  aggregation switch object
                    aggregation_switch = create_device(aggregation_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                if ip_sanitizer(row['BS Converter IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf4_ospf3_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf4_ospf3_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # bs converter data
                    bs_converter_data = {
                        # 'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'BS Converter created on {}.'.format(full_time)
                    }
                    # bs converter object
                    bs_converter = create_device(bs_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                if ip_sanitizer(row['POP Converter IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf4_ospf5_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf4_ospf5_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # pop converter data
                    pop_converter_data = {
                        # 'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'POP Converter created on {}.'.format(full_time)
                    }
                    # pop converter object
                    pop_converter = create_device(pop_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}'.format(special_chars_name_sanitizer_with_lower_case(row['Sector ID']) if 'Sector ID' in row.keys() else "")

                # antenna alias
                alias = '{}'.format(circuit_id_sanitizer(row['Sector ID']) if 'Sector ID' in row.keys() else "")

                # sector antenna data
                sector_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['ODU IP'] if 'ODU IP' in row.keys() else "",
                    'tilt': row['Antenna Tilt'] if 'Antenna Tilt' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'beam_width': row['Antenna Beamwidth'] if 'Antenna Beamwidth' in row.keys() else "",
                    'azimuth_angle': row['Azimuth'] if 'Azimuth' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'sync_splitter_used': row['Sync Splitter Used'] if 'Sync Splitter Used' in row.keys() else "",
                    'make_of_antenna': row['Make Of Antenna'] if 'Make Of Antenna' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }

                # sector antenna object
                sector_antenna = create_antenna(sector_antenna_data)

                # ------------------------------- Backhaul -------------------------------
                # backhaul data
                bh_configured_on = ""
                try:
                    bh_configured_on = Device.objects.get(ip_address=row['BH Configured On Switch/Converter'])
                except Exception as e:
                    logger.info(e.message)

                backhaul_data = {
                    'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                    'bh_configured_on': bh_configured_on,
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                    'bh_switch': bs_converter,
                    'pop': pop_converter,
                    'aggregator': aggregation_switch,
                    'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                    'aggregator_port': 0,
                    'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                    'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                    'dr_site': row['DR Site'] if 'DR Site' in row.keys() else "",
                    'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                    'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                    'ior_id': row['IOR ID'] if 'IOR ID' in row.keys() else "",
                    'bh_provider': row['BH Provider'] if 'BH Provider' in row.keys() else "",
                    'description': 'Backhaul created on {}.'.format(full_time)
                }

                # backhaul object
                backhaul = ""
                if row['BH Configured On Switch/Converter']:
                    if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                        backhaul = create_backhaul(backhaul_data)
            except Exception as e:
                backhaul = ""

            try:
                # ------------------------------- Base Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                # bs name
                alias = row['BS Name'] if 'BS Name' in row.keys() else ""

                # base station data
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'organization': organization,
                    'bs_switch': bs_switch,
                    'bs_site_id': row['Site ID'] if 'Site ID' in row.keys() else "",
                    'bs_site_type': row['Site Type'] if 'Site Type' in row.keys() else "",
                    'bs_type': row['Type Of BS (Technology)'] if 'Type Of BS (Technology)' in row.keys() else "",
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'infra_provider': row['Infra Provider'] if 'Infra Provider' in row.keys() else "",
                    'gps_type': row['Type Of GPS'] if 'Type Of GPS' in row.keys() else "",
                    'backhaul': backhaul,
                    'bh_bso': "",
                    'hssu_used': "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower Height'] if 'Tower Height' in row.keys() else "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'address': row['Address'] if 'Address' in row.keys() else "",
                    'site_ams': row['Site AMS'] if 'Site AMS' in row.keys() else "",
                    'site_infra_type': row['Site Infra Type'] if 'Site Infra Type' in row.keys() else "",
                    'site_sap_id': row['Site SAP ID'] if 'Site SAP ID' in row.keys() else "",
                    'mgmt_vlan': row['MGMT VLAN'] if 'MGMT VLAN' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }

                # base station object
                basestation = ""
                if name and alias:
                    basestation = create_basestation(basestation_data)
            except Exception as e:
                basestation = ""

            try:
                # ---------------------------------- Sector ---------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sector name
                name = '{}_{}'.format(special_chars_name_sanitizer_with_lower_case(row['Sector ID']) if 'Sector ID' in row.keys() else "",
                                      row['Sector Name'] if 'Sector Name' in row.keys() else "")

                # sector alias
                alias = row['Sector Name'].upper() if 'Sector Name' in row.keys() else ""

                # rfs date
                if 'RFS Date' in row.keys():
                    rfs_date = validate_date(row['RFS Date'])
                else:
                    rfs_date = ""

                # sector data
                sector_data = {
                    'name': name,
                    'alias': alias,
                    'base_station': basestation,
                    'sector_id': row['Sector ID'].strip().lower() if 'Sector ID' in row.keys() else "",
                    'bs_technology': 4,
                    'sector_configured_on': base_station,
                    'antenna': sector_antenna,
                    'planned_frequency': row['Planned Frequency'] if 'Planned Frequency' in row.keys() else "",
                    'dr_site': row['DR Site'] if 'DR Site' in row.keys() else "",
                    'rfs_date': rfs_date,
                    'description': 'Sector created on {}.'.format(full_time)
                }

                # sector object
                sector = create_sector(sector_data)
            except Exception as e:
                sector = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'PMP BS',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_pmp_sm_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading PMP SM inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """
    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] == "Date Of Acceptance":
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get machine and associated sites details in dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    machine_and_site_info = get_machine_details('ospf', [2])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* PMP SM - Row: {}".format(counter))

            # errors in this row
            errors = ""

            # initialize variables
            sub_station = ""
            substation_antenna = ""
            sector = ""
            customer = ""
            circuit = ""

            # SS device vendor.
            ss_device_vendor = 4

            # SS device model.
            ss_device_model = 5

            # SS device type
            ss_device_type = 9

            if 'Vendor' in row.keys():
                if row['Vendor'] == 'Radwin5K':
                    ss_device_vendor = 11
                    ss_device_model = 14
                    ss_device_type = 17

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START PMP SM ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'pmp_sm')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END PMP SM ERROR LOGGER *********************************

            try:
                # ----------------------------- Sub Station Device ---------------------------
                if ip_sanitizer(row['SS IP']):
                    # initialize name
                    name = ""

                    # initialize alias
                    alias = ""

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # device name
                    name = device_latest_id
                    # name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID']) if 'Circuit ID' in row.keys() else ""

                    # device alias
                    alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                    # sub station data
                    sub_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 4,
                        'device_vendor': ss_device_vendor,
                        'device_model': ss_device_model,
                        'device_type': ss_device_type,
                        'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                        'mac': row['MAC'] if 'MAC' in row.keys() else "",
                        'state': "",
                        'city': "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                        'description': 'Sub Station created on {}.'.format(full_time)
                    }
                    # sub station object
                    sub_station = create_device(sub_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------- Sub Station Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}'.format(special_chars_name_sanitizer_with_lower_case(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                # antenna alias
                alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                # sub station antenna data
                substation_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                    'antenna_type': row['Antenna Type'] if 'Antenna Type' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'beam_width': row['Antenna Beamwidth'] if 'Antenna Beamwidth' in row.keys() else "",
                    'reflector': row['Lens/Reflector'] if 'Lens/Reflector' in row.keys() else "",
                    'mount_type': row['SS Mount Type'] if 'SS Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sub station antenna object
                substation_antenna = create_antenna(substation_antenna_data)
            except Exception as e:
                substation_antenna = ""

            try:
                # ------------------------------- Sub Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sub station data
                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")
                substation_data = {
                    'name': name,
                    'alias': alias,
                    'device': sub_station,
                    'antenna': substation_antenna,
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                    'ethernet_extender': row['Ethernet Extender'] if 'Ethernet Extender' in row.keys() else "",
                    'cable_length': row['Cable Length'] if 'Cable Length' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'mac_address': row['MAC'] if 'MAC' in row.keys() else "",
                    'cpe_vlan': row['CPE VLAN'] if 'CPE VLAN' in row.keys() else "",
                    'sacfa_no': row['SACFA No'] if 'SACFA No' in row.keys() else "",
                    'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                    'description': 'Sub Station created on {}.'.format(full_time)
                }

                # sub station object
                substation = ""
                if name and alias:
                    substation = create_substation(substation_data)
            except Exception as e:
                substation = ""

            try:
                # ------------------------------- Customer -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # customer data
                # sanitize customer name
                name = "{}_{}".format(special_chars_name_sanitizer_with_lower_case(row['Customer Name'] if 'Customer Name' in row.keys() else ""),
                                      special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else ""))
                alias = row['Customer Name'] if 'Customer Name' in row.keys() else ""

                customer_data = {
                    'name': name,
                    'alias': alias,
                    'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                    'description': 'Customer created on {}.'.format(full_time)
                }

                # customer object
                customer = ""
                if name:
                    customer = create_customer(customer_data)
            except Exception as e:
                customer = ""

            # ------------------------------ GET SS SECTOR ------------------------------
            # ss sector
            sector = ""

            try:
                ss_bs_ip = ip_sanitizer(row['AP IP'] if 'AP IP' in row else "")
                sector_configured_on_device = Device.objects.get(ip_address=ss_bs_ip)
                sector = Sector.objects.get(sector_configured_on=sector_configured_on_device)
            except Exception as e:
                logger.info("Sector not found. Exception:")

            try:
                # ------------------------------- Circuit -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize circuit name
                name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # circuit data
                alias = circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else ""
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "",
                    'sector': sector,
                    'customer': customer,
                    'sub_station': substation,
                    'qos_bandwidth': row['QOS (BW)'] if 'QOS (BW)' in row.keys() else "",
                    'dl_rssi_during_acceptance': row['RSSI During Acceptance'] if 'RSSI During Acceptance' in row.keys() else "",
                    'dl_cinr_during_acceptance': row['CINR During Acceptance'] if 'CINR During Acceptance' in row.keys() else "",
                    'sold_cir': row['Customer Sold CIR In Mbps'] if 'Customer Sold CIR In Mbps' in row.keys() else "",
                    'date_of_acceptance': date_of_acceptance,
                    'description': 'Circuit created on {}.'.format(full_time)
                }

                # circuit object
                circuit = ""
                if name and alias:
                    circuit = create_circuit(circuit_data)
            except Exception as e:
                circuit = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'PMP SM',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_wimax_bs_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading WiMAX BS inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """
    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if isinstance(sheet.cell(row_index, col_index).value, str):
                d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
            elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
            else:
                d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get 'ospf5' machine and associated sites in a dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    # ospf5_machine_and_site_info = get_machine_details('ospf', [1, 4])

    ospf1_machine_and_site_info = get_machine_details('ospf', [1])
    ospf4_ospf3_machine_and_site_info = get_machine_details('ospf', [4, 3])
    ospf4_ospf5_machine_and_site_info = get_machine_details('ospf', [4, 5])
    ospf5_machine_and_site_info = get_machine_details('ospf', [5])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)
    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* Wimax BS - Row: {}".format(counter))

            bs_switch_tech = 7
            bs_switch_vendor = 9
            bs_switch_model = 12
            bs_switch_type = 12
            if 'BS Switch Vendor' in row:
                bs_switch_tech = 3
                try:
                    bs_switch_vendor = DeviceVendor.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_model = DeviceModel.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_type = DeviceType.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass

            aggregation_switch_tech = 7
            aggregation_switch_vendor = 9
            aggregation_switch_model = 12
            aggregation_switch_type = 12
            if 'Aggregation Switch Vendor' in row:
                aggregation_switch_tech = 3
                try:
                    aggregation_switch_vendor = DeviceVendor.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_model = DeviceModel.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_type = DeviceType.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass

            # errors in this row
            errors = ""

            # initialize variables
            base_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            backhaul = ""
            basestation = ""
            sector = ""

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START WIMAX BS ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'wimax_bs')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END WIMAX BS ERROR LOGGER *********************************

            try:
                # ----------------------------- Base Station Device ---------------------------
                if ip_sanitizer(row['IDU IP']):

                    # initialize name
                    name = ""

                    # initialize alias
                    alias = ""

                    # get machine and associated sites details in dictionary
                    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument

                    # Machine Name.
                    m_name = ''

                    # Machine Numbers.
                    m_numbers = []

                    if row.get('Machine Name'):
                        try:
                            m_name = str(row['Machine Name']).translate(None, digits)
                            m_numbers = map(int, re.findall('\d+', row['Machine Name']))
                        except Exception as e:
                            pass

                    machine_and_site_info = get_machine_details(m_name, m_numbers)

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # device name
                    name = device_latest_id

                    # device alias
                    alias = circuit_id_sanitizer(row['Sector ID']) if 'Sector ID' in row.keys() else ""

                    # Fetch parent ip, port & type from sheet row
                    parent_ip = ip_sanitizer(row.get('Parent IP', ''))
                    parent_type = row.get('Parent Type', '')
                    parent_port = row.get('Parent Port', '')

                    # base station data
                    base_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 3,
                        'device_vendor': 3,
                        'device_model': 3,
                        'device_type': 4,
                        'ip': row['IDU IP'] if 'IDU IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'Base Station created on {}.'.format(full_time),
                        'parent_ip': parent_ip,
                        'parent_type': parent_type,
                        'parent_port': parent_port
                    }

                    # base station object
                    base_station = create_device(base_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    base_station = ""
            except Exception as e:
                logger.exception("Base Station not created. Exception: ", e.message)
                base_station = ""

            # ******************************************************************************************
            # ****************************** DR Site Anonymous Check (Start) ***************************

            # # check for dr site (disaster recovery site); if it's yes than do not create any entry beyond this point
            # # just get base station/idu device and make it 'dr configured on' attribute of current sector
            # # get dr site status
            # dr_site_status = row['DR Site'] if 'DR Site' in row.keys() else ""
            #
            # # get current sector
            # sector_id = row['Sector ID'] if 'Sector ID' in row.keys() else ""
            #
            # # pmp name
            # pmp = ""
            # try:
            #     if 'PMP' in row.keys():
            #         pmp = row['PMP']
            #         if isinstance(pmp, basestring) or isinstance(pmp, float):
            #             pmp = int(pmp)
            # except Exception as e:
            #     logger.info("PMP not in sheet or something wrong. Exception: ", e.message)
            #
            # # sector name
            # sector_name = '{}_{}_{}'.format(
            #     special_chars_name_sanitizer_with_lower_case(row['Sector ID']) if 'Sector ID' in row.keys() else "",
            #     row['Sector Name'] if 'Sector Name' in row.keys() else "", pmp)
            #
            # # get sector with current sector id
            # dr_sector = Sector.objects.filter(name=sector_name)
            #
            # if (dr_site_status.lower() == "yes") and dr_sector:
            #     if dr_sector:
            #         # if sector already exist than make base station/idu device it's 'dr configured on' device
            #         # and than skip the current loop by using 'continue' so that no entry beyond this point created
            #         dr_sector[0].dr_configured_on = base_station
            #         dr_sector[0].save()
            #         continue

            # ****************************** DR Site Anonymous Check (End) *****************************
            # ******************************************************************************************

            try:
                # ------------------------------ BS Switch -----------------------------
                if ip_sanitizer(row['BS Switch IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf1_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:",
                                    e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf1_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # base station data
                    bs_switch_data = {
                        # 'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bs_switch_tech,
                        'device_vendor': bs_switch_vendor,
                        'device_model': bs_switch_model,
                        'device_type': bs_switch_type,
                        'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'BS Switch created on {}.'.format(full_time)
                    }
                    # base station object
                    bs_switch = create_device(bs_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                if ip_sanitizer(row['Aggregation Switch']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf5_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:",
                                    e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf5_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # aggregation switch data
                    aggregation_switch_data = {
                        # 'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': aggregation_switch_tech,
                        'device_vendor': aggregation_switch_vendor,
                        'device_model': aggregation_switch_model,
                        'device_type': aggregation_switch_type,
                        'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'Aggregation Switch created on {}.'.format(full_time)
                    }
                    #  aggregation switch object
                    aggregation_switch = create_device(aggregation_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                if ip_sanitizer(row['BS Converter IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf4_ospf3_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf4_ospf3_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # bs converter data
                    bs_converter_data = {
                        # 'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'BS Converter created on {}.'.format(full_time)
                    }
                    # bs converter object
                    bs_converter = create_device(bs_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                if ip_sanitizer(row['POP Converter IP']):
                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(ospf4_ospf5_machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in ospf4_ospf5_machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # pop converter data
                    pop_converter_data = {
                        # 'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 8,
                        'device_vendor': 8,
                        'device_model': 10,
                        'device_type': 13,
                        'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Address'] if 'Address' in row.keys() else "",
                        'description': 'POP Converter created on {}.'.format(full_time)
                    }
                    # pop converter object
                    pop_converter = create_device(pop_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}'.format(special_chars_name_sanitizer_with_lower_case(row['Sector ID']) if 'Sector ID' in row.keys() else "")

                # antenna alias
                alias = '{}'.format(circuit_id_sanitizer(row['Sector ID']) if 'Sector ID' in row.keys() else "")

                # sector antenna data
                sector_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['ODU IP'] if 'ODU IP' in row.keys() else "",
                    'tilt': row['Antenna Tilt'] if 'Antenna Tilt' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'beam_width': row['Antenna Beamwidth'] if 'Antenna Beamwidth' in row.keys() else "",
                    'azimuth_angle': row['Azimuth'] if 'Azimuth' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'splitter_installed': row['Installation Of Splitter'] if 'Installation Of Splitter' in row.keys() else "",
                    'make_of_antenna': row['Make Of Antenna'] if 'Make Of Antenna' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sector antenna object
                sector_antenna = create_antenna(sector_antenna_data)

                # ------------------------------- Backhaul -------------------------------
                # backhaul data
                bh_configured_on = ""
                try:
                    bh_configured_on = Device.objects.get(ip_address=row['BH Configured On Switch/Converter'])
                except Exception as e:
                    logger.info(e.message)

                backhaul_data = {
                    'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                    'bh_configured_on': bh_configured_on,
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                    'bh_switch': bs_converter,
                    'pop': pop_converter,
                    'aggregator': aggregation_switch,
                    'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                    'aggregator_port': 0,
                    'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                    'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                    'dr_site': row['DR Site'] if 'DR Site' in row.keys() else "",
                    'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                    'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                    'description': 'Backhaul created on {}.'.format(full_time)
                }

                # backhaul object
                backhaul = ""
                if row['BH Configured On Switch/Converter']:
                    if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                        backhaul = create_backhaul(backhaul_data)
            except Exception as e:
                backhaul = ""

            try:
                # ------------------------------- Base Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                # bs name
                alias = row['BS Name'] if 'BS Name' in row.keys() else ""

                # base station data
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'organization': organization,
                    'bs_switch': bs_switch,
                    'bs_site_id': row['Site ID'] if 'Site ID' in row.keys() else "",
                    'bs_site_type': row['Site Type'] if 'Site Type' in row.keys() else "",
                    'bs_type': row['Type Of BS (Technology)'] if 'Type Of BS (Technology)' in row.keys() else "",
                    'bh_port_name': row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else "",
                    'bh_port': 0,
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'infra_provider': row['Infra Provider'] if 'Infra Provider' in row.keys() else "",
                    'gps_type': row['Type Of GPS'] if 'Type Of GPS' in row.keys() else "",
                    'backhaul': backhaul,
                    'bh_bso': "",
                    'hssu_used': "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower Height'] if 'Tower Height' in row.keys() else "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'address': row['Address'] if 'Address' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }

                # base station object
                basestation = ""
                if name and alias:
                    basestation = create_basestation(basestation_data)
            except Exception as e:
                basestation = ""

            try:
                # ---------------------------------- Sector ---------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # pmp name
                pmp = ""
                try:
                    if 'PMP' in row.keys():
                        pmp = row['PMP']
                        if isinstance(pmp, basestring) or isinstance(pmp, float):
                            pmp = int(pmp)
                except Exception as e:
                    logger.info("PMP not in sheet or something wrong. Exception: ", e.message)

                # sector configured on port
                port = ""
                try:
                    port_name = "pmp" + str(pmp)
                    port_alias = "PMP Port " + str(pmp)
                    port_value = pmp
                    port = create_device_port(port_name, port_alias, port_value)
                except Exception as e:
                    logger.info("Sector Configured On port not present. Exception: ", e.message)

                # sector name
                name = '{}_{}_{}'.format(
                    special_chars_name_sanitizer_with_lower_case(row['Sector ID']) if 'Sector ID' in row.keys() else "",
                    row['Sector Name'] if 'Sector Name' in row.keys() else "", pmp)

                # sector alias
                alias = row['Sector Name'].upper() if 'Sector Name' in row.keys() else ""

                # mrc
                mrc = row['MRC'] if 'MRC' in row.keys() else ""

                # dr site
                dr_site = row['DR Site'] if 'DR Site' in row.keys() else ""

                # idu ip
                idu_ip = row['IDU IP'] if 'IDU IP' in row.keys() else ""

                # master device
                master_device = base_station

                # slave device
                slave_device = ""

                # *********************************************************************************************
                # ********************************* MRC Case Handling (Start) *********************************
                # *********************************************************************************************

                # if we get 'mrc' yes than only make one sector having pmp port 1
                if mrc.lower() == "yes" and pmp == 2:
                    continue

                # *********************************************************************************************
                # ********************************** MRC Case Handling (End) **********************************
                # *********************************************************************************************

                # *********************************************************************************************
                # ************************ DR handling according to ip address (Start) ************************
                # *********************************************************************************************

                # Rule for identifying master/slave device:
                # Master device ip address is just previous to ip address of slave device.
                # For e.g. if master device ip is '10.156.4.2' than slave device ip is '10.156.4.3'

                # identify whether device is master/slave if 'dr site' is 'yes' and current sector is already present
                if dr_site.lower() == "yes":
                    if idu_ip:
                        # master/slave identifier from workbook
                        ms_identifier = row['DR Master/Slave'] if 'DR Master/Slave' in row.keys() else ""
                        # current sector
                        current_sector = ""

                        # current sector 'sector_configured_on' device
                        sector_device = ""

                        try:
                            # get current sector only if it's 'dr_site' is 'Yes'
                            current_sector = Sector.objects.get(name=name, dr_site="Yes")
                        except Exception as e:
                            logger.info("Sector with sector id - {} not exist. Exception: {} ".format(alias, e.message))

                        if current_sector:
                            # sector configured on device
                            sector_device = current_sector.sector_configured_on

                            # dr configured on device
                            dr_device = current_sector.dr_configured_on
                            if sector_device or dr_device:
                                # sector device previous ip (decrement idu ip by 1)
                                sd_prev_ip = ""
                                try:
                                    sd_prev_ip = ipaddr.IPAddress(sector_device.ip_address) - 1
                                except Exception as e:
                                    logger.info("No ip address for sector device. Exception: {}".format(e.message))

                                # next ip (increment idu ip by 1)
                                sd_next_ip = ""
                                try:
                                    sd_next_ip = ipaddr.IPAddress(sector_device.ip_address) + 1
                                except Exception as e:
                                    logger.info("No ip address for sector device. Exception: {}".format(e.message))

                                # idu ip address 'ipaddr' object
                                idu_ip_address = ipaddr.IPAddress(idu_ip)

                                # identify master/slave device corresponding to master/slave bit
                                if ms_identifier:
                                    if ms_identifier == "Master":
                                        master_device = base_station
                                        slave_device = ""
                                    elif ms_identifier == "Slave":
                                        master_device = ""
                                        slave_device = base_station
                                    else:
                                        pass
                                else:
                                    # if 'idu_ip_address' is ip address just previous to 'sector_configured_on'
                                    # device
                                    # than make current 'sector_configured_on' device to 'dr_configured_on' device
                                    # and make 'base_station' device new 'sector_configured_on' device
                                    if idu_ip_address == sd_prev_ip:
                                        master_device = base_station
                                        slave_device = sector_device
                                    # if 'idu_ip_address' is ip address just next to 'sector_configured_on' device
                                    # than just 'base_station' device new 'dr_configured_on' device
                                    # and 'sector_configured_on' device remains the same
                                    elif idu_ip_address == sd_next_ip:
                                        master_device = sector_device
                                        slave_device = base_station
                                    else:
                                        pass
                        else:
                            # if current sector not exist in database and needs to be created
                            # than if master/slave bit 'ms_identifier' exist than assign sector devices according
                            # to the corresponding bit else continue with the normal flow
                            if ms_identifier:
                                if ms_identifier == "Master":
                                    master_device = base_station
                                    slave_device = ""
                                elif ms_identifier == "Slave":
                                    master_device = ""
                                    slave_device = base_station
                                else:
                                    pass

                # *********************************************************************************************
                # ************************ DR handling according to ip address (End) **************************
                # *********************************************************************************************

                # sector data
                sector_data = {
                    'name': name,
                    'alias': alias,
                    'sector_id': row['Sector ID'].strip().lower() if 'Sector ID' in row.keys() else "",
                    'base_station': basestation,
                    'bs_technology': 3,
                    'sector_configured_on': master_device,
                    'sector_configured_on_port': port,
                    'antenna': sector_antenna,
                    'planned_frequency': row['Planned Frequency'] if 'Planned Frequency' in row.keys() else "",
                    'dr_site': dr_site,
                    'mrc': row['MRC'].strip() if 'MRC' in row.keys() else "",
                    'dr_configured_on': slave_device,
                    'description': 'Sector created on {}.'.format(full_time)
                }

                # sector object
                sector = create_sector(sector_data)
            except Exception as e:
                sector = ""
                logger.info("Sector Exception: ", e.message)

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'Wimax BS',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_wimax_ss_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading WiMAX SS inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """
    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] == "Date Of Acceptance":
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* Wimax SS - Row: {}".format(counter))

            # errors in this row
            errors = ""

            # initialize variables
            sub_station = ""
            substation_antenna = ""
            sector = ""
            customer = ""
            circuit = ""

            # SS device type
            ss_device_type = 5

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START WIMAX SS ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'wimax_ss')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END WIMAX SS ERROR LOGGER *********************************

            try:
                # ----------------------------- Sub Station Device ---------------------------
                if ip_sanitizer(row['SS IP']):
                    # initialize name
                    name = ""

                    # initialize alias
                    alias = ""

                    # get machine and associated sites details in dictionary
                    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument

                    # Machine Name.
                    m_name = None

                    # Machine Numbers.
                    m_numbers = None

                    if row['Machine Name']:
                        try:
                            m_name = str(row['Machine Name']).translate(None, digits)
                            m_numbers = map(int, re.findall('\d+', row['Machine Name']))
                        except Exception as e:
                            pass

                    machine_and_site_info = get_machine_details(m_name, m_numbers)

                    # get machine and site
                    machine_and_site = ""
                    try:
                        machine_and_site = get_machine_and_site(machine_and_site_info)
                    except Exception as e:
                        logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                    if machine_and_site:
                        # get machine
                        machine = ""
                        try:
                            machine = machine_and_site['machine']
                            machine_name = machine.name
                        except Exception as e:
                            machine = ""
                            logger.info("Unable to get machine. Exception:", e.message)

                        # get site_instance
                        site = ""
                        try:
                            site = machine_and_site['site']
                            site_name = site.name
                            for site_dict in machine_and_site_info[machine_name]:
                                # 'k' is site name and 'v' is number of associated devices with that site
                                for k, v in site_dict.iteritems():
                                    if k == site_name:
                                        # increment number of devices corresponding to the site associated with
                                        # current device in 'machine_and_site_info' dictionary
                                        site_dict[k] += 1
                        except Exception as e:
                            site = ""
                            logger.info("Unable to get site. Exception:", e.message)

                    # device name
                    name = device_latest_id
                    # name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID']) if 'Circuit ID' in row.keys() else ""

                    # device alias
                    alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                    # sub station data
                    sub_station_data = {
                        'device_name': name,
                        'device_alias': alias,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 3,
                        'device_vendor': 3,
                        'device_model': 3,
                        'device_type': ss_device_type,
                        'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                        'mac': row['MAC'] if 'MAC' in row.keys() else "",
                        'state': "",
                        'city': "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                        'description': 'Sub Station created on {}.'.format(full_time)
                    }
                    # sub station object
                    sub_station = create_device(sub_station_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------- Sub Station Antenna -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # antenna name
                name = '{}'.format(special_chars_name_sanitizer_with_lower_case(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                # antenna alias
                alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")

                # sub station antenna data
                substation_antenna_data = {
                    'antenna_name': name,
                    'antenna_alias': alias,
                    'ip': row['SS IP'] if 'SS IP' in row.keys() else "",
                    'antenna_type': row['Antenna Type'] if 'Antenna Type' in row.keys() else "",
                    'height': row['Antenna Height'] if 'Antenna Height' in row.keys() else "",
                    'polarization': row['Polarization'] if 'Polarization' in row.keys() else "",
                    'beam_width': row['Antenna Beamwidth'] if 'Antenna Beamwidth' in row.keys() else "",
                    'reflector': row['Lens/Reflector'] if 'Lens/Reflector' in row.keys() else "",
                    'mount_type': row['SS Mount Type'] if 'SS Mount Type' in row.keys() else "",
                    'description': 'Sector Antenna created on {}.'.format(full_time)
                }
                # sub station antenna object
                substation_antenna = create_antenna(substation_antenna_data)
            except Exception as e:
                substation_antenna = ""

            try:
                # ------------------------------- Sub Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sub station data
                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                alias = '{}'.format(circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "")
                substation_data = {
                    'name': name,
                    'alias': alias,
                    'device': sub_station,
                    'antenna': substation_antenna,
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                    'ethernet_extender': row['Ethernet Extender'].lower() if 'Ethernet Extender' in row.keys() else "",
                    'cable_length': row['Cable Length'] if 'Cable Length' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'mac_address': row['MAC'] if 'MAC' in row.keys() else "",
                    'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                    'description': 'Sub Station created on {}.'.format(full_time)
                }
                # sub station object
                substation = ""
                if name and alias:
                    substation = create_substation(substation_data)
            except Exception as e:
                substation = ""

            try:
                # ------------------------------- Customer -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # customer data
                # sanitize customer name
                name = "{}_{}".format(special_chars_name_sanitizer_with_lower_case(row['Customer Name'] if 'Customer Name' in row.keys() else ""),
                                      special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else ""))
                alias = row['Customer Name'] if 'Customer Name' in row.keys() else ""

                customer_data = {
                    'name': name,
                    'alias': alias,
                    'address': row['Customer Address'] if 'Customer Address' in row.keys() else "",
                    'description': 'Customer created on {}.'.format(full_time)
                }

                # customer object
                customer = ""
                if name:
                    customer = create_customer(customer_data)
            except Exception as e:
                customer = ""

            # ------------------------------ GET SS SECTOR ------------------------------
            # ss sector
            sector = ""

            try:
                sector_id = row['Sector ID'].strip() if 'Sector ID' in row.keys() else ""
                sector = Sector.objects.filter(sector_id=sector_id)[0]
            except Exception as e:
                logger.info(e.message)

            try:
                # ------------------------------- Circuit -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # sanitize circuit name
                name = special_chars_name_sanitizer_with_lower_case(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # circuit data
                alias = circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else ""
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': circuit_id_sanitizer(row['Circuit ID']) if 'Circuit ID' in row.keys() else "",
                    'sector': sector,
                    'customer': customer,
                    'sub_station': substation,
                    'qos_bandwidth': row['QOS (BW)'] if 'QOS (BW)' in row.keys() else "",
                    'dl_rssi_during_acceptance': row['RSSI During Acceptance'] if 'RSSI During Acceptance' in row.keys() else "",
                    'dl_cinr_during_acceptance': row['CINR During Acceptance'] if 'CINR During Acceptance' in row.keys() else "",
                    'date_of_acceptance': date_of_acceptance,
                    'description': 'Circuit created on {}.'.format(full_time)
                }

                # circuit object
                circuit = ""
                if name and alias:
                    circuit = create_circuit(circuit_data)
            except Exception as e:
                circuit = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'Wimax SS',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()

@task()
def bulk_upload_backhaul_inventory(gis_id, organization, sheettype, auto=''):
    """ Uploading Backhaul inventory from excel sheet to database

        Parameters:
            gis_id (unicode) - GISInventoryBulkImport object id (id from table `inventory_gisinventorybulkimport`)
                               e.g. 98
            organization (<class 'organization.models.Organization'>) - organization object e.g. TCL
            sheettype (unicode) - type of sheet valid/invalid e.g. invalid

        Returns:
           - Nothing
    """
    # gis bulk upload id
    gis_id = gis_id

    # current user organization
    organization = organization

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get object for 'GISInventoryBulkImport' model
    gis_bu_obj = ""
    try:
        gis_bu_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
    except Exception as e:
        logger.info(e.message)

    # get valid or invalid sheet based upon sheettype
    if sheettype == 'valid':
        file_path = gis_bu_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif sheettype == 'invalid':
        file_path = gis_bu_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # error rows list
    error_rows = []

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] in ["Date Of Acceptance", "SS Date Of Acceptance"]:
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # get 'ospf5' machine and associated sites in a dictionary
    # pass machine name and list of machines postfix i.e [1, 5] for 'ospf1' and 'ospf5' as argument
    ospf1_machine_and_site_info = get_machine_details('ospf', [1])
    ospf4_ospf3_machine_and_site_info = get_machine_details('ospf', [4, 3])
    ospf4_ospf5_machine_and_site_info = get_machine_details('ospf', [4, 5])
    ospf5_machine_and_site_info = get_machine_details('ospf', [5])

    # id of last inserted row in 'device' model
    device_latest_id = 0

    # row counter
    counter = 0

    # get device latest inserted in schema
    try:
        id_list = [Device.objects.latest('id').id, int(Device.objects.latest('id').device_name)]
        device_latest_id = max(id_list)
    except Exception as e:
        logger.info("No device is added in database till now. Exception: ", e.message)

    try:
        # reading of values start from 2nd row
        row_number = 2

        for row in complete_d:

            # Create organization object
            try:
                organization = get_organization_from_sheet(row.get('Organization'))
            except Exception, e:
                try:
                    organization = Organization.objects.get(name__iexact='tcl')
                except Exception, e:
                    organization = ''
                    total_organization = Organization.objects.all().count()
                    if total_organization:
                        organization = Organization.objects.all()[0]

            # increment device latest id by 1
            device_latest_id += 1

            # increment counter by 1
            counter += 1

            logger.info("********************* Backhaul - Row: {}".format(counter))

            # errors in this row
            errors = ""

            # initialize variables
            base_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            backhaul = ""
            basestation = ""

            # insert row no. in row dictionary to identify error row number
            row['Row No.'] = row_number

            # ********************************* START BACKHAUL ERROR LOGGER *******************************
            errors = bulk_upload_error_logger(row, 'backhaul')

            # append errors to error rows
            if errors:
                row['Bulk Upload Errors'] = errors

            # ********************************* END BACKHAUL ERROR LOGGER *********************************

            # technology present in inventory sheet
            tech_in_inventory_sheet = row['Technology'].replace(" ", "") if 'Technology' in row.keys() else ""

            # type present in inventory sheet
            type_in_inventory_sheet = row['Converter Type'].replace(" ", "") if 'Converter Type' in row.keys() else ""

            # devices technology
            bh_device_technology = None
            try:
                bh_device_technology = DeviceTechnology.objects.get(name__iexact=tech_in_inventory_sheet)
            except Exception as e:
                logger.info("Backhaul devices technology not exist.")

            # devices type
            bh_device_type = None
            try:
                bh_device_type = DeviceType.objects.get(name__iexact=type_in_inventory_sheet)
            except Exception as e:
                logger.info("Backhaul device technology not exist.")

            bs_switch_tech = 7
            bs_switch_vendor = 9
            bs_switch_model = 12
            bs_switch_type = 12
            if 'BS Switch Vendor' in row:
                bs_switch_tech = bh_device_technology.id if bh_device_technology else None
                try:
                    bs_switch_vendor = DeviceVendor.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_model = DeviceModel.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    bs_switch_type = DeviceType.objects.get(name=row['BS Switch Vendor']).id
                except Exception as e:
                    pass

            aggregation_switch_tech = 7
            aggregation_switch_vendor = 9
            aggregation_switch_model = 12
            aggregation_switch_type = 12
            if 'Aggregation Switch Vendor' in row:
                aggregation_switch_tech = bh_device_technology.id if bh_device_technology else None
                try:
                    aggregation_switch_vendor = DeviceVendor.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_model = DeviceModel.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass
                try:
                    aggregation_switch_type = DeviceType.objects.get(name=row['Aggregation Switch Vendor']).id
                except Exception as e:
                    pass

            # dummy exception class to skip all loops when maching model is found
            class FoundModel(Exception):
                pass

            # reverse mapping: there can me multiple device models associates with the same device type
            #                  for e.g. 'RiCi' device type is associated with models 'RiCi_Converter' & 'RICI-LC';
            #                  so to get correct model we must check it corresponding to it's associated technologies,
            #                  and consider model which is associated with the technology given in excel sheet; same
            #                  condition exist with device vendor.

            # devices model
            bh_device_model = None
            try:
                bh_device_model = ModelType.objects.filter(type=bh_device_type)
                # if more than one device model is fetched than we need to loop on it to find it's corresponding
                # technology; first we need to fetch models than we need to loop on them; then we fetch
                # vendors corresponding to the model in current loop; then we fetch device technologies
                # corresponding to the current vendor in loop; at last we need to loop on these device technologies
                # and compare there name with one which is given in excel sheet; if we find a match than we consider the
                # model in current loop as 'bh_device_model' and skip all other loops by raising an exception
                if len(bh_device_model) > 1:

                    # loop on device models
                    for temp_model in bh_device_model:
                        temp_vendors = VendorModel.objects.filter(model=temp_model.model)
                        if temp_vendors:

                            # loop on device vendors
                            for temp_vendor in temp_vendors:
                                temp_technology = None
                                try:
                                    temp_technology = TechnologyVendor.objects.filter(vendor=temp_vendor.vendor)
                                except Exception as e:
                                    logger.error("Temp technology not exist.")
                                if temp_technology:

                                    # loop on device technologies
                                    for tech in temp_technology:
                                        # compare current technology with the technology in the loop
                                        if tech.technology.name.lower() == tech_in_inventory_sheet.lower():
                                            bh_device_model = temp_model.model
                                            raise FoundModel
                elif bh_device_model:
                    bh_device_model = bh_device_model[0].model
            except FoundModel:
                pass

            # device vendor
            bh_device_vendor = None
            try:
                bh_device_vendor = VendorModel.objects.filter(model=bh_device_model)[0].vendor
            except Exception as e:
                logger.info("Backhaul device vendor not exist.")

            try:
                # ------------------------------ Create BS Switch -----------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf1_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf1_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Switch IP']):

                    # Fetch parent ip, port & type from sheet row
                    bs_switch_parent_ip = ip_sanitizer(row.get('BS Switch Parent IP', ''))
                    bs_switch_parent_type = row.get('BS Switch Parent Type', '')
                    bs_switch_parent_port = row.get('BS Switch Parent Port', '')

                    # bs switch data
                    bs_switch_data = {
                        # 'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bs_switch_tech,
                        'device_vendor': bs_switch_vendor,
                        'device_model': bs_switch_model,
                        'device_type': bs_switch_type,
                        'ip': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Switch created on {}.'.format(full_time),
                        'parent_ip': bs_switch_parent_ip,
                        'parent_type': bs_switch_parent_type,
                        'parent_port': bs_switch_parent_port
                    }
                    # bs switch object
                    bs_switch = create_device(bs_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:",
                                e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['Aggregation Switch']):

                    # Fetch parent ip, port & type from sheet row
                    aggr_switch_parent_ip = ip_sanitizer(row.get('Aggregation Switch Parent IP', ''))
                    aggr_switch_parent_type = row.get('Aggregation Switch Parent Type', '')
                    aggr_switch_parent_port = row.get('Aggregation Switch Parent Port', '')

                    # aggregation switch data
                    aggregation_switch_data = {
                        # 'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': aggregation_switch_tech,
                        'device_vendor': aggregation_switch_vendor,
                        'device_model': aggregation_switch_model,
                        'device_type': aggregation_switch_type,
                        'ip': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'Aggregation Switch created on {}.'.format(full_time),
                        'parent_ip': aggr_switch_parent_ip,
                        'parent_type': aggr_switch_parent_type,
                        'parent_port': aggr_switch_parent_port
                    }
                    # aggregation switch object
                    aggregation_switch = create_device(aggregation_switch_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf3_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:",
                                e.message)
                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf3_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['BS Converter IP']):

                    # Fetch parent ip, port & type from sheet row
                    bs_converter_parent_ip = ip_sanitizer(row.get('BS Converter Parent IP', ''))
                    bs_converter_parent_type = row.get('BS Converter Parent Type', '')
                    bs_converter_parent_port = row.get('BS Converter Parent Port', '')

                    # bs converter data
                    bs_converter_data = {
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bh_device_technology.id if bh_device_technology else "",
                        'device_vendor': bh_device_vendor.id if bh_device_vendor else "",
                        'device_model': bh_device_model.id if bh_device_model else "",
                        'device_type': bh_device_type.id if bh_device_type else "",
                        'ip': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'BS Converter created on {}.'.format(full_time),
                        'parent_ip': bs_converter_parent_ip,
                        'parent_type': bs_converter_parent_type,
                        'parent_port': bs_converter_parent_port
                    }

                    # bs converter object
                    bs_converter = create_device(bs_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine and site
                machine_and_site = ""
                try:
                    machine_and_site = get_machine_and_site(ospf4_ospf5_machine_and_site_info)
                except Exception as e:
                    logger.info("No machine and site returned by function 'get_machine_and_site'. Exception:", e.message)

                if machine_and_site:
                    # get machine
                    machine = ""
                    try:
                        machine = machine_and_site['machine']
                        machine_name = machine.name
                    except Exception as e:
                        machine = ""
                        logger.info("Unable to get machine. Exception:", e.message)

                    # get site_instance
                    site = ""
                    try:
                        site = machine_and_site['site']
                        site_name = site.name
                        for site_dict in ospf4_ospf5_machine_and_site_info[machine_name]:
                            # 'k' is site name and 'v' is number of associated devices with that site
                            for k, v in site_dict.iteritems():
                                if k == site_name:
                                    # increment number of devices corresponding to the site associated with
                                    # current device in 'machine_and_site_info' dictionary
                                    site_dict[k] += 1
                    except Exception as e:
                        site = ""
                        logger.info("Unable to get site. Exception:", e.message)

                if ip_sanitizer(row['POP Converter IP']):

                    # Fetch parent ip, port & type from sheet row
                    pop_converter_parent_ip = ip_sanitizer(row.get('POP Converter Parent IP', ''))
                    pop_converter_parent_type = row.get('POP Converter Parent Type', '')
                    pop_converter_parent_port = row.get('POP Converter Parent Port', '')

                    # pop converter data
                    pop_converter_data = {
                        # 'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'device_name': device_latest_id,
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': bh_device_technology.id if bh_device_technology else "",
                        'device_vendor': bh_device_vendor.id if bh_device_vendor else "",
                        'device_model': bh_device_model.id if bh_device_model else "",
                        'device_type': bh_device_type.id if bh_device_type else "",
                        'ip': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
                        'mac': "",
                        'state': row['State'] if 'State' in row.keys() else "",
                        'city': row['City'] if 'City' in row.keys() else "",
                        'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                        'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                        'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                        'description': 'POP Converter created on {}.'.format(full_time),
                        'parent_ip': pop_converter_parent_ip,
                        'parent_type': pop_converter_parent_type,
                        'parent_port': pop_converter_parent_port
                    }

                    # pop converter object
                    pop_converter = create_device(pop_converter_data)

                    # increment device latest id by 1
                    device_latest_id += 1
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            # backhaul configured on 'port name' and 'port number'
            bh_port = row['Switch/Converter Port'] if 'Switch/Converter Port' in row.keys() else ""
            bh_port_name = ""
            bh_port_number = ""
            if bh_port:
                bh_port_parts = bh_port.rsplit("/", 1)
                try:
                    bh_port_name = bh_port_parts[0]
                except Exception as e:
                    logger.info("BH Configured On port not exist.")

                try:
                    bh_port_number = bh_port_parts[1]
                except Exception as e:
                    logger.info("BH Configured On port number not exist")

            try:
                # ------------------------------- Backhaul -------------------------------
                # bh configured on
                bh_configured_on = ""
                try:
                    bh_configured_on = Device.objects.get(ip_address=row['BH Configured On Switch/Converter'])
                except Exception as e:
                    logger.info(e.message)

                if 'BH Configured On Switch/Converter' in row.keys():
                    if ip_sanitizer(row['BH Configured On Switch/Converter']):
                        # backhaul data
                        backhaul_data = {
                            'ip': row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row.keys() else "",
                            'bh_configured_on': bh_configured_on,
                            'bh_port_name': bh_port,
                            'bh_port': bh_port_number,
                            'bh_type': row['Backhaul Type'] if 'Backhaul Type' in row.keys() else "",
                            'bh_switch': bs_converter,
                            'pop': pop_converter,
                            'aggregator': aggregation_switch,
                            'aggregator_port_name': row['Aggregation Switch Port'] if 'Aggregation Switch Port' in row.keys() else "",
                            'aggregator_port': 0,
                            'pe_hostname': row['PE Hostname'] if 'PE Hostname' in row.keys() else "",
                            'pe_ip': row['PE IP'] if 'PE IP' in row.keys() else "",
                            'bh_connectivity': row['BH Offnet/Onnet'] if 'BH Offnet/Onnet' in row.keys() else "",
                            'bh_circuit_id': row['BH Circuit ID'] if 'BH Circuit ID' in row.keys() else "",
                            'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                            'ttsl_circuit_id': row['BSO Circuit ID'] if 'BSO Circuit ID' in row.keys() else "",
                            'description': 'Backhaul created on {}.'.format(full_time)
                        }

                        # backhaul object
                        backhaul = ""
                        if row['BH Configured On Switch/Converter']:
                            if row['BH Configured On Switch/Converter'] not in ['NA', 'na', 'N/A', 'n/a']:
                                backhaul = create_backhaul(backhaul_data)
                    else:
                        backhaul = ""
                else:
                    backhaul = ""
            except Exception as e:
                backhaul = ""

            try:
                # ------------------------------- Base Station -------------------------------
                # initialize name
                name = ""

                # initialize alias
                alias = ""

                # base station data
                # sanitize bs name
                name = special_chars_name_sanitizer_with_lower_case(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                alias = row['BS Name'] if 'BS Name' in row.keys() else ""
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'organization': organization,
                    'bs_switch': bs_switch,
                    'backhaul': backhaul,
                    'bh_port_name': bh_port,
                    'bh_port': bh_port_number,
                    'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                    'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'bh_capacity': row['BH Capacity'] if 'BH Capacity' in row.keys() else "",
                    'building_height': row['Building Height'] if 'Building Height' in row.keys() else "",
                    'tower_height': row['Tower/Pole Height'] if 'Tower/Pole Height' in row.keys() else "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'address': row['BS Address'] if 'BS Address' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }
                # base station object
                basestation = ""
                if name and alias:
                    basestation = create_basestation(basestation_data)
            except Exception as e:
                basestation = ""

            # increament row number
            row_number += 1

            if errors:
                error_rows.append(row)

        # create error log workbook
        excel_generator_for_new_column('Bulk Upload Errors',
                                       'bulk_upload_errors',
                                       keys_list,
                                       error_rows,
                                       'Backhaul',
                                       file_path,
                                       sheettype)

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        if auto:
            gis_obj.is_new = 0
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


def bulk_upload_error_logger(row=None, sheet=None):
    """ Generate excel workbook containing per row errors during bulk upload

    Args:
        row (dict): dictionary containing excel row data with headers as dictionary keys
        sheet (str): name of sheet i.e. 'wimax_bs'

    Returns:
        errors (str): error in row i.e Base Station Device: Device can't be created without IP.
                                       BS Converter: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.
                                       POP Converter: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.

    """

    # errors
    errors = ""

    # ************************************ DEVICES CHECK ***********************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_bs', 'wimax_bs']:
        # check for base station device
        if 'IP' not in row.keys():
            errors += "Base Station Device: Device can't be created without IP.\n"
        elif row['IP'] in ['na', 'n/a', 'NA', 'N/A']:
            errors += "Base Station Device: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
        elif not ip_sanitizer(row['IP']):
            errors += "Base Station Device: Wrong Base Station Device IP.\n"
        else:
            pass

    if sheet in ['ptp', 'ptp_bh', 'pmp_sm', 'wimax_ss']:
        # check for sub station device
        if 'SS IP' not in row.keys():
            errors += "Sub Station Device: Device can't be created without IP.\n"
        elif row['SS IP'] in ['na', 'n/a', 'NA', 'N/A']:
            errors += "Sub Station Device: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
        elif not ip_sanitizer(row['SS IP']):
            errors += "Sub Station Device: Wrong Sub Station Device IP.\n"
        else:
            pass

    if sheet in ['ptp', 'ptp_bh', 'pmp_bs', 'wimax_bs', 'backhaul']:
        # check for bs switch
        if 'BS Switch IP' in row.keys():
            if not row['BS Switch IP']:
                errors += "BS Switch: Empty BS Switch IP.\n"
            elif row['BS Switch IP'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "BS Switch: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['BS Switch IP']):
                errors += "BS Switch: Wrong BS Switch IP.\n"
            else:
                pass

        # check for aggregation switch
        if 'Aggregation Switch' in row.keys():
            if not row['Aggregation Switch']:
                errors += "Aggregation Switch: Empty Aggregation Switch.\n"
            elif row['Aggregation Switch'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Aggregation Switch: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['BS Switch IP']):
                errors += "Aggregation Switch: Wrong Aggregation Switch IP.\n"
            else:
                pass

        # check for bs converter
        if 'BS Converter IP' in row.keys():
            if not row['BS Converter IP']:
                errors += "BS Converter: Empty BS Converter IP.\n"
            elif row['BS Converter IP'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "BS Converter: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['BS Converter IP']):
                errors += "BS Converter: Wrong BS Converter IP.\n"
            else:
                pass

        # check for pop converter
        if 'POP Converter IP' in row.keys():
            if not row['POP Converter IP']:
                errors += "POP Converter: Empty POP Converter IP.\n"
            elif row['POP Converter IP'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "POP Converter: Device can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['POP Converter IP']):
                errors += "POP Converter: Wrong POP Converter IP.\n"
            else:
                pass

    # ************************************ SECTOR ANTENNA CHECK ***********************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_bs', 'wimax_bs']:
        # check for sector antenna
        # sector antenna row key
        if sheet == 'ptp':
            sector_antenna_key = 'SS Circuit ID'
        elif sheet == 'ptp_bh':
            sector_antenna_key = 'Circuit ID'
        else:
            sector_antenna_key = 'Sector ID'

        if sector_antenna_key in row.keys():
            if not row[sector_antenna_key]:
                errors += "Sector Antenna: Empty {}.\n".format(sector_antenna_key)
            elif row[sector_antenna_key] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector Antenna: Antenna can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass

    # ************************************** SS ANTENNA CHECK *************************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_sm', 'wimax_ss']:
        # check for sub station antenna
        # ss antenna row key
        if sheet in ['ptp', 'ptp_bh']:
            ss_antenna_key = 'SS Circuit ID'
        else:
            ss_antenna_key = 'Sector ID'
        if ss_antenna_key in row.keys():
            if not row[ss_antenna_key]:
                errors += "Sub Station Antenna: Empty {}.\n".format(ss_antenna_key)
            elif row['SS IP'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sub Station Antenna: Antenna can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['SS IP']):
                errors += "Sub Station Antenna: Wrong {}.\n".format(ss_antenna_key)
            else:
                pass

    # ************************************** BACKHAUL CHECK *************************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_bs', 'wimax_bs', 'backhaul']:
        # check for backhaul
        if 'BH Configured On Switch/Converter' in row.keys():
            if not row['BH Configured On Switch/Converter']:
                errors += "Backhaul: Empty BH Configured On Switch/Converter.\n"
            elif row['BH Configured On Switch/Converter'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Backhaul: Backhaul can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['BH Configured On Switch/Converter']):
                errors += "Backhaul: Wrong BH Configured On Switch/Converter.\n"
            else:
                pass

    # *********************************** BASE STATION CHECK ************************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_bs', 'wimax_bs', 'backhaul']:
        # check for base station
        if 'BS Name' in row.keys():
            if not row['BS Name']:
                errors += "Base Station: Empty BS Name.\n"
            elif row['BS Name'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Base Station: Base Station can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass

        # check for city
        if 'City' in row.keys():
            if not row['City']:
                errors += "Base Station: Corrupted Base Station created with no city.\n"
            elif row['City'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Base Station: Corrupted Base Station created with city name as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass

        # check for state
        if 'State' in row.keys():
            if not row['State']:
                errors += "Base Station: Corrupted Base Station created with no state.\n"
            elif row['State'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Base Station: Corrupted Base Station created with state name as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass

    # *********************************** SECTOR CHECK ************************************
    if sheet in ['ptp', 'ptp_bh']:
        # check for sector
        if 'SS Circuit ID' in row.keys():
            if not row['SS Circuit ID']:
                errors += "Sector: Empty SS Circuit ID.\n"
            elif row['SS Circuit ID'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with names 'na', 'n/a', 'NA', 'N/A'.\n"
            elif not ip_sanitizer(row['SS Circuit ID']):
                errors += "Sector: Wrong SS Circuit ID.\n"
            else:
                pass
    if sheet in ['pmp_bs']:
        # check for sector id
        if 'Sector ID' in row.keys():
            if not row['Sector ID']:
                errors += "Sector: Empty Sector ID.\n"
            elif row['Sector ID'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with sector id as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass
        # check for sector name
        if 'Sector Name' in row.keys():
            if not row['Sector Name']:
                errors += "Sector: Corrupted sector created without sector name.\n"
            elif row['Sector Name'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with sector name as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass
    if sheet in ['wimax_bs']:
        # check for sector id
        if 'Sector ID' in row.keys():
            if not row['Sector ID']:
                errors += "Sector: Empty Sector ID.\n"
            elif row['Sector ID'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with sector id as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass
        # check for sector name
        if 'Sector Name' in row.keys():
            if not row['Sector Name']:
                errors += "Sector: Corrupted sector created without sector name.\n"
            elif row['Sector Name'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with sector name as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass
        # check for pmp port
        if 'PMP Port' in row.keys():
            if not row['PMP Port']:
                errors += "Sector: Corrupted sector created without pmp port.\n"
            elif row['PMP Port'] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sector: Sector can't be created with pmp port as 'na', 'n/a', 'NA', 'N/A'.\n"
            else:
                pass

    # *********************************** SUB STATION CHECK ***********************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_sm', 'wimax_ss']:
        # sub station name
        if sheet in ['ptp', 'ptp_bh']:
            substation_name = 'SS Circuit ID'
        else:
            substation_name = 'Circuit ID'

        # check for sub station
        if substation_name in row.keys():
            if not row[substation_name]:
                errors += "Sub Station: Empty SS Circuit ID.\n"
            elif row[substation_name] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Sub Station: Sub Station can't be created with {} as 'na', 'n/a', 'NA', 'N/A'.\n".format(
                    substation_name)
            else:
                pass

    # *********************************** CUSTOMER CHECK **************************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_sm', 'wimax_ss']:
        # customer name and circuit id keys
        if sheet in ['ptp', 'ptp_bh']:
            customer_name_key = 'SS Customer Name'
            circuit_id_key = 'SS Circuit ID'
        else:
            customer_name_key = 'Customer Name'
            circuit_id_key = 'Circuit ID'

        # check for customer name
        if customer_name_key in row.keys():
            if not row[customer_name_key]:
                errors += "Customer: Empty {}.\n".format(customer_name_key)
            elif row[customer_name_key] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Customer: Customer can't be created with {} as 'na', 'n/a', 'NA', 'N/A'.\n".format(
                    customer_name_key)
            else:
                pass

        # check for circuit id
        if circuit_id_key in row.keys():
            if not row[circuit_id_key]:
                errors += "Customer: Corrupted Customer created without {}.\n".format(circuit_id_key)
            elif row[circuit_id_key] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Customer: Customer can't be created with {} as 'na', 'n/a', 'NA', 'N/A'.\n".format(
                    circuit_id_key)
            else:
                pass

    # *********************************** CIRCUIT CHECK **************************************
    if sheet in ['ptp', 'ptp_bh', 'pmp_sm', 'wimax_ss']:
        # circuit id keys
        if sheet in ['ptp', 'ptp_bh']:
            circuit_id_key = 'SS Circuit ID'
        else:
            circuit_id_key = 'Circuit ID'

        # check for circuit id
        if circuit_id_key in row.keys():
            if not row[circuit_id_key]:
                errors += "Circuit: Corrupted Circuit created without {}.\n".format(circuit_id_key)
            elif row[circuit_id_key] in ['na', 'n/a', 'NA', 'N/A']:
                errors += "Circuit: Circuit can't be created with {} as 'na', 'n/a', 'NA', 'N/A'.\n".format(
                    circuit_id_key)
            else:
                pass

    return errors


def bulk_upload_error_file_generator(keys_list, error_rows, sheettype, file_path, workbook):
    """ Generate excel workbook containing per row errors during bulk upload

    Args:
        keys_list (list): list containing names of excel columns
        error_rows (list) : list of dictionaries containing excel rows
        sheettype (unicode): type of sheet i.e. valid/invalid
        filepath (unicode): path of file i.e. inventory_files/invalid/2014-12-29-02-18-32_invalid_WiMAX Few Rows.xls
        workbook (str): sheet name i.e. 'PMP BS'

    Returns:
        device (class 'device.models.Device'): <Device: 10.75.158.219>

    """

    # error rows list
    error_rows_list = []

    # headers for excel sheet
    headers = keys_list

    # append errors key in keys_list
    keys_list.append('Bulk Upload Errors')

    for val in error_rows:
        temp_list = list()
        for key in keys_list:
            try:
                temp_list.append(val[key])
            except Exception as e:
                logger.info(e.message)
        error_rows_list.append(temp_list)

    wb_bulk_upload_errors = xlwt.Workbook()
    ws_bulk_upload_errors = wb_bulk_upload_errors.add_sheet(workbook)

    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')
    style_errors = xlwt.easyxf('pattern: pattern solid, fore_colour red;' 'font: colour white, bold True;')

    try:
        for i, col in enumerate(headers):
            if col != 'Bulk Upload Errors':
                ws_bulk_upload_errors.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
            else:
                ws_bulk_upload_errors.write(0, i, col.decode('utf-8', 'ignore').strip(), style_errors)
    except Exception as e:
        pass

    try:
        for i, l in enumerate(error_rows_list):
            i += 1
            for j, col in enumerate(l):
                ws_bulk_upload_errors.write(i, j, col)
    except Exception as e:
        pass

    # bulk upload errors file path
    if sheettype == 'valid':
        bulk_upload_file_path = file_path.replace('valid', 'bulk_upload_errors')
    elif sheettype == 'invalid':
        bulk_upload_file_path = file_path.replace('invalid', 'bulk_upload_errors')
    else:
        bulk_upload_file_path = None

    # if directory for bulk upload excel sheets didn't exist than create one
    if not os.path.exists(MEDIA_ROOT + 'inventory_files/bulk_upload_errors'):
        os.makedirs(MEDIA_ROOT + 'inventory_files/bulk_upload_errors')

    # saving bulk upload errors excel sheet
    try:
        wb_bulk_upload_errors.save(MEDIA_ROOT + bulk_upload_file_path)
    except Exception as e:
        logger.info(e.message)


@task()
def bulk_upload_delta_generator(gis_ob_id, workbook_type, sheet_type):
    # gis object
    gis_obj = None
    try:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_ob_id)
    except Exception as e:
        logger.info("No GIS object exist. Exception: ", e)
    # workbook type i.e. valid/invalid
    workbook_type = workbook_type

    # sheet type i.e. PTP/PTP BH/PMP BS/PMP SM/Wimax BS/Wimax SS/Backhaul
    sheet_type = sheet_type

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get valid or invalid workbook based upon workbook type
    file_path = ""
    if workbook_type == 'valid':
        file_path = gis_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif workbook_type == 'invalid':
        file_path = gis_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] in ["Date Of Acceptance", "SS Date Of Acceptance"]:
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # delta
    delta_list = []

    try:
        for row in complete_d:
            # current delta
            current_delta = ""

            # ********************************* BS DEVICE DELTA CHECK ********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:
                if 'IP' in row:
                    if row['IP']:
                        bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['IP']))
                        if bs_device:
                            current_delta += "BS Device: Updated \n"
                        else:
                            current_delta += "BS Device: Created \n"
                    else:
                        current_delta += "BS Device: NA \n"
                if sheet_type in ['PMP BS']:
                    if 'ODU IP' in row:
                        if row['ODU IP']:
                            bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['ODU IP']))
                            if bs_device:
                                current_delta += "BS Device: Updated \n"
                            else:
                                current_delta += "BS Device: Created \n"
                        else:
                            current_delta += "BS Device: NA \n"
                if sheet_type in ['PMP BS']:
                    if 'IDU IP' in row:
                        if row['IDU IP']:
                            bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['IDU IP']))
                            if bs_device:
                                current_delta += "BS Device: Updated \n"
                            else:
                                current_delta += "BS Device: Created \n"
                        else:
                            current_delta += "BS Device: NA \n"

            # ********************************* SS DEVICE DELTA CHECK ********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                if 'SS IP' in row:
                    if row['SS IP']:
                        ss_device = Device.objects.filter(ip_address=ip_sanitizer(row['SS IP']))
                        if ss_device:
                            current_delta += "SS Device: Updated \n"
                        else:
                            current_delta += "SS Device: Created \n"
                    else:
                        current_delta += "SS Device: NA \n"

            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS', 'Backhaul']:
                # ********************************** BS SWITCH DELTA CHECK **********************************
                if 'BS Switch IP' in row:
                    if row['BS Switch IP']:
                        bs_switch_device = Device.objects.filter(ip_address=ip_sanitizer(row['BS Switch IP']))
                        if bs_switch_device:
                            current_delta += "BS Switch Device: Updated \n"
                        else:
                            current_delta += "BS Switch Device: Created \n"
                    else:
                        current_delta += "BS Switch Device: NA \n"

                # ********************************* AGGREGATOR DELTA CHECK ***********************************
                if 'Aggregation Switch' in row:
                    if row['Aggregation Switch']:
                        aggregator_device = Device.objects.filter(ip_address=ip_sanitizer(row['Aggregation Switch']))
                        if aggregator_device:
                            current_delta += "Aggregation Switch Device: Updated \n"
                        else:
                            current_delta += "Aggregation Switch Device: Created \n"
                    else:
                        current_delta += "Aggregation Switch Device: NA \n"

                # ********************************* BS CONVERTER DELTA CHECK *********************************
                if 'BS Converter IP' in row:
                    if row['BS Converter IP']:
                        bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['BS Converter IP']))
                        if bs_device:
                            current_delta += "BS Converter Device: Updated \n"
                        else:
                            current_delta += "BS Converter Device: Created \n"
                    else:
                        current_delta += "BS Converter Device: NA \n"

                # ********************************* POP CONVERTER DELTA CHECK ********************************
                if 'POP Converter IP' in row:
                    if row['POP Converter IP']:
                        bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['POP Converter IP']))
                        if bs_device:
                            current_delta += "POP Converter Device: Updated \n"
                        else:
                            current_delta += "POP Converter Device: Created \n"
                    else:
                        current_delta += "POP Converter Device: NA \n"

            # *********************************** SECTOR ANTENNA CHECK *********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:
                # sector antenna name
                sector_antenna_name = ""

                if sheet_type in ['PTP']:
                    sector_antenna_name = '{}_ne'.format(special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else ""))
                elif sheet_type in ['PTP BH']:
                    sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row else "")
                elif sheet_type in ['PMP BS']:
                    sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID'] if 'Sector ID' in row else "")
                elif sheet_type in ['Wimax BS']:
                    sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID'] if 'Sector ID' in row else "")
                else:
                    pass

                if sector_antenna_name:
                    # sector antenna
                    sector_antenna = Antenna.objects.filter(name=sector_antenna_name)

                    if sector_antenna:
                        current_delta += "Sector Antenna: Updated \n"
                    else:
                        current_delta += "Sector Antenna: Created \n"

            # ************************************* SS ANTENNA CHECK **********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # ss antenna name
                ss_antenna_name = ""

                if sheet_type in ['PTP']:
                    ss_antenna_name = '{}_ne'.format(special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else ""))
                elif sheet_type in ['PTP BH']:
                    ss_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else "")
                elif sheet_type in ['PMP SM']:
                    ss_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else "")
                elif sheet_type in ['Wimax SS']:
                    ss_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row else "")
                else:
                    pass

                if ss_antenna_name:
                    # ss antenna
                    ss_antenna = Antenna.objects.filter(name=ss_antenna_name)

                    if ss_antenna:
                        current_delta += "SS Antenna: Updated \n"
                    else:
                        current_delta += "SS Antenna: Created \n"

            # ************************************* BACKHAUL CHECK **********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS', 'Backhaul']:
                backhaul_name = ip_sanitizer(
                    row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row else "")

                # backhaul
                if backhaul_name:
                    backhaul = Backhaul.objects.filter(name=backhaul_name)

                    if backhaul:
                        current_delta += "Backhaul: Updated \n"
                    else:
                        current_delta += "Backhaul: Created \n"

            # *********************************** BASE STATION CHECK ********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS', 'Backhaul']:
                # base station name
                base_station_name = ""
                bs_temp_name = special_chars_name_sanitizer_with_lower_case(
                    row['BS Name'] if 'BS Name' in row.keys() else "")
                try:
                    if all(k in row for k in ("BS Name", "City", "State")):
                        # concatinate city and state in bs name
                        base_station_name = "{}_{}_{}".format(bs_temp_name,
                                                              row['City'][:3].lower() if 'City' in row.keys() else "",
                                                              row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                # base station
                if base_station_name:
                    base_station = BaseStation.objects.filter(name=base_station_name)

                    if base_station:
                        current_delta += "Base Station: Updated \n"
                    else:
                        current_delta += "Base Station: Created \n"

            # ************************************* SECTOR CHECK ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:
                # ss antenna name
                sector_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    sector_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP BS']:
                    sector_name = '{}_{}'.format(special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID']) if 'Sector ID' in row.keys() else "",
                        row['Sector Name'] if 'Sector Name' in row.keys() else "")
                elif sheet_type in ['Wimax BS']:
                    # pmp name
                    pmp = ""
                    try:
                        if 'PMP' in row.keys():
                            pmp = row['PMP']
                            if isinstance(pmp, basestring) or isinstance(pmp, float):
                                pmp = int(pmp)
                    except Exception as e:
                        pass

                    # sector name
                    sector_name = '{}_{}_{}'.format(special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID']) if 'Sector ID' in row.keys() else "",
                        row['Sector Name'] if 'Sector Name' in row.keys() else "", pmp)
                else:
                    pass

                # base station
                if sector_name:
                    sector = Sector.objects.filter(name=sector_name)

                    if sector:
                        current_delta += "Sector: Updated \n"
                    else:
                        current_delta += "Sector: Created \n"

            # ************************************ SUBSTATION CHECK **********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # substation name
                substation_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    substation_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    substation_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                else:
                    pass

                if substation_name:
                    # substation
                    substation = SubStation.objects.filter(name=substation_name)

                    if substation:
                        current_delta += "Sub Station: Updated \n"
                    else:
                        current_delta += "Sub Station: Created \n"

            # ************************************ CUSTOMER CHECK ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # customer name
                customer_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    customer_name = "{0}_{1}_{1}".format(
                        special_chars_name_sanitizer_with_lower_case(
                            row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""),
                        special_chars_name_sanitizer_with_lower_case(
                            row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""))
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    customer_name = "{}_{}".format(
                        special_chars_name_sanitizer_with_lower_case(
                            row['Customer Name'] if 'Customer Name' in row.keys() else ""),
                        special_chars_name_sanitizer_with_lower_case(
                            row['Circuit ID'] if 'Circuit ID' in row.keys() else ""))
                else:
                    pass

                if customer_name:
                    # customer
                    customer = Customer.objects.filter(name=customer_name)

                    if customer:
                        current_delta += "Customer: Updated \n"
                    else:
                        current_delta += "Customer: Created \n"

            # ************************************ CIRCUIT CHECK ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # circuit name
                circuit_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    circuit_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    circuit_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                else:
                    pass

                if circuit_name:
                    # circuit
                    circuit = Circuit.objects.filter(name=circuit_name)

                    if circuit:
                        current_delta += "Circuit: Updated \n"
                    else:
                        current_delta += "Circuit: Created \n"

            # adding delta key in current row
            row['Current Delta'] = current_delta

            delta_list.append(row)

        # create error log workbook
        excel_generator_for_new_column('Current Delta',
                                       'bulk_upload_deltas',
                                       keys_list,
                                       delta_list,
                                       sheet_type,
                                       file_path,
                                       workbook_type,
                                       1)

    except Exception as e:
        logger.exception(e.message)


@task()
def delete_gis_inventory(gis_ob_id, workbook_type, sheet_type, auto=''):
    # gis object
    gis_obj = None
    try:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_ob_id)
    except Exception as e:
        logger.info("No GIS object exist. Exception: ", e)
    # workbook type i.e. valid/invalid
    workbook_type = workbook_type

    # sheet type i.e. PTP/PTP BH/PMP BS/PMP SM/Wimax BS/Wimax SS/Backhaul
    sheet_type = sheet_type

    # timestamp
    timestamp = time.time()
    full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y at %H:%M:%S')

    # get valid or invalid workbook based upon workbook type
    file_path = ""
    if workbook_type == 'valid':
        file_path = gis_obj.valid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    elif workbook_type == 'invalid':
        file_path = gis_obj.invalid_filename
        file_path = "".join(file_path.split("/media"))
        book = xlrd.open_workbook(MEDIA_ROOT + file_path)
    else:
        book = ""

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

    # fetching excel rows values as list of key value pair dictionaries where keys are from first row of excel
    # and values are form other remaining rows
    for row_index in xrange(1, sheet.nrows):
        d = dict()
        for col_index in xrange(len(keys)):
            if keys[col_index] in ["Date Of Acceptance", "SS Date Of Acceptance"]:
                if isinstance(sheet.cell(row_index, col_index).value, float):
                    try:
                        d[keys[col_index].encode('utf-8').strip()] = datetime.datetime(
                            *xlrd.xldate_as_tuple(sheet.cell(row_index, col_index).value, book.datemode)).date()
                    except Exception as e:
                        logger.info("Date of Exception Error. Exception: {}".format(e.message))
            else:
                if isinstance(sheet.cell(row_index, col_index).value, str):
                    d[keys[col_index].encode('utf-8').strip()] = unicode(sheet.cell(row_index, col_index).value).strip()
                elif isinstance(sheet.cell(row_index, col_index).value, unicode):
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value.strip()
                else:
                    d[keys[col_index].encode('utf-8').strip()] = sheet.cell(row_index, col_index).value

        complete_d.append(d)

    # delta
    deleted_list = []

    try:
        count = 0
        for row in complete_d:
            count += 1
            logger.exception("************************************* Row deleted: {}".format(count))

            # current delta
            deleted_rows = list()

            is_dr = False
            # ********************************* BS DEVICE DELETION ********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:

                # PTP/ PTP BH
                if 'IP' in row:
                    if row['IP']:
                        bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['IP']))
                        if bs_device.exists():
                            # delete bs device
                            bs_device.delete()
                            deleted_rows.insert(0, "BS Device: Deleted \n")
                        else:
                            deleted_rows.insert(0, "BS Device: Not Exist \n")
                    else:
                        deleted_rows.insert(0, "BS Device: NA \n")

                # PMP
                if sheet_type in ['PMP BS']:
                    if 'ODU IP' in row:
                        if row['ODU IP']:
                            bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['ODU IP']))
                            if bs_device.exists():
                                # delete bs device
                                bs_device.delete()
                                deleted_rows.insert(0, "BS Device: Deleted \n")
                            else:
                                deleted_rows.insert(0, "BS Device: Not Exist \n")
                        else:
                            deleted_rows.insert(0, "BS Device: NA \n")

                # Wimax
                if sheet_type in ['Wimax BS']:
                    if 'IDU IP' in row:
                        if row['IDU IP']:
                            bs_device = Device.objects.filter(ip_address=ip_sanitizer(row['IDU IP']))
                            if bs_device.exists():
                                try:
                                    # Total Sectors connected to this device
                                    total_sectors = bs_device[0].sector_configured_on.all().count()

                                    # Total DR Sectors connected to this device
                                    total_dr_sectors = bs_device[0].dr_configured_on.all().count()

                                    if total_dr_sectors > 0:
                                        is_dr = True

                                    # Delete the sector device if their is only one sector is present in inventory
                                    if total_sectors == 1 and total_dr_sectors == 0:
                                        # delete bs device
                                        bs_device.delete()
                                        deleted_rows.insert(0, "BS Device: Deleted \n")
                                    elif total_dr_sectors == 1 and total_sectors == 0:
                                        # delete bs device
                                        bs_device.delete()
                                        deleted_rows.insert(0, "BS Device: Deleted \n")
                                except Exception, e:
                                    pass
                            else:
                                deleted_rows.insert(0, "BS Device: Not Exist \n")
                        else:
                            deleted_rows.insert(0, "BS Device: NA \n")

            # *********************************** SECTOR ANTENNA DELETION *********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:
                # sector antenna name
                sector_antenna_name = ""

                if sheet_type in ['PTP']:
                    sector_antenna_name = '{}_ne'.format(special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else ""))
                elif sheet_type in ['PTP BH']:
                    sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row else "")
                elif sheet_type in ['PMP BS']:
                    sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID'] if 'Sector ID' in row else "")
                elif sheet_type in ['Wimax BS']:
                    if not is_dr:
                        sector_antenna_name = special_chars_name_sanitizer_with_lower_case(
                            row['Sector ID'] if 'Sector ID' in row else ""
                        )
                else:
                    pass

                if sector_antenna_name:
                    # sector antenna
                    sector_antenna = Antenna.objects.filter(name=sector_antenna_name)

                    if sector_antenna.exists():
                        # delete setor antenna
                        sector_antenna.delete()
                        deleted_rows.insert(0, "Sector Antenna: Deleted \n")
                    else:
                        deleted_rows.insert(0, "Sector Antenna: Not Exist \n")

            # ************************************* SS ANTENNA DELETION **********************************
            if sheet_type in ['PMP SM', 'Wimax SS']:
                # ss antenna name
                ss_antenna_name = ""

                if sheet_type in ['PMP SM']:
                    ss_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row else "")
                elif sheet_type in ['Wimax SS']:
                    ss_antenna_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row else "")
                else:
                    pass

                if ss_antenna_name:
                    # ss antenna
                    ss_antenna = Antenna.objects.filter(name=ss_antenna_name)

                    if ss_antenna.exists():
                        # delete ss antenna
                        ss_antenna.delete()
                        deleted_rows.insert(0, "SS Antenna: Deleted \n")
                    else:
                        deleted_rows.insert(0, "SS Antenna: Not Exist \n")

            # ********************************* SS DEVICE DELETION ********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                if 'SS IP' in row:
                    if row['SS IP']:
                        ss_device = Device.objects.filter(ip_address=ip_sanitizer(row['SS IP']))
                        if ss_device.exists():
                            # delete ss
                            ss_device.delete()
                            deleted_rows.insert(0, "SS Device: Deleted \n")
                        else:
                            deleted_rows.insert(0, "SS Device: Not Exist \n")
                    else:
                        deleted_rows.insert(0, "SS Device: NA \n")

            # if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS', 'Backhaul']:
            #     # ********************************** BS SWITCH DELETION **********************************
            #     if 'BS Switch IP' in row:
            #         if row['BS Switch IP']:
            #             bs_switch_device = Device.objects.filter(ip_address=ip_sanitizer(row['BS Switch IP']))
            #             if bs_switch_device.exists():
            #                 # bs switch device
            #                 bs_switch_device.delete()
            #                 deleted_rows.insert(0, "BS Switch Device: Deleted \n")
            #             else:
            #                 deleted_rows.insert(0, "BS Switch Device: Not Exist \n")
            #         else:
            #             deleted_rows.insert(0, "BS Switch Device: NA \n")

            #     # ********************************* AGGREGATOR DELETION ***********************************
            #     if 'Aggregation Switch' in row:
            #         if row['Aggregation Switch']:
            #             aggregator_device = Device.objects.filter(ip_address=ip_sanitizer(row['Aggregation Switch']))
            #             if aggregator_device.exists():
            #                 # delete aggregator device
            #                 aggregator_device.delete()
            #                 deleted_rows.insert(0, "Aggregation Switch Device: Deleted \n")
            #             else:
            #                 deleted_rows.insert(0, "Aggregation Switch Device: Not Exist \n")
            #         else:
            #             deleted_rows.insert(0, "Aggregation Switch Device: NA \n")

            #     # ********************************* BS CONVERTER DELETION *********************************
            #     if 'BS Converter IP' in row:
            #         if row['BS Converter IP']:
            #             bs_converter = Device.objects.filter(ip_address=ip_sanitizer(row['BS Converter IP']))
            #             if bs_converter.exists():
            #                 # delete bs converter
            #                 bs_converter.delete()
            #                 deleted_rows.insert(0, "BS Converter Device: Deleted \n")
            #             else:
            #                 deleted_rows.insert(0, "BS Converter Device: Not Exist \n")
            #         else:
            #             deleted_rows.insert(0, "BS Converter Device: NA \n")

            #     # ********************************* POP CONVERTER DELETION ********************************
            #     if 'POP Converter IP' in row:
            #         if row['POP Converter IP']:
            #             pop_converter = Device.objects.filter(ip_address=ip_sanitizer(row['POP Converter IP']))
            #             if pop_converter.exists():
            #                 # delete pop converter
            #                 pop_converter.delete()
            #                 deleted_rows.insert(0, "POP Converter Device: Deleted \n")
            #             else:
            #                 deleted_rows.insert(0, "POP Converter Device: Not Exist \n")
            #         else:
            #             deleted_rows.insert(0, "POP Converter Device: NA \n")

            # ************************************ CUSTOMER DELETION ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # customer name
                customer_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    customer_name = "{0}_{1}_{1}".format(
                        special_chars_name_sanitizer_with_lower_case(
                            row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""),
                        special_chars_name_sanitizer_with_lower_case(
                            row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""))
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    customer_name = "{}_{}".format(
                        special_chars_name_sanitizer_with_lower_case(
                            row['Customer Name'] if 'Customer Name' in row.keys() else ""),
                        special_chars_name_sanitizer_with_lower_case(
                            row['Circuit ID'] if 'Circuit ID' in row.keys() else ""))
                else:
                    pass

                if customer_name:
                    # customer
                    customer = Customer.objects.filter(name=customer_name)

                    if customer.exists():
                        # delete customer
                        customer.delete()
                        deleted_rows.insert(0, "Customer: Deleted \n")
                    else:
                        deleted_rows.insert(0, "Customer: Not Exist \n")

            # ************************************ CIRCUIT DELETION ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # circuit name
                circuit_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    circuit_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    circuit_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                else:
                    pass

                if circuit_name:
                    # circuit
                    circuit = Circuit.objects.filter(name=circuit_name)

                    if circuit.exists():
                        # delete circuit
                        circuit.delete()
                        deleted_rows.insert(0, "Circuit: Deleted \n")
                    else:
                        deleted_rows.insert(0, "Circuit: Not Exist \n")

            # ************************************ SUBSTATION DELETION **********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP SM', 'Wimax SS']:
                # substation name
                substation_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    substation_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP SM', 'Wimax SS']:
                    substation_name = special_chars_name_sanitizer_with_lower_case(
                        row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                else:
                    pass

                if substation_name:
                    substation = SubStation.objects.filter(name=substation_name)

                    if substation.exists():
                        # delete substation
                        substation.delete()
                        deleted_rows.insert(0, "Sub Station: Deleted \n")
                    else:
                        deleted_rows.insert(0, "Sub Station: Not Exist \n")

            # ************************************* SECTOR DELETION ***********************************
            if sheet_type in ['PTP', 'PTP BH', 'PMP BS', 'Wimax BS']:
                # ss antenna name
                sector_name = ""

                if sheet_type in ['PTP', 'PTP BH']:
                    sector_name = special_chars_name_sanitizer_with_lower_case(
                        row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                elif sheet_type in ['PMP BS']:
                    sector_name = '{}_{}'.format(special_chars_name_sanitizer_with_lower_case(
                        row['Sector ID']) if 'Sector ID' in row.keys() else "",
                        row['Sector Name'] if 'Sector Name' in row.keys() else "")
                elif sheet_type in ['Wimax BS']:
                    if not is_dr:
                        # pmp name
                        pmp = ""
                        try:
                            if 'PMP' in row.keys():
                                pmp = row['PMP']
                                if isinstance(pmp, basestring) or isinstance(pmp, float):
                                    pmp = int(pmp)
                        except Exception as e:
                            pass

                        # sector name
                        sector_name = '{}_{}_{}'.format(
                            special_chars_name_sanitizer_with_lower_case(
                                row['Sector ID']
                            ) if 'Sector ID' in row.keys() else "",
                            row['Sector Name'] if 'Sector Name' in row.keys() else "",
                            pmp
                        )
                else:
                    pass

                # base station
                if sector_name:
                    sector = Sector.objects.filter(name=sector_name)

                    if sector.exists():
                        # delete sector
                        sector.delete()
                        deleted_rows.insert(0, "Sector: Deleted \n")
                    else:
                        deleted_rows.insert(0, "Sector: Not Exist \n")

            # ************************************* BACKHAUL DELETION **********************************
            # if sheet_type in ['Backhaul']:
            #     backhaul_name = ip_sanitizer(
            #         row['BH Configured On Switch/Converter'] if 'BH Configured On Switch/Converter' in row else "")

            #     # backhaul
            #     if backhaul_name:
            #         backhaul = Backhaul.objects.filter(name=backhaul_name)

            #         if backhaul.exists():
            #             # delete backhaul
            #             backhaul.delete()
            #             deleted_rows.insert(0, "Backhaul: Deleted \n")
            #         else:
            #             deleted_rows.insert(0, "Backhaul: Not Exist \n")

            # adding delta key in current row
            row['Deleted'] = "".join(deleted_rows)

            deleted_list.append(row)

        # create delta workbook
        excel_generator_for_new_column(
            'Deleted',
            'deleted_inventory',
            keys_list,
            deleted_list,
            sheet_type,
            file_path,
            workbook_type,
            1
        )

        if auto:
            gis_obj.is_new = 0
            gis_obj.save()

    except Exception as e:
        logger.exception(e.message)


def excel_generator_for_new_column(col_name,
                                   directory,
                                   keys_list,
                                   rows,
                                   sheettype,
                                   file_path,
                                   workbook,
                                   rep_count=None):
    """ Generate excel workbook with new column added in sheet

    Args:
        col_name (str): name of new column i.e. 'Bulk Upload Errors'
        directory (str): name of directory for workbook i.e. 'bulk_upload_errors'
        keys_list (list): list containing names of excel columns
        rows (list) : list of dictionaries containing excel rows
        sheettype (unicode): type of sheet i.e. valid/invalid
        filepath (unicode): path of file i.e. inventory_files/invalid/2014-12-29-02-18-32_invalid_WiMAX Few Rows.xls
        workbook (str): sheet name i.e. 'PMP BS'
        rep_count (int): number of occurences of string needs to be replaced i.e. 1

    Returns:

    """

    # rows list
    rows_list = []

    # column name
    column_name = col_name

    # headers for excel sheet
    headers = keys_list

    # append errors key in keys_list

    keys_list.append(column_name)

    for row in rows:
        temp_list = list()
        for key in keys_list:
            try:
                temp_list.append(row[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        rows_list.append(temp_list)

    new_workbook = xlwt.Workbook()
    new_worksheet = new_workbook.add_sheet(sheettype)

    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')
    style_new_row = xlwt.easyxf('pattern: pattern solid, fore_colour red;' 'font: colour white, bold True;')

    try:
        for i, col in enumerate(headers):
            if col != column_name:
                new_worksheet.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
            else:
                new_worksheet.write(0, i, col.decode('utf-8', 'ignore').strip(), style_new_row)

    except Exception as e:
        pass

    try:

        for i, l in enumerate(rows_list):
            i += 1
            for j, col in enumerate(l):
                new_worksheet.write(i, j, col)
    except Exception as e:
        pass

    # file path
    if rep_count:
        if workbook == 'valid':
            upload_file_path = file_path.replace('valid', directory, rep_count)
        elif workbook == 'invalid':
            upload_file_path = file_path.replace('invalid', directory, rep_count)
        else:
            upload_file_path = None
    else:
        if workbook == 'valid':
            upload_file_path = file_path.replace('valid', directory)
        elif workbook == 'invalid':
            upload_file_path = file_path.replace('invalid', directory)
        else:
            upload_file_path = None

    # if directory didn't exist than create one
    if not os.path.exists(MEDIA_ROOT + 'inventory_files/{}'.format(directory)):
        os.makedirs(MEDIA_ROOT + 'inventory_files/{}'.format(directory))

    # saving excel sheet
    try:
        new_workbook.save(MEDIA_ROOT + upload_file_path)

    except Exception as e:
        logger.info(e.message)


@task
def validate_file_for_bulk_upload(op_type=''):
    """
    Validate inventory files for bulk upload.
    """
    # if directory didn't exist than create one
    if op_type in ['c', 'd']:
        if op_type == 'c':
            auto_upload_dir = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/create'
            is_new_bit = 1
            uploaded_by = "Auto Upload"
        elif op_type == 'd':
            auto_upload_dir = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/delete'
            is_new_bit = 2
            uploaded_by = "Auto Delete"
        else:
            return False

        if os.path.exists(auto_upload_dir) and os.listdir(auto_upload_dir):
            count = 0
            for ufile in os.listdir(auto_upload_dir):
                count += 1
                logger.exception("########################################################## {}".format(count))

                if op_type == 'c':
                    # File path.
                    filepath = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/create/' + ufile

                    # Relative file path.
                    relative_filepath = 'inventory_files/auto_upload_inventory/create/' + ufile
                elif op_type == 'd':
                    # File path.
                    filepath = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/delete/' + ufile

                    # Relative file path.
                    relative_filepath = 'inventory_files/auto_upload_inventory/delete/' + ufile
                else:
                    return False

                # Current timestamp.
                timestamp = time.time()

                # Formatted time.
                full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')

                # Destination path (Where we need to move files after processing of scheduled inventory.)
                dest = MEDIA_ROOT + 'inventory_files/original'

                # if directory didn't exist than create one
                if not os.path.exists(dest):
                    os.makedirs(dest)

                # Description for the uploaded inventory.
                description = "Auto upload inventory on {}".format(full_time)

                # Valid sheet names.
                valid_sheets = ["Wimax BS", "Wimax SS", "PMP BS", "PMP SM", "Converter", "PTP", "PTP BH", "Backhaul"]

                # Reading workbook using 'xlrd' module.
                try:
                    # Open the workbook.
                    book = xlrd.open_workbook(filepath, formatting_info=True)

                    # List sheet names, and pull a sheet by name.
                    sheet_names = book.sheet_names()

                    for sheet_name in sheet_names:
                        # Current timestamp.
                        x = time.time()

                        # Formatted time.
                        fulltimestamp = datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d-%H-%M-%S-%f')
                        # Get the technology of uploaded inventory sheet.
                        if "Wimax" in sheet_name:
                            technology = "Wimax"
                        elif "PMP" in sheet_name:
                            technology = "PMP"
                        elif "PTP" in sheet_name:
                            technology = "PTP"
                        elif "Backhaul" in sheet_name:
                            technology = "Backhaul"
                        elif "Converter" in sheet_name:
                            technology = "Converter"
                        else:
                            technology = "Unknown"

                        # execute only if a valid sheet is selected from form
                        if sheet_name in valid_sheets:
                            sheet = book.sheet_by_name(sheet_name)

                            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if
                                    sheet.cell(0, col_index).value]

                            keys_list = [x.encode('utf-8').strip() for x in keys]

                            complete_d = list()
                            for row_index in xrange(1, sheet.nrows):
                                d = {keys[col_index].encode('utf-8').strip(): sheet.cell(row_index, col_index).value
                                     for col_index in xrange(len(keys))}
                                complete_d.append(d)

                            # book_to_upload = xlcopy(book)
                            dest_filename = sheet_name.lower().replace(' ', '_').strip() + '_' + fulltimestamp + '.xls'
                            try:
                                shutil.copyfile(filepath, dest + '/' + dest_filename)
                            except Exception as e:
                                description = e.message
                                logger.exception(e.message)

                            gis_bulk_obj = GISInventoryBulkImport()
                            gis_bulk_obj.original_filename = dest + '/' + dest_filename
                            gis_bulk_obj.status = 0
                            gis_bulk_obj.sheet_name = sheet_name
                            gis_bulk_obj.technology = technology
                            gis_bulk_obj.description = description
                            gis_bulk_obj.uploaded_by = uploaded_by
                            gis_bulk_obj.is_auto = 1
                            gis_bulk_obj.is_new = is_new_bit
                            gis_bulk_obj.save()
                            gis_bulk_id = gis_bulk_obj.id

                            result = validate_gis_inventory_excel_sheet.delay(
                                gis_bulk_id,
                                complete_d,
                                sheet_name,
                                keys_list,
                                full_time,
                                dest_filename
                            )
                
                    try:
                        os.remove(filepath)
                    except Exception, e:
                        pass
                except Exception as e:
                    logger.info("Workbook not uploaded. Exception: ", e.message)
        else:
            logger.exception("Not there.")
    else:
        return False


@task
def process_file_for_bulk_upload():
    """
    Background processing of inventories for bulk upload.
    """
    # Get inventories which are not processed yet.
    inventories = GISInventoryBulkImport.objects.filter(is_new=1)

    if inventories:
        for inventory in inventories:
            # user organization
            organization = ''

            try:
                # Organization.
                organization = Organization.objects.get(name="TCL")

                # Update data import status in GISInventoryBulkImport model.
                gis_obj = None
                sheet_name = ''
                try:
                    gis_obj = inventory
                    gis_obj.upload_status = 1
                    gis_obj.save()
                    sheet_name = gis_obj.sheet_name
                except Exception as e:
                    logger.info(e.message)
                    
                if sheet_name == 'PTP':
                    valid_result = bulk_upload_ptp_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_ptp_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'PTP BH':
                    valid_result = bulk_upload_ptp_bh_inventory.delay(gis_obj.id, organization, 'valid' 'auto')
                    invalid_result = bulk_upload_ptp_bh_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'PMP BS':
                    valid_result = bulk_upload_pmp_bs_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_pmp_bs_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'PMP SM':
                    valid_result = bulk_upload_pmp_sm_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_pmp_sm_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'Wimax BS':
                    valid_result = bulk_upload_wimax_bs_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_wimax_bs_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'Wimax SS':
                    valid_result = bulk_upload_wimax_ss_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_wimax_ss_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                elif sheet_name == 'Backhaul':
                    valid_result = bulk_upload_backhaul_inventory.delay(gis_obj.id, organization, 'valid', 'auto')
                    invalid_result = bulk_upload_backhaul_inventory.delay(gis_obj.id, organization, 'invalid', 'auto')
                else:
                    valid_result = ""
                    invalid_result = ""
            except Exception as e:
                logger.info(e.message)


@task
def process_file_for_bulk_delete():
    """
    Background processing of inventories for bulk delete.
    """
    # Get inventories which are not processed yet.
    inventories = GISInventoryBulkImport.objects.filter(is_new=2)

    if inventories:
        for inventory in inventories:
            try:
                # Update data import status in GISInventoryBulkImport model.
                gis_obj = None
                sheet_name = ''
                try:
                    gis_obj = inventory
                    sheet_name = gis_obj.sheet_name
                except Exception as e:
                    logger.info(e.message)

                if sheet_name in ['PTP', 'PTP BH', 'PMP BS', 'PMP SM', 'Wimax BS', 'Wimax SS', 'Backhaul']:
                    valid_result = delete_gis_inventory.delay(gis_obj.id, 'valid', sheet_name, 'auto')
                    invalid_result = delete_gis_inventory.delay(gis_obj.id, 'invalid', sheet_name, 'auto')
                else:
                    valid_result = ""
                    invalid_result = ""
            except Exception as e:
                logger.info(e.message)
    else:
        return False


def create_device(device_payload):
    """ Create Device object

    Args:
        device_payload (dict):  {
                                    'city': u'Delhi(NewDelhi)',
                                    'description': 'BaseStationcreatedon28-Sep-2014at22: 55: 03.',
                                    'state': u'Delhi',
                                    'device_model': 2,
                                    'ip': u'10.75.158.219',
                                    'site': 1,
                                    'longitude': 77.253333333333,
                                    'device_name': u'10.75.158.219',
                                    'machine': '',
                                    'mac': u'00: 15: 67: d7: 88: 02',
                                    'device_type': 3,
                                    'address': u'A-88,
                                    EastOfKailash,
                                    Delhi',
                                    'latitude': 28.560277777778,
                                    'organization': <Organization: TCL>,
                                    'device_vendor': 2,
                                    'device_technology': 2
                                }

    Returns:
        device (class 'device.models.Device'): <Device: 10.75.158.219>

    """

    # dictionary containing device data
    device_payload = device_payload
    # initializing variables
    device_name, device_alias, machine, device_technology, device_vendor, device_model, device_type = [''] * 7
    site_instance, ip_address, mac_address, state, city, latitude, longitude, address, description = [''] * 9
    organization = ''
    parent_ip = ''
    parent_type = ''
    parent_port = ''

    # get device parameters
    if 'device_name' in device_payload.keys():
        device_name = device_payload['device_name'] if device_payload['device_name'] else ""
    if 'organization' in device_payload.keys():
        organization = device_payload['organization'] if device_payload['organization'] else ""
    if 'device_alias' in device_payload.keys():
        device_alias = device_payload['device_alias'] if device_payload['device_alias'] else ""
    else:
        if 'ip' in device_payload.keys():
            device_alias = device_payload['ip'] if device_payload['ip'] else ""
    if 'machine' in device_payload.keys():
        machine = device_payload['machine'] if device_payload['machine'] else ""
    if 'site' in device_payload.keys():
        site_instance = device_payload['site'] if device_payload['site'] else ""
    if 'device_technology' in device_payload.keys():
        device_technology = device_payload['device_technology'] if device_payload['device_technology'] else ""
    if 'device_vendor' in device_payload.keys():
        device_vendor = device_payload['device_vendor'] if device_payload['device_vendor'] else ""
    if 'device_model' in device_payload.keys():
        device_model = device_payload['device_model'] if device_payload['device_model'] else ""
    if 'device_type' in device_payload.keys():
        device_type = device_payload['device_type'] if device_payload['device_type'] else ""
    if 'ip' in device_payload.keys():
        ip_address = device_payload['ip'] if device_payload['ip'] else ""
    if 'mac' in device_payload.keys():
        mac_address = sanitize_mac_address(device_payload['mac']) if device_payload['mac'] else ""
    if 'state' in device_payload.keys():
        state = device_payload['state'] if device_payload['state'] else ""
    if 'city' in device_payload.keys():
        city = device_payload['city'] if device_payload['city'] else ""
    if 'latitude' in device_payload.keys():
        latitude = device_payload['latitude'] if device_payload['latitude'] else ""
    if 'longitude' in device_payload.keys():
        longitude = device_payload['longitude'] if device_payload['longitude'] else ""
    if 'address' in device_payload.keys():
        address = device_payload['address'] if device_payload['address'] else ""
    if 'description' in device_payload.keys():
        description = device_payload['description'] if device_payload['description'] else ""
    if 'parent_ip' in device_payload.keys():
        parent_ip = device_payload['parent_ip'] if device_payload['parent_ip'] else ""
    if 'parent_type' in device_payload.keys():
        parent_type = device_payload['parent_type'] if device_payload['parent_type'] else ""
    if 'parent_port' in device_payload.keys():
        parent_port = device_payload['parent_port'] if device_payload['parent_port'] else ""

    # lat long validator
    regex_lat_long = '^[-+]?\d*\.\d+|\d+'

    # update device if it exists in database
    if device_name:
        if device_name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING DEVICE -------------------------------
            try:
                # device object
                device = Device.objects.get(ip_address=ip_address)
                # device alias
                if device_alias:
                    try:
                        device.device_alias = device_alias
                    except Exception as e:
                        logger.info("Device Alias: ({} - {})".format(device_alias, e.message))
                # machine
                # if machine:
                #     try:
                #         device.machine = machine
                #     except Exception as e:
                #         logger.info("Machine: ({} - {})".format(machine, e.message))
                # site instance
                # if site_instance:
                #     try:
                #         device.site_instance = site_instance
                #     except Exception as e:
                #         logger.info("Site Instance: ({} - {})".format(site_instance, e.message))
                
                if parent_ip:
                    try:
                        device.parent = Device.objects.get(Q(ip_address=parent_ip), ~Q(id=device.id))
                    except Exception, e:
                        logger.info("Parent IP: ({})".format(e.message))

                if parent_type:
                    try:
                        device.parent_type = parent_type
                    except Exception, e:
                        logger.info("Parent Type: ({})".format(e.message))

                if parent_port:
                    try:
                        device.parent_port = parent_port
                    except Exception, e:
                        logger.info("Parent Port: ({})".format(e.message))

                try:
                    device.organization = organization
                except Exception as e:
                    logger.info("Organization: ({})".format(e.message))
                # device technology
                if device_technology:
                    try:
                        device.device_technology = device_technology
                    except Exception as e:
                        logger.info("Device Technology: ({} - {})".format(device_technology, e.message))
                # device vendor
                if device_vendor:
                    try:
                        device.device_vendor = device_vendor
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_vendor, e.message))
                # device model
                if device_model:
                    try:
                        device.device_model = device_model
                    except Exception as e:
                        logger.info("Device Model: ({} - {})".format(device_model, e.message))
                # device type
                if device_type:
                    try:
                        device.device_type = device_type
                    except Exception as e:
                        logger.info("Device Type: ({} - {})".format(device_type, e.message))
                # mac address
                if mac_address:
                    try:
                        device.mac_address = mac_address
                    except Exception as e:
                        logger.info("MAC Address: ({} - {})".format(mac_address, e.message))
                # netmask
                device.netmask = '255.255.255.0'
                # dhcp state
                device.dhcp_state = 'Disable'
                # host priority
                device.host_priority = 'Normal'
                # host state
                device.host_state = 'Enable'
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        device.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        device.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                try:
                    device.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        device_state = get_state(state=state)
                        if not device_state:
                            raise Exception("While Device Update: State Not Found")
                        device.state = device_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city = get_city(state=state, city_name=city)
                            if not device_city:
                                raise Exception("While Device Update: City Not Found")
                        else:
                            raise Exception("While Device Update: In City: State Not Found")
                        device.city = device_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        device.address = address
                    except Exception as e:
                        logger.info("Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        device.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # saving device
                device.save()
                return device
            except Exception as e:
                # ---------------------------- CREATING DEVICE -------------------------------
                # device object
                device = Device()
                # device name
                if device_name:
                    try:
                        device.device_name = device_name
                    except Exception as e:
                        logger.info("Device Name: ({} - {})".format(device_name, e.message))
                # device alias
                if device_alias:
                    try:
                        device.device_alias = device_alias
                    except Exception as e:
                        logger.info("Device Alias: ({} - {})".format(device_alias, e.message))

                if parent_ip:
                    try:
                        device.parent = Device.objects.get(ip_address=parent_ip)
                    except Exception, e:
                        logger.info("Parent IP: ({})".format(e.message))

                if parent_type:
                    try:
                        device.parent_type = parent_type
                    except Exception, e:
                        logger.info("Parent Type: ({})".format(e.message))

                if parent_port:
                    try:
                        device.parent_port = parent_port
                    except Exception, e:
                        logger.info("Parent Port: ({})".format(e.message))

                # machine
                if machine:
                    try:
                        device.machine = machine
                    except Exception as e:
                        logger.info("Machine: ({} - {})".format(machine, e.message))
                # site instance
                if site_instance:
                    try:
                        device.site_instance = site_instance
                    except Exception as e:
                        logger.info("Site Instance: ({} - {})".format(site_instance, e.message))
                # organization
                try:
                    device.organization = organization
                except Exception as e:
                    logger.info("Organization: ({})".format(e.message))
                # device technology
                if device_technology:
                    try:
                        device.device_technology = device_technology
                    except Exception as e:
                        logger.info("Device Technology: ({} - {})".format(device_technology, e.message))
                # device vendor
                if device_vendor:
                    try:
                        device.device_vendor = device_vendor
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_vendor, e.message))
                # device model
                if device_model:
                    try:
                        device.device_model = device_model
                    except Exception as e:
                        logger.info("Device Vendor: ({} - {})".format(device_model, e.message))
                # device type
                if device_type:
                    try:
                        device.device_type = device_type
                    except Exception as e:
                        logger.info("Device Type: ({} - {})".format(device_type, e.message))
                # ip address
                if ip_address:
                    try:
                        device.ip_address = ip_address
                    except Exception as e:
                        logger.info("IP Address: ({} - {})".format(ip_address, e.message))
                # mac address
                if mac_address:
                    try:
                        device.mac_address = mac_address
                    except Exception as e:
                        logger.info("MAC Address: ({} - {})".format(mac_address, e.message))
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        device.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        device.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                try:
                    device.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        device_state = get_state(state=state)
                        if not device_state:
                            raise Exception("While Device Update: State Not Found")
                        device.state = device_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city = get_city(state=state, city_name=city)
                            if not device_city:
                                raise Exception("While Device Update: City Not Found")
                        else:
                            raise Exception("While Device Update: In City: State Not Found")
                        device.city = device_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        device.address = address
                    except Exception as e:
                        logger.info("Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        device.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # is deleted
                device.is_deleted = 0
                # is added to nms
                device.is_added_to_nms = 0
                # is monitored on nms
                device.is_monitored_on_nms = 0
                # saving device
                try:
                    device.save()
                    return device
                except Exception as e:
                    logger.info("Device Object: ({} - {})".format(device_name, e.message))
                    return ""


def create_antenna(antenna_payload):
    """ Create Antenna object

    Args:
        antenna_payload (dict): {
                                    'description': 'SectorAntennacreatedon28-Sep-2014at22: 55: 03.',
                                    'mount_type': u'NA',
                                    'ip': u'10.75.158.219',
                                    'height': 28.0,
                                    'polarization': u'vertical',
                                    'gain': u'NA',
                                    'antenna_type': u'NA'
                               }

    Returns:
        antenna (class 'inventory.models.Antenna'): <Antenna: 10.75.158.219>

    """

    # dictionary containing antenna payload
    antenna_payload = antenna_payload

    # initializing variables
    name, alias, antenna_type, height, tilt, gain, mount_type, beam_width, azimuth_angle, reflector = [''] * 10
    splitter_installed, sync_splitter_used, make_of_antenna, polarization, description = [''] * 5

    # get antenna parameters
    if 'antenna_name' in antenna_payload.keys():
        name = antenna_payload['antenna_name']
    else:
        name = antenna_payload['ip'] if antenna_payload['ip'] else ""
    if 'antenna_alias' in antenna_payload.keys():
        alias = antenna_payload['antenna_alias']
    else:
        alias = antenna_payload['ip'] if antenna_payload['ip'] else ""
    if 'antenna_type' in antenna_payload.keys():
        antenna_type = antenna_payload['antenna_type'] if antenna_payload['antenna_type'] else ""
    if 'height' in antenna_payload.keys():
        height = antenna_payload['height'] if antenna_payload['height'] else ""
    if 'tilt' in antenna_payload.keys():
        tilt = antenna_payload['tilt'] if antenna_payload['tilt'] else ""
    if 'gain' in antenna_payload.keys():
        gain = antenna_payload['gain'] if antenna_payload['gain'] else ""
    if 'mount_type' in antenna_payload.keys():
        mount_type = antenna_payload['mount_type'] if antenna_payload['mount_type'] else ""
    if 'beam_width' in antenna_payload.keys():
        beam_width = antenna_payload['beam_width'] if antenna_payload['beam_width'] else ""
    if 'azimuth_angle' in antenna_payload.keys():
        azimuth_angle = antenna_payload['azimuth_angle'] if antenna_payload['azimuth_angle'] else ""
    if 'reflector' in antenna_payload.keys():
        reflector = antenna_payload['reflector'] if antenna_payload['reflector'] else ""
    if 'splitter_installed' in antenna_payload.keys():
        splitter_installed = antenna_payload['splitter_installed'] if antenna_payload['splitter_installed'] else ""
    if 'sync_splitter_used' in antenna_payload.keys():
        sync_splitter_used = antenna_payload['sync_splitter_used'] if antenna_payload['sync_splitter_used'] else ""
    if 'make_of_antenna' in antenna_payload.keys():
        make_of_antenna = antenna_payload['make_of_antenna'] if antenna_payload['make_of_antenna'] else ""
    if 'polarization' in antenna_payload.keys():
        polarization = antenna_payload['polarization'] if antenna_payload['polarization'] else ""
    if 'description' in antenna_payload.keys():
        description = antenna_payload['description'] if antenna_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ------------------------------ UPDATING ANTENNA -------------------------------
            try:
                # update antenna if it exists in database
                antenna = Antenna.objects.get(name=name)
                # alias
                if alias:
                    try:
                        antenna.alias = alias
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # antenna type
                if antenna_type:
                    try:
                        antenna.antenna_type = antenna_type
                    except Exception as e:
                        logger.info("Antenna Type: ({} - {})".format(antenna_type, e.message))
                # height
                if height:
                    if isinstance(height, int) or isinstance(height, float):
                        try:
                            antenna.height = height
                        except Exception as e:
                            logger.info("Antenna Height: ({} - {})".format(height, e.message))
                # tilt
                if tilt:
                    if isinstance(tilt, int) or isinstance(tilt, float):
                        try:
                            antenna.tilt = tilt
                        except Exception as e:
                            logger.info("Antenna Tilt: ({} - {})".format(tilt, e.message))
                # gain
                if gain:
                    if isinstance(gain, int) or isinstance(gain, float):
                        try:
                            antenna.gain = gain
                        except Exception as e:
                            logger.info("Antenna Gain: ({} - {})".format(gain, e.message))
                # mount type
                if mount_type:
                    try:
                        antenna.mount_type = mount_type
                    except Exception as e:
                        logger.info("Antenna Mount Type: ({} - {})".format(mount_type, e.message))
                # beam width
                if beam_width:
                    if isinstance(beam_width, int) or isinstance(beam_width, float):
                        try:
                            antenna.beam_width = beam_width
                        except Exception as e:
                            logger.info("Antenna Beamwidth: ({} - {})".format(beam_width, e.message))
                # azimuth angle
                if azimuth_angle:
                    if isinstance(azimuth_angle, int) or isinstance(azimuth_angle, float):
                        try:
                            antenna.azimuth_angle = azimuth_angle
                        except Exception as e:
                            logger.info("Azimuth Angle: ({} - {})".format(azimuth_angle, e.message))
                    else:
                        antenna.azimuth_angle = 0
                # reflector
                if reflector:
                    try:
                        antenna.reflector = reflector
                    except Exception as e:
                        logger.info("Antenna Reflector: ({} - {})".format(reflector, e.message))
                # splitter installed
                if splitter_installed:
                    try:
                        antenna.splitter_installed = splitter_installed
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # sync splitter installed
                if sync_splitter_used:
                    try:
                        antenna.sync_splitter_used = sync_splitter_used
                    except Exception as e:
                        logger.info("Antenna Sync Splitter Used: ({} - {})".format(sync_splitter_used, e.message))
                # make of antenna
                if make_of_antenna:
                    try:
                        antenna.make_of_antenna = make_of_antenna
                    except Exception as e:
                        logger.info("Make Of Antenna: ({} - {})".format(make_of_antenna, e.message))
                # polarization
                if polarization:
                    try:
                        antenna.polarization = polarization
                    except Exception as e:
                        logger.info("Antenna Polarization: ({} - {})".format(make_of_antenna, e.message))
                # description
                if description:
                    try:
                        antenna.description = description
                    except Exception as e:
                        logger.info("Antenna Description: ({} - {})".format(description, e.message))
                # saving antenna
                antenna.save()
                return antenna
            except Exception as e:
                # ---------------------------- CREATING ANTENNA -------------------------------
                # create antenna if it doesn't exist in database
                antenna = Antenna()
                # name
                antenna.name = name
                # alias
                if alias:
                    try:
                        antenna.alias = alias
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # antenna type
                if antenna_type:
                    try:
                        antenna.antenna_type = antenna_type
                    except Exception as e:
                        logger.info("Antenna Type: ({} - {})".format(antenna_type, e.message))
                # height
                if height:
                    if isinstance(height, int) or isinstance(height, float):
                        try:
                            antenna.height = height
                        except Exception as e:
                            logger.info("Antenna Height: ({} - {})".format(height, e.message))
                # tilt
                if tilt:
                    if isinstance(tilt, int) or isinstance(tilt, float):
                        try:
                            antenna.tilt = tilt
                        except Exception as e:
                            logger.info("Antenna Tilt: ({} - {})".format(tilt, e.message))
                # gain
                if gain:
                    if isinstance(gain, int) or isinstance(gain, float):
                        try:
                            antenna.gain = gain
                        except Exception as e:
                            logger.info("Antenna Gain: ({} - {})".format(gain, e.message))
                # mount type
                if mount_type:
                    try:
                        antenna.mount_type = mount_type
                    except Exception as e:
                        logger.info("Antenna Mount Type: ({} - {})".format(mount_type, e.message))
                # beam width
                if beam_width:
                    if isinstance(beam_width, int) or isinstance(beam_width, float):
                        try:
                            antenna.beam_width = beam_width
                        except Exception as e:
                            logger.info("Antenna Beamwidth: ({} - {})".format(beam_width, e.message))
                # azimuth angle
                if azimuth_angle:
                    if isinstance(azimuth_angle, int) or isinstance(azimuth_angle, float):
                        try:
                            antenna.azimuth_angle = azimuth_angle
                        except Exception as e:
                            logger.info("Azimuth Angle: ({} - {})".format(azimuth_angle, e.message))
                    else:
                        antenna.azimuth_angle = 0
                else:
                    antenna.azimuth_angle = 0
                # reflector
                if reflector:
                    try:
                        antenna.reflector = reflector
                    except Exception as e:
                        logger.info("Antenna Reflector: ({} - {})".format(reflector, e.message))
                # splitter installed
                if splitter_installed:
                    try:
                        antenna.splitter_installed = splitter_installed
                    except Exception as e:
                        logger.info("Antenna Alias: ({} - {})".format(alias, e.message))
                # sync splitter installed
                if sync_splitter_used:
                    try:
                        antenna.sync_splitter_used = sync_splitter_used
                    except Exception as e:
                        logger.info("Antenna Sync Splitter Used: ({} - {})".format(sync_splitter_used, e.message))
                # make of antenna
                if make_of_antenna:
                    try:
                        antenna.make_of_antenna = make_of_antenna
                    except Exception as e:
                        logger.info("Make Of Antenna: ({} - {})".format(make_of_antenna, e.message))
                # polarization
                if polarization:
                    try:
                        antenna.polarization = polarization
                    except Exception as e:
                        logger.info("Antenna Polarization: ({} - {})".format(make_of_antenna, e.message))
                # description
                if description:
                    try:
                        antenna.description = description
                    except Exception as e:
                        logger.info("Antenna Description: ({} - {})".format(description, e.message))
                try:
                    antenna.save()
                    return antenna
                except Exception as e:
                    logger.info("Antenna Object: ({} - {})".format(name, e.message))
                    return ""


def create_backhaul(backhaul_payload):
    """ Create Backhaul object

    Args:
        backhaul_payload (dict): {
                                    'bh_configured_on': <Device: 10.175.16.199>,
                                    'description': 'Backhaulcreatedon28-Sep-2014at22: 55: 03.',
                                    'bh_connectivity': u'Onnet',
                                    'bh_circuit_id': u'IOR_166748',
                                    'pe_hostname': u'dl-con-kcl-mi07-rt01',
                                    'ip': u'10.175.16.199',
                                    'bh_type': u'Ethernet',
                                    'bh_switch': None,
                                    'pop': None,
                                    'bh_port': 0,
                                    'aggregator_port': 0,
                                    'bh_capacity': 100.0,
                                    'aggregator_port_name': u'NA',
                                    'ttsl_circuit_id': '',
                                    'pe_ip': u'192.168.192.43',
                                    'aggregator': None,
                                    'bh_port_name': u'Fa0/25'
                                }

    Returns:
        backhaul (class 'inventory.models.Backhaul'): <Backhaul: 10.75.158.219>

    """

    # dictionary containing backhaul payload
    backhaul_payload = backhaul_payload

    # initializing variables
    name, alias, bh_configured_on, bh_port_name, bh_port, bh_type, bh_switch, switch_port_name, switch_port = [''] * 9
    pop, pop_port_name, pop_port, aggregator, aggregator_port_name, aggregator_port, pe_hostname, pe_ip = [''] * 8
    dr_site, bh_connectivity, bh_circuit_id, ttsl_circuit_id, description, bh_capacity, ior_id, bh_provider = [''] * 8

    # get backhaul parameters
    if 'ip' in backhaul_payload.keys():
        name = backhaul_payload['ip'] if backhaul_payload['ip'] else ""
        alias = backhaul_payload['ip'] if backhaul_payload['ip'] else ""
    if 'bh_configured_on' in backhaul_payload.keys():
        bh_configured_on = backhaul_payload['bh_configured_on'] if backhaul_payload['bh_configured_on'] else ""
    if 'bh_port_name' in backhaul_payload.keys():
        bh_port_name = backhaul_payload['bh_port_name'] if backhaul_payload['bh_port_name'] else ""
    if 'bh_port' in backhaul_payload.keys():
        bh_port = backhaul_payload['bh_port'] if backhaul_payload['bh_port'] else ""
    if 'bh_type' in backhaul_payload.keys():
        bh_type = backhaul_payload['bh_type'] if backhaul_payload['bh_type'] else ""
    if 'bh_switch' in backhaul_payload.keys():
        bh_switch = backhaul_payload['bh_switch'] if backhaul_payload['bh_switch'] else ""
    if 'switch_port_name' in backhaul_payload.keys():
        switch_port_name = backhaul_payload['switch_port_name'] if backhaul_payload['switch_port_name'] else ""
    if 'switch_port' in backhaul_payload.keys():
        switch_port = backhaul_payload['switch_port'] if backhaul_payload['switch_port'] else ""
    if 'pop' in backhaul_payload.keys():
        pop = backhaul_payload['pop'] if backhaul_payload['pop'] else ""
    if 'pop_port_name' in backhaul_payload.keys():
        pop_port_name = backhaul_payload['pop_port_name'] if backhaul_payload['pop_port_name'] else ""
    if 'pop_port' in backhaul_payload.keys():
        pop_port = backhaul_payload['pop_port'] if backhaul_payload['pop_port'] else ""
    if 'aggregator' in backhaul_payload.keys():
        aggregator = backhaul_payload['aggregator'] if backhaul_payload['aggregator'] else ""
    if 'aggregator_port_name' in backhaul_payload.keys():
        aggregator_port_name = backhaul_payload['aggregator_port_name'] if backhaul_payload['aggregator_port_name'] else ""
    if 'aggregator_port' in backhaul_payload.keys():
        aggregator_port = backhaul_payload['aggregator_port'] if backhaul_payload['aggregator_port'] else ""
    if 'pe_hostname' in backhaul_payload.keys():
        pe_hostname = backhaul_payload['pe_hostname'] if backhaul_payload['pe_hostname'] else ""
    if 'pe_ip' in backhaul_payload.keys():
        pe_ip = backhaul_payload['pe_ip'] if backhaul_payload['pe_ip'] else ""
    if 'dr_site' in backhaul_payload.keys():
        dr_site = backhaul_payload['dr_site'].lower() if backhaul_payload['dr_site'] else ""
    if 'bh_connectivity' in backhaul_payload.keys():
        bh_connectivity = backhaul_payload['bh_connectivity'] if backhaul_payload['bh_connectivity'] else ""
    if 'bh_circuit_id' in backhaul_payload.keys():
        bh_circuit_id = backhaul_payload['bh_circuit_id'] if backhaul_payload['bh_circuit_id'] else ""
    if 'bh_capacity' in backhaul_payload.keys():
        bh_capacity = backhaul_payload['bh_capacity'] if backhaul_payload['bh_capacity'] else ""
    if 'ttsl_circuit_id' in backhaul_payload.keys():
        ttsl_circuit_id = backhaul_payload['ttsl_circuit_id'] if backhaul_payload['ttsl_circuit_id'] else ""
    if 'description' in backhaul_payload.keys():
        description = backhaul_payload['description'] if backhaul_payload['description'] else ""
    if 'ior_id' in backhaul_payload.keys():
        ior_id = backhaul_payload['ior_id'] if backhaul_payload['ior_id'] else ""
    if 'bh_provider' in backhaul_payload.keys():
        bh_provider = backhaul_payload['bh_provider'] if backhaul_payload['bh_provider'] else ""
    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ------------------------------ UPDATING BACKHAUL -------------------------------
            try:
                # update backhaul if it exists in database
                backhaul = Backhaul.objects.get(name=name)
                # alias
                if alias:
                    try:
                        backhaul.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bh configured on
                if bh_configured_on:
                    try:
                        backhaul.bh_configured_on = bh_configured_on
                    except Exception as e:
                        logger.info("BH Configured On: ({} - {})".format(bh_configured_on, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        backhaul.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if bh_port:
                    try:
                        backhaul.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh type
                if bh_type:
                    try:
                        backhaul.bh_type = bh_type
                    except Exception as e:
                        logger.info("BH Type: ({} - {})".format(bh_type, e.message))
                # bh switch
                if bh_switch:
                    try:
                        backhaul.bh_switch = bh_switch
                    except Exception as e:
                        logger.info("BH Switch: ({} - {})".format(bh_switch, e.message))
                # switch port name
                if switch_port_name:
                    try:
                        backhaul.switch_port_name = switch_port_name
                    except Exception as e:
                        logger.info("Switch Port Name: ({} - {})".format(switch_port_name, e.message))
                # switch port
                if switch_port:
                    try:
                        backhaul.switch_port = switch_port
                    except Exception as e:
                        logger.info("Switch Port: ({} - {})".format(switch_port, e.message))
                # pop
                if pop:
                    try:
                        backhaul.pop = pop
                    except Exception as e:
                        logger.info("POP: ({} - {})".format(pop, e.message))
                # pop port name
                if pop_port_name:
                    try:
                        backhaul.pop_port_name = pop_port_name
                    except Exception as e:
                        logger.info("POP Port Name: ({} - {})".format(pop_port_name, e.message))
                # pop_port
                if pop_port:
                    try:
                        backhaul.pop_port = pop_port
                    except Exception as e:
                        logger.info("POP Port: ({} - {})".format(pop_port, e.message))
                # aggregator
                if aggregator:
                    try:
                        backhaul.aggregator = aggregator
                    except Exception as e:
                        logger.info("Aggregator: ({} - {})".format(aggregator, e.message))
                # aggregator port name
                if aggregator_port_name:
                    try:
                        backhaul.aggregator_port_name = aggregator_port_name
                    except Exception as e:
                        logger.info("Aggregator Port Name: ({} - {})".format(aggregator_port_name, e.message))
                # aggregator port
                if aggregator_port:
                    try:
                        backhaul.aggregator_port = aggregator_port
                    except Exception as e:
                        logger.info("Aggregator Port: ({} - {})".format(aggregator_port, e.message))
                # pe hostname
                if pe_hostname:
                    try:
                        backhaul.pe_hostname = pe_hostname
                    except Exception as e:
                        logger.info("PE Hostname: ({} - {})".format(pe_hostname, e.message))
                # pe ip
                if pe_ip:
                    try:
                        backhaul.pe_ip = pe_ip
                    except Exception as e:
                        logger.info("PE IP: ({} - {})".format(pe_ip, e.message))
                # dr site
                if dr_site:
                    try:
                        if dr_site == "yes":
                            backhaul.dr_site = "Yes"
                        elif dr_site == "no":
                            backhaul.dr_site = "No"
                        else:
                            backhaul.dr_site = ""
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # bh connectivity
                if bh_connectivity:
                    try:
                        backhaul.bh_connectivity = bh_connectivity
                    except Exception as e:
                        logger.info("BH Connectivity: ({} - {})".format(bh_connectivity, e.message))
                # bh circuit id
                if bh_circuit_id:
                    try:
                        backhaul.bh_circuit_id = bh_circuit_id
                    except Exception as e:
                        logger.info("BH Circuit ID: ({} - {})".format(bh_circuit_id, e.message))
                # bh capacity
                if bh_capacity:
                    try:
                        backhaul.bh_capacity = int(bh_capacity)
                    except Exception as e:
                        logger.info("BH Capacity: ({} - {})".format(bh_capacity, e.message))
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit ID: ({} - {})".format(ttsl_circuit_id, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # ior id
                if ior_id:
                    try:
                        backhaul.ior_id = ior_id
                    except Exception as e:
                        logger.info("IOR ID: ({} - {})".format(ior_id, e.message))
                # bh_provider
                if bh_provider:
                    try:
                        backhaul.bh_provider = bh_provider
                    except Exception as e:
                        logger.info("BH Provider: ({} - {})".format(bh_provider, e.message))
                # saving backhaul
                backhaul.save()
                return backhaul
            except Exception as e:
                # ---------------------------- CREATING BACKHAUL -------------------------------
                # create backhaul if it doesn't exist in database
                backhaul = Backhaul()
                # name
                if name:
                    try:
                        backhaul.name = name
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # alias
                if alias:
                    try:
                        backhaul.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bh configured on
                if bh_configured_on:
                    try:
                        backhaul.bh_configured_on = bh_configured_on
                    except Exception as e:
                        logger.info("BH Configured On: ({} - {})".format(bh_configured_on, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        backhaul.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if bh_port:
                    try:
                        backhaul.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh type
                if bh_type:
                    try:
                        backhaul.bh_type = bh_type
                    except Exception as e:
                        logger.info("BH Type: ({} - {})".format(bh_type, e.message))
                # bh switch
                if bh_switch:
                    try:
                        backhaul.bh_switch = bh_switch
                    except Exception as e:
                        logger.info("BH Switch: ({} - {})".format(bh_switch, e.message))
                # switch port name
                if switch_port_name:
                    try:
                        backhaul.switch_port_name = switch_port_name
                    except Exception as e:
                        logger.info("Switch Port Name: ({} - {})".format(switch_port_name, e.message))
                # switch port
                if switch_port:
                    try:
                        backhaul.switch_port = switch_port
                    except Exception as e:
                        logger.info("Switch Port: ({} - {})".format(switch_port, e.message))
                # pop
                if pop:
                    try:
                        backhaul.pop = pop
                    except Exception as e:
                        logger.info("POP: ({} - {})".format(pop, e.message))
                # pop port name
                if pop_port_name:
                    try:
                        backhaul.pop_port_name = pop_port_name
                    except Exception as e:
                        logger.info("POP Port Name: ({} - {})".format(pop_port_name, e.message))
                # pop_port
                if pop_port:
                    try:
                        backhaul.pop_port = pop_port
                    except Exception as e:
                        logger.info("POP Port: ({} - {})".format(pop_port, e.message))
                # aggregator
                if aggregator:
                    try:
                        backhaul.aggregator = aggregator
                    except Exception as e:
                        logger.info("Aggregator: ({} - {})".format(aggregator, e.message))
                # aggregator port name
                if aggregator_port_name:
                    try:
                        backhaul.aggregator_port_name = aggregator_port_name
                    except Exception as e:
                        logger.info("Aggregator Port Name: ({} - {})".format(aggregator_port_name, e.message))
                # aggregator port
                if aggregator_port:
                    try:
                        backhaul.aggregator_port = aggregator_port
                    except Exception as e:
                        logger.info("Aggregator Port: ({} - {})".format(aggregator_port, e.message))
                # dr site
                if dr_site:
                    try:
                        if dr_site == "yes":
                            backhaul.dr_site = "Yes"
                        elif dr_site == "no":
                            backhaul.dr_site = "No"
                        else:
                            backhaul.dr_site = ""
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # pe hostname
                if pe_hostname:
                    try:
                        backhaul.pe_hostname = pe_hostname
                    except Exception as e:
                        logger.info("PE Hostname: ({} - {})".format(pe_hostname, e.message))
                # pe ip
                if pe_ip:
                    try:
                        backhaul.pe_ip = pe_ip
                    except Exception as e:
                        logger.info("PE IP: ({} - {})".format(pe_ip, e.message))
                # bh connectivity
                if bh_connectivity:
                    try:
                        backhaul.bh_connectivity = bh_connectivity
                    except Exception as e:
                        logger.info("BH Connectivity: ({} - {})".format(bh_connectivity, e.message))
                # bh circuit id
                if bh_circuit_id:
                    try:
                        backhaul.bh_circuit_id = bh_circuit_id
                    except Exception as e:
                        logger.info("BH Circuit ID: ({} - {})".format(bh_circuit_id, e.message))
                # bh capacity
                if bh_capacity:
                    try:
                        backhaul.bh_capacity = int(bh_capacity)
                    except Exception as e:
                        logger.info("BH Capacity: ({} - {})".format(bh_capacity, e.message))
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit IB: ({} - {})".format(ttsl_circuit_id, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
                # ior id
                if ior_id:
                    try:
                        backhaul.ior_id = ior_id
                    except Exception as e:
                        logger.info("IOR ID: ({} - {})".format(ior_id, e.message))
                # bh_provider
                if bh_provider:
                    try:
                        backhaul.bh_provider = bh_provider
                    except Exception as e:
                        logger.info("BH Provider: ({} - {})".format(bh_provider, e.message))
                try:
                    backhaul.save()
                    return backhaul
                except Exception as e:
                    logger.info("Backhaul Object: ({} - {})".format(name, e.message))
                    return ""


def create_basestation(basestation_payload):
    """ Create BaseStation object

    Args:
        basestation_payload (dict): {
                                        'tower_height': 14.0,
                                        'description': 'BaseStationcreatedon28-Sep-2014at22: 55: 03.',
                                        'building_height': 14.0,
                                        'address': u'A-88,
                                        EastOfKailash,
                                        Delhi',
                                        'hssu_used': '',
                                        'bs_switch': <Device: 10.175.16.199>,
                                        'bh_bso': u'RadwinwithWimax',
                                        'city': u'Delhi(NewDelhi)',
                                        'name': 'east_of_kailash_dr',
                                        'longitude': 77.253333333333,
                                        'alias': u'EastOfKailash-DR',
                                        'state': u'Delhi',
                                        'backhaul': <Backhaul: 10.175.16.199>,
                                        'latitude': 28.560277777778
                                    }

    Returns:
        basestation (class 'inventory.models.BaseStation'): <BaseStation: 10.75.158.219>

    """

    # dictionary containing base station payload
    basestation_payload = basestation_payload

    # initializing variables
    name, alias, bs_site_id, bs_site_type, bs_switch, backhaul, bs_type, bh_bso, hssu_used, hssu_port = [''] * 10
    latitude, longitude, infra_provider, gps_type, building_height, tower_height, country, state, city = [''] * 9
    bh_port_name, bh_port, bh_capacity, address, description, site_ams, site_infra_type, site_sap_id, mgmt_vlan = [''] * 9

    # get base station parameters
    if 'name' in basestation_payload.keys():
        name = basestation_payload['name'] if basestation_payload['name'] else ""
    if 'alias' in basestation_payload.keys():
        alias = basestation_payload['alias'] if basestation_payload['alias'] else ""
    if 'organization' in basestation_payload.keys():
        organization = basestation_payload['organization'] if basestation_payload['organization'] else ""
    if 'bs_site_id' in basestation_payload.keys():
        bs_site_id = basestation_payload['bs_site_id'] if basestation_payload['bs_site_id'] else ""
    if 'bs_site_type' in basestation_payload.keys():
        bs_site_type = basestation_payload['bs_site_type'] if basestation_payload['bs_site_type'] else ""
    if 'bs_switch' in basestation_payload.keys():
        bs_switch = basestation_payload['bs_switch'] if basestation_payload['bs_switch'] else ""
    if 'backhaul' in basestation_payload.keys():
        backhaul = basestation_payload['backhaul'] if basestation_payload['backhaul'] else ""
    if 'bh_port_name' in basestation_payload.keys():
        bh_port_name = basestation_payload['bh_port_name'] if basestation_payload['bh_port_name'] else ""
    if 'bh_port' in basestation_payload.keys():
        bh_port = basestation_payload['bh_port'] if isinstance(basestation_payload['bh_port'], (int, float)) else ""
    if 'bh_capacity' in basestation_payload.keys():
        bh_capacity = basestation_payload['bh_capacity'] if isinstance(basestation_payload['bh_capacity'], (int, float)) else ""
    if 'bs_type' in basestation_payload.keys():
        bs_type = basestation_payload['bs_type'] if basestation_payload['bs_type'] else ""
    if 'bh_bso' in basestation_payload.keys():
        bh_bso = basestation_payload['bh_bso'] if basestation_payload['bh_bso'] else ""
    if 'hssu_used' in basestation_payload.keys():
        hssu_used = basestation_payload['hssu_used'] if basestation_payload['hssu_used'] else ""
    if 'hssu_port' in basestation_payload.keys():
        hssu_port = basestation_payload['hssu_port'] if basestation_payload['hssu_port'] else ""
    if 'switch_port' in basestation_payload.keys():
        switch_port = basestation_payload['switch_port'] if isinstance(basestation_payload['switch_port'], (int, float)) else ""
    if 'latitude' in basestation_payload.keys():
        latitude = basestation_payload['latitude'] if basestation_payload['latitude'] else ""
    if 'longitude' in basestation_payload.keys():
        longitude = basestation_payload['longitude'] if basestation_payload['longitude'] else ""
    if 'pop_port' in basestation_payload.keys():
        pop_port = basestation_payload['pop_port'] if isinstance(basestation_payload['pop_port'], (int, float)) else ""
    if 'infra_provider' in basestation_payload.keys():
        infra_provider = basestation_payload['infra_provider'] if basestation_payload['infra_provider'] else ""
    if 'gps_type' in basestation_payload.keys():
        gps_type = basestation_payload['gps_type'] if basestation_payload['gps_type'] else ""
    if 'building_height' in basestation_payload.keys():
        building_height = basestation_payload['building_height'] if isinstance(basestation_payload['building_height'], (int, float)) else ""
    if 'tower_height' in basestation_payload.keys():
        tower_height = basestation_payload['tower_height'] if isinstance(basestation_payload['tower_height'], (int, float)) else ""
    if 'country' in basestation_payload.keys():
        country = basestation_payload['country'] if basestation_payload['country'] else ""
    if 'state' in basestation_payload.keys():
        state = basestation_payload['state'] if basestation_payload['state'] else ""
    if 'city' in basestation_payload.keys():
        city = basestation_payload['city'] if basestation_payload['city'] else ""
    if 'address' in basestation_payload.keys():
        address = basestation_payload['address'] if basestation_payload['address'] else ""
    if 'description' in basestation_payload.keys():
        description = basestation_payload['description'] if basestation_payload['description'] else ""

    # lat long validator
    regex_lat_long = '^[-+]?\d*\.\d+|\d+'

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING BASE STATION -----------------------------
            try:
                # update basestation if it exists in database
                basestation = BaseStation.objects.get(name=name)
                # alias
                if alias:
                    try:
                        basestation.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))
                # bs site id
                if bs_site_id:
                    try:
                        if isinstance(bs_site_id, float):
                            basestation.bs_site_id = int(bs_site_id)
                        else:
                            basestation.bs_site_id = bs_site_id
                    except Exception as e:
                        logger.info("BS Site ID: ({} - {})".format(bs_site_id, e.message))
                
                # Organization
                if organization:
                    basestation.organization = organization

                # bs site type
                if bs_site_type:
                    try:
                        basestation.bs_site_type = bs_site_type
                    except Exception as e:
                        logger.info("BS Site Type: ({} - {})".format(bs_site_type, e.message))
                # bs switch
                if bs_switch:
                    try:
                        basestation.bs_switch = bs_switch
                    except Exception as e:
                        logger.info("BS Switch: ({} - {})".format(bs_switch, e.message))
                # backhaul
                if backhaul:
                    try:
                        basestation.backhaul = backhaul
                    except Exception as e:
                        logger.info("Backhaul: ({} - {})".format(backhaul, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        basestation.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if isinstance(bh_port, (int, float)):
                    try:
                        basestation.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh capacity
                if bh_capacity:
                    try:
                        basestation.bh_capacity = int(bh_capacity)
                    except Exception as e:
                        logger.info("BH Capacity: ({} - {})".format(bh_capacity, e.message))
                # bs type
                if bs_type:
                    try:
                        basestation.bs_type = bs_type
                    except Exception as e:
                        logger.info("BS Type: ({} - {})".format(bs_type, e.message))
                # bh bso
                if bh_bso:
                    try:
                        basestation.bh_bso = bh_bso
                    except Exception as e:
                        logger.info("BH BSO: ({} - {})".format(bh_bso, e.message))
                # hssu used
                if hssu_used:
                    try:
                        basestation.hssu_used = hssu_used
                    except Exception as e:
                        logger.info("HSSU Used: ({} - {})".format(hssu_used, e.message))
                # hssu port
                if hssu_port:
                    try:
                        basestation.hssu_port = hssu_port
                    except Exception as e:
                        logger.info("HSSU Port: ({} - {})".format(hssu_port, e.message))
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        basestation.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        basestation.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # infra provider
                if infra_provider:
                    try:
                        basestation.infra_provider = infra_provider
                    except Exception as e:
                        logger.info("Infra Provider: ({} - {})".format(infra_provider, e.message))
                # gps type
                if gps_type:
                    try:
                        basestation.gps_type = gps_type
                    except Exception as e:
                        logger.info("GPS Type: ({} - {})".format(gps_type, e.message))
                # building height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            basestation.building_height = building_height
                        except Exception as e:
                            logger.info("Building Height: ({} - {})".format(building_height, e.message))
                    if isinstance(building_height, basestring):
                        try:
                            basestation.building_height = Decimal(building_height)
                        except Exception as e:
                            logger.info("Building Height: ({} - {})".format(building_height, e.message))
                # tower height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            basestation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                    if isinstance(tower_height, basestring):
                        try:
                            basestation.tower_height = Decimal(tower_height)
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                try:
                    basestation.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        basestation_state = get_state(state=state)
                        if not basestation_state:
                            raise Exception("While Basestation Update: State Not Found")
                        basestation.state = basestation_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            basestation_city = get_city(state=state, city_name=city)
                            if not basestation_city:
                                raise Exception("While Basestation Update: City Not Found")
                        else:
                            raise Exception("While Basestation Update: In City: State Not Found")
                        basestation.city = basestation_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # maintenance status
                basestation.maintenance_status = "No"
                # provisioning status
                basestation.provisioning_status = "Normal"
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
                # site ams
                if site_ams:
                    try:
                        basestation.site_ams = site_ams
                    except Exception as e:
                        logger.info("Site AMS: ({} - {})".format(site_ams, e.message))
                # site infra type
                if site_infra_type:
                    try:
                        basestation.site_infra_type = site_infra_type
                    except Exception as e:
                        logger.info("Site Infra Type: ({} - {})".format(site_infra_type, e.message))
                # site sap id
                if site_sap_id:
                    try:
                        basestation.site_sap_id = site_sap_id
                    except Exception as e:
                        logger.info("Site SAP Type: ({} - {})".format(site_sap_id, e.message))
                # mgmt vlan
                if mgmt_vlan:
                    try:
                        basestation.mgmt_vlan = mgmt_vlan
                    except Exception as e:
                        logger.info("MGMT VLAN: ({} - {})".format(mgmt_vlan, e.message))
                # saving base station
                basestation.save()
                return basestation
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create basestation if it doesn't exist in database
                basestation = BaseStation()
                # name
                if name:
                    try:
                        basestation.name = name
                    except Exception as e:
                        logger.info("BH Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        basestation.alias = alias
                    except Exception as e:
                        logger.info("BH Alias: ({} - {})".format(alias, e.message))

                # Organization
                if organization:
                    basestation.organization = organization
                    
                # bs site id
                if bs_site_id:
                    try:
                        basestation.bs_site_id = bs_site_id
                    except Exception as e:
                        logger.info("BS Site ID: ({} - {})".format(bs_site_id, e.message))
                # bs site type
                if bs_site_type:
                    try:
                        basestation.bs_site_type = bs_site_type
                    except Exception as e:
                        logger.info("BS Site Type: ({} - {})".format(bs_site_type, e.message))
                # bs switch
                if bs_switch:
                    try:
                        basestation.bs_switch = bs_switch
                    except Exception as e:
                        logger.info("BS Switch: ({} - {})".format(bs_switch, e.message))
                # backhaul
                if backhaul:
                    try:
                        basestation.backhaul = backhaul
                    except Exception as e:
                        logger.info("Backhaul: ({} - {})".format(backhaul, e.message))
                # bh port name
                if bh_port_name:
                    try:
                        basestation.bh_port_name = bh_port_name
                    except Exception as e:
                        logger.info("BH Port Name: ({} - {})".format(bh_port_name, e.message))
                # bh port
                if isinstance(bh_port, (int, float)):
                    try:
                        basestation.bh_port = bh_port
                    except Exception as e:
                        logger.info("BH Port: ({} - {})".format(bh_port, e.message))
                # bh capacity
                if bh_capacity:
                    try:
                        basestation.bh_capacity = int(bh_capacity)
                    except Exception as e:
                        logger.info("BH Capacity: ({} - {})".format(bh_capacity, e.message))
                # bs type
                if bs_type:
                    try:
                        basestation.bs_type = bs_type
                    except Exception as e:
                        logger.info("BS Type: ({} - {})".format(bs_type, e.message))
                # bh bso
                if bh_bso:
                    try:
                        basestation.bh_bso = bh_bso
                    except Exception as e:
                        logger.info("BH BSO: ({} - {})".format(bh_bso, e.message))
                # hssu used
                if hssu_used:
                    try:
                        basestation.hssu_used = hssu_used
                    except Exception as e:
                        logger.info("HSSU Used: ({} - {})".format(hssu_used, e.message))
                # hssu port
                if hssu_port:
                    try:
                        basestation.hssu_port = hssu_port
                    except Exception as e:
                        logger.info("HSSU Port: ({} - {})".format(hssu_port, e.message))
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        basestation.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        basestation.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # infra provider
                if infra_provider:
                    try:
                        basestation.infra_provider = infra_provider
                    except Exception as e:
                        logger.info("Infra Provider: ({} - {})".format(infra_provider, e.message))
                # gps type
                if gps_type:
                    try:
                        basestation.gps_type = gps_type
                    except Exception as e:
                        logger.info("GPS Type: ({} - {})".format(gps_type, e.message))
                # building height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            basestation.building_height = building_height
                        except Exception as e:
                            logger.info("Building Height: ({} - {})".format(building_height, e.message))
                    if isinstance(building_height, basestring):
                        try:
                            basestation.building_height = Decimal(building_height)
                        except Exception as e:
                            logger.info("Building Height: ({} - {})".format(building_height, e.message))
                # tower height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            basestation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                    if isinstance(tower_height, basestring):
                        try:
                            basestation.tower_height = Decimal(tower_height)
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                try:
                    basestation.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        basestation_state = get_state(state=state)
                        if not basestation_state:
                            raise Exception("While Basestation Update: State Not Found")
                        basestation.state = basestation_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            basestation_city = get_city(state=state, city_name=city)
                            if not basestation_city:
                                raise Exception("While Basestation Update: City Not Found")
                        else:
                            raise Exception("While Basestation Update: In City: State Not Found")
                        basestation.city = basestation_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # maintenance status
                basestation.maintenance_status = "No"
                # provisioning status
                basestation.provisioning_status = "Normal"
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
                # site ams
                if site_ams:
                    try:
                        basestation.site_ams = site_ams
                    except Exception as e:
                        logger.info("Site AMS: ({} - {})".format(site_ams, e.message))
                # site infra type
                if site_infra_type:
                    try:
                        basestation.site_infra_type = site_infra_type
                    except Exception as e:
                        logger.info("Site Infra Type: ({} - {})".format(site_infra_type, e.message))
                # site sap id
                if site_sap_id:
                    try:
                        basestation.site_sap_id = site_sap_id
                    except Exception as e:
                        logger.info("Site SAP Type: ({} - {})".format(site_sap_id, e.message))
                # mgmt vlan
                if mgmt_vlan:
                    try:
                        basestation.mgmt_vlan = mgmt_vlan
                    except Exception as e:
                        logger.info("MGMT VLAN: ({} - {})".format(mgmt_vlan, e.message))
                try:
                    basestation.save()
                    return basestation
                except Exception as e:
                    logger.info("Base Station Object: ({} - {})".format(name, e.message))
                    return ""


def create_sector(sector_payload):
    """ Create Sector object

    Args:
        sector_payload (dict): {
                                    'description': 'Sectorcreatedon28-Sep-2014at22: 55: 03.',
                                    'antenna': <Antenna: 10.75.158.219>,
                                    'ip': u'10.75.158.219',
                                    'sector_configured_on': <Device: 10.75.158.219>,
                                    'base_station': <BaseStation: east_of_kailash_dr>,
                                    'bs_technology': 2
                               }

    Returns:
        sector (class 'inventory.models.Sector'): <Sector: 10.75.158.219>

    """

    # dictionary containing sector payload
    sector_payload = sector_payload

    # initializing variables
    name, alias, sector_id, base_station, bs_technology, sector_configured_on, sector_configured_on_port = [''] * 7
    antenna, mrc, tx_power, rx_power, rf_bandwidth, frame_length, cell_radius, frequency, modulation = [''] * 9
    dr_site, dr_configured_on, description, planned_frequency, rfs_date = [''] * 5

    # get sector parameters
    if 'name' in sector_payload.keys():
        name = sector_payload['name'] if sector_payload['name'] else ""
    if 'alias' in sector_payload.keys():
        alias = sector_payload['alias'] if sector_payload['alias'] else ""
    if 'sector_id' in sector_payload.keys():
        sector_id = sector_payload['sector_id'] if sector_payload['sector_id'] else ""
    if 'base_station' in sector_payload.keys():
        base_station = sector_payload['base_station'] if sector_payload['base_station'] else ""
    if 'bs_technology' in sector_payload.keys():
        bs_technology = sector_payload['bs_technology'] if sector_payload['bs_technology'] else ""
    if 'sector_configured_on' in sector_payload.keys():
        sector_configured_on = sector_payload['sector_configured_on'] if sector_payload['sector_configured_on'] else ""
    if 'sector_configured_on_port' in sector_payload.keys():
        sector_configured_on_port = sector_payload['sector_configured_on_port'] if sector_payload['sector_configured_on_port'] else ""
    if 'antenna' in sector_payload.keys():
        antenna = sector_payload['antenna'] if sector_payload['antenna'] else ""
    if 'dr_site' in sector_payload.keys():
        dr_site = sector_payload['dr_site'].lower() if sector_payload['dr_site'] else ""
    if 'dr_configured_on' in sector_payload.keys():
        dr_configured_on = sector_payload['dr_configured_on'] if sector_payload['dr_configured_on'] else ""
    if 'mrc' in sector_payload.keys():
        mrc = sector_payload['mrc'] if sector_payload['mrc'] else ""
    if 'tx_power' in sector_payload.keys():
        tx_power = sector_payload['tx_power'] if sector_payload['tx_power'] else ""
    if 'rx_power' in sector_payload.keys():
        rx_power = sector_payload['rx_power'] if sector_payload['rx_power'] else ""
    if 'rf_bandwidth' in sector_payload.keys():
        rf_bandwidth = sector_payload['rf_bandwidth'] if sector_payload['rf_bandwidth'] else ""
    if 'frame_length' in sector_payload.keys():
        frame_length = sector_payload['frame_length'] if sector_payload['frame_length'] else ""
    if 'cell_radius' in sector_payload.keys():
        cell_radius = sector_payload['cell_radius'] if sector_payload['cell_radius'] else ""
    if 'frequency' in sector_payload.keys():
        frequency = sector_payload['frequency'] if sector_payload['frequency'] else ""
    if 'planned_frequency' in sector_payload.keys():
        planned_frequency = sector_payload['planned_frequency'] if sector_payload['planned_frequency'] else ""
    if 'modulation' in sector_payload.keys():
        modulation = sector_payload['modulation'] if sector_payload['modulation'] else ""
    if 'description' in sector_payload.keys():
        description = sector_payload['description'] if sector_payload['description'] else ""
    if 'rfs_date' in sector_payload.keys():
        rfs_date = sector_payload['rfs_date'] if sector_payload['rfs_date'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a', '_']:
            # ---------------------------- UPDATING SECTOR -----------------------------
            try:
                # update sector if it exists in database
                sector = Sector.objects.get(name=name)
                # alias
                if alias:
                    try:
                        sector.alias = alias
                    except Exception as e:
                        logger.info("Sector Alias: ({} - {})".format(alias, e.message))

                # sector id
                if sector_id:
                    try:
                        sector.sector_id = sector_id
                    except Exception as e:
                        logger.info("Sector ID: ({} - {})".format(sector_id, e.message))
                # base station
                if base_station:
                    try:
                        sector.base_station = base_station
                    except Exception as e:
                        logger.info("Sector Base Station: ({} - {})".format(base_station, e.message))
                # bs technology
                if bs_technology:
                    try:
                        sector.bs_technology = DeviceTechnology.objects.get(pk=bs_technology)
                    except Exception as e:
                        logger.info("BS Technology: ({} - {})".format(bs_technology, e.message))
                # sector configured on
                if sector_configured_on:
                    try:
                        sector.sector_configured_on = sector_configured_on
                    except Exception as e:
                        logger.info("Sector Configured On: ({} - {})".format(sector_configured_on, e.message))
                # sector configured on port
                if sector_configured_on_port:
                    try:
                        sector.sector_configured_on_port = sector_configured_on_port
                    except Exception as e:
                        logger.info("Sector Configured On Port: ({} - {})".format(sector_configured_on_port, e.message))
                # antenna
                if antenna:
                    try:
                        sector.antenna = antenna
                    except Exception as e:
                        logger.info("Sector Antenna: ({} - {})".format(antenna, e.message))
                # mrc
                if mrc:
                    try:
                        sector.mrc = mrc
                    except Exception as e:
                        logger.info("MRC: ({} - {})".format(mrc, e.message))
                # dr site
                if dr_site:
                    try:
                        if dr_site == "yes":
                            sector.dr_site = "Yes"
                        elif dr_site == "no":
                            sector.dr_site = "No"
                        else:
                            sector.dr_site = ""
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))

                # dr configured on
                if dr_configured_on:
                    try:
                        sector.dr_configured_on = dr_configured_on
                    except Exception as e:
                        logger.exception("DR Configured On: ({} - {})".format(dr_configured_on, e.message))
                # tx power
                if tx_power:
                    if isinstance(tx_power, int) or isinstance(tx_power, float):
                        try:
                            sector.tx_power = tx_power
                        except Exception as e:
                            logger.info("TX Power: ({} - {})".format(tx_power, e.message))
                # rx power
                if rx_power:
                    if isinstance(rx_power, int) or isinstance(rx_power, float):
                        try:
                            sector.rx_power = rx_power
                        except Exception as e:
                            logger.info("RX Power: ({} - {})".format(rx_power, e.message))
                # rf bandwidth
                if rf_bandwidth:
                    if isinstance(rf_bandwidth, int) or isinstance(rf_bandwidth, float):
                        try:
                            sector.rf_bandwidth = rf_bandwidth
                        except Exception as e:
                            logger.info("RF Bandwidth: ({} - {})".format(rf_bandwidth, e.message))
                # frame length
                if frame_length:
                    if isinstance(frame_length, int) or isinstance(frame_length, float):
                        try:
                            sector.frame_length = frame_length
                        except Exception as e:
                            logger.info("Frame Length: ({} - {})".format(frame_length, e.message))
                # cell radius
                if cell_radius:
                    if isinstance(cell_radius, int) or isinstance(cell_radius, float):
                        try:
                            sector.cell_radius = cell_radius
                        except Exception as e:
                            logger.info("Cell Radius: ({} - {})".format(cell_radius, e.message))
                # frequency
                if frequency:
                    if isinstance(frequency, int) or isinstance(frequency, float):
                        try:
                            sector.frequency = frequency
                        except Exception as e:
                            logger.info("Frequency: ({} - {})".format(frequency, e.message))
                # planned frequency
                if planned_frequency:
                    if isinstance(planned_frequency, int) or isinstance(planned_frequency, float):
                        try:
                            sector.planned_frequency = planned_frequency
                        except Exception as e:
                            logger.info("Planned Frequency: ({} - {})".format(planned_frequency, e.message))
                # modulation
                if modulation:
                    try:
                        sector.modulation = modulation
                    except Exception as e:
                        logger.info("Modulation: ({} - {})".format(modulation, e.message))
                # description
                if description:
                    try:
                        sector.description = description
                    except Exception as e:
                        logger.info("Sector Description: ({} - {})".format(description, e.message))
                # rfs date
                if rfs_date:
                    try:
                        sector.rfs_date = rfs_date
                    except Exception as e:
                        logger.info("RFS Date: ({} - {})".format(rfs_date, e.message))
                # saving sector
                sector.save()
                return sector
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create sector if it doesn't exist in database
                sector = Sector()
                # name
                if name:
                    try:
                        sector.name = name
                    except Exception as e:
                        logger.info("Sector Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        sector.alias = alias
                    except Exception as e:
                        logger.info("Sector Alias: ({} - {})".format(alias, e.message))
                # sector id
                if sector_id:
                    try:
                        sector.sector_id = sector_id
                    except Exception as e:
                        logger.info("Sector ID: ({} - {})".format(sector_id, e.message))
                # base station
                if base_station:
                    try:
                        sector.base_station = base_station
                    except Exception as e:
                        logger.info("Sector Base Station: ({} - {})".format(base_station, e.message))
                # bs technology
                if bs_technology:
                    try:
                        sector.bs_technology = DeviceTechnology.objects.get(pk=bs_technology)
                    except Exception as e:
                        logger.info("BS Technology: ({} - {})".format(bs_technology, e.message))
                # sector configured on
                if sector_configured_on:
                    try:
                        sector.sector_configured_on = sector_configured_on
                    except Exception as e:
                        logger.info("Sector Configured On: ({} - {})".format(sector_configured_on, e.message))
                # sector configured on port
                if sector_configured_on_port:
                    try:
                        sector.sector_configured_on_port = sector_configured_on_port
                    except Exception as e:
                        logger.info("Sector Configured On Port: ({} - {})".format(sector_configured_on_port, e.message))
                # antenna
                if antenna:
                    try:
                        sector.antenna = antenna
                    except Exception as e:
                        logger.info("Sector Antenna: ({} - {})".format(antenna, e.message))
                # mrc
                if mrc:
                    try:
                        sector.mrc = mrc
                    except Exception as e:
                        logger.info("MRC: ({} - {})".format(mrc, e.message))
                # dr site
                if dr_site:
                    try:
                        if dr_site == "yes":
                            sector.dr_site = "Yes"
                        elif dr_site == "no":
                            sector.dr_site = "No"
                        else:
                            sector.dr_site = ""
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))

                # dr configured on
                if dr_configured_on:
                    try:
                        sector.dr_configured_on = dr_configured_on
                    except Exception as e:
                        logger.exception("DR Configured On: ({} - {})".format(dr_configured_on, e.message))
                # tx power
                if tx_power:
                    if isinstance(tx_power, int) or isinstance(tx_power, float):
                        try:
                            sector.tx_power = tx_power
                        except Exception as e:
                            logger.info("TX Power: ({} - {})".format(tx_power, e.message))
                # rx power
                if rx_power:
                    if isinstance(rx_power, int) or isinstance(rx_power, float):
                        try:
                            sector.rx_power = rx_power
                        except Exception as e:
                            logger.info("RX Power: ({} - {})".format(rx_power, e.message))
                # rf bandwidth
                if rf_bandwidth:
                    if isinstance(rf_bandwidth, int) or isinstance(rf_bandwidth, float):
                        try:
                            sector.rf_bandwidth = rf_bandwidth
                        except Exception as e:
                            logger.info("RF Bandwidth: ({} - {})".format(rf_bandwidth, e.message))
                # frame length
                if frame_length:
                    if isinstance(frame_length, int) or isinstance(frame_length, float):
                        try:
                            sector.frame_length = frame_length
                        except Exception as e:
                            logger.info("Frame Length: ({} - {})".format(frame_length, e.message))
                # cell radius
                if cell_radius:
                    if isinstance(cell_radius, int) or isinstance(cell_radius, float):
                        try:
                            sector.cell_radius = cell_radius
                        except Exception as e:
                            logger.info("Cell Radius: ({} - {})".format(cell_radius, e.message))
                # frequency
                if frequency:
                    if isinstance(frequency, int) or isinstance(frequency, float):
                        try:
                            sector.frequency = frequency
                        except Exception as e:
                            logger.info("Frequency: ({} - {})".format(frequency, e.message))
                # planned frequency
                if planned_frequency:
                    if isinstance(planned_frequency, int) or isinstance(planned_frequency, float):
                        try:
                            sector.planned_frequency = planned_frequency
                        except Exception as e:
                            logger.info("Planned Frequency: ({} - {})".format(planned_frequency, e.message))
                # modulation
                if modulation:
                    try:
                        sector.modulation = modulation
                    except Exception as e:
                        logger.info("Modulation: ({} - {})".format(modulation, e.message))
                # description
                if description:
                    try:
                        sector.description = description
                    except Exception as e:
                        logger.info("Sector Description: ({} - {})".format(description, e.message))
                # rfs date
                if rfs_date:
                    try:
                        sector.rfs_date = rfs_date
                    except Exception as e:
                        logger.info("RFS Date: ({} - {})".format(rfs_date, e.message))
                try:
                    sector.save()
                    return sector
                except Exception as e:
                    logger.info("Sector Object: ({} - {})".format(name, e.message))
                    return ""


def create_customer(customer_payload):
    """ Create Customer object

    Args:
        customer_payload (dict): {
                                    'alias': u'Lotte-India-Corp-Ltd',
                                    'description': 'SSCustomercreatedon28-Sep-2014at22: 55: 03.',
                                    'name': 'lotte_india_corp_ltd',
                                    'address': u'LOTTEINDIACORPORATIONLTD.,
                                    FLATNO.301,
                                    IIIrdFLOOR,
                                    SHAYOGBUILDING-58,
                                    NEHRUPALACE,
                                    ,
                                    NEWDELHI-110019.,
                                    NewDelhi,
                                    DelhiIndia110019'
                                }

    Returns:
        customer (class 'inventory.models.Customer'): <Customer: 10.75.158.219>

    """

    # dictionary containing customer payload
    customer_payload = customer_payload

    # initializing variables
    name, alias, address, description = [''] * 4

    # get customer parameters
    if 'name' in customer_payload.keys():
        name = customer_payload['name'] if customer_payload['name'] else ""
    if 'alias' in customer_payload.keys():
        alias = customer_payload['alias'] if customer_payload['alias'] else ""
    if 'address' in customer_payload.keys():
        address = customer_payload['address'] if customer_payload['address'] else ""
    if 'description' in customer_payload.keys():
        description = customer_payload['description'] if customer_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING CUSTOMER -----------------------------
            try:
                # update customer if it exists in database
                customer = Customer.objects.get(name=name)
                # alias
                if alias:
                    try:
                        customer.alias = alias
                    except Exception as e:
                        logger.info("Customer Alias: ({} - {})".format(alias, e.message))
                # address
                if address:
                    try:
                        customer.address = address
                    except Exception as e:
                        logger.info("Customer Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        customer.description = description
                    except Exception as e:
                        logger.info("Customer Description: ({} - {})".format(description, e.message))
                # saving customer
                customer.save()
                return customer
            except Exception as e:
                # ---------------------------- CREATING CUSTOMER -------------------------------
                # create sector if it doesn't exist in database
                customer = Customer()
                # name
                if name:
                    try:
                        customer.name = name
                    except Exception as e:
                        logger.info("Customer Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        customer.alias = alias
                    except Exception as e:
                        logger.info("Customer Alias: ({} - {})".format(alias, e.message))
                # address
                if address:
                    try:
                        customer.address = address
                    except Exception as e:
                        logger.info("Customer Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        customer.description = description
                    except Exception as e:
                        logger.info("Customer Description: ({} - {})".format(description, e.message))
                try:
                    customer.save()
                    return customer
                except Exception as e:
                    logger.info("Customer Object: ({} - {})".format(name, e.message))
                    return ""


def create_substation(substation_payload):
    """ Create SubStation object

    Args:
        substation_payload (dict): {
                                        'tower_height': 15.0,
                                        'description': 'SubStationcreatedon28-Sep-2014at22: 55: 03.',
                                        'building_height': 31.0,
                                        'address': u'LOTTEINDIACORPORATIONLTD.,
                                        FLATNO.301,
                                        IIIrdFLOOR,
                                        SHAYOGBUILDING-58,
                                        NEHRUPALACE,
                                        ,
                                        NEWDELHI-110019.,
                                        NewDelhi,
                                        DelhiIndia110019',
                                        'device': <Device: 10.75.158.220>,
                                        'cable_length': 45.0,
                                        'city': u'Delhi(NewDelhi)',
                                        'name': '091newd623009178956',
                                        'antenna': <Antenna: 10.75.158.220>,
                                        'ethernet_extender': u'NA',
                                        'longitude': 77.25227777777778,
                                        'alias': u'10.75.158.220',
                                        'state': u'Delhi',
                                        'mac_address': u'00: 15: 67: da: 1a: 29',
                                        'latitude': 28.548944444444444
                                   }

    Returns:
        substation (class 'inventory.models.SubStation'): <SubStation: 10.75.158.219>

    """

    # dictionary containing substation payload
    substation_payload = substation_payload

    # lat long validator
    regex_lat_long = '^[-+]?\d*\.\d+|\d+'

    # initializing variables
    name, alias, device, antenna, version, serial_no, building_height, tower_height, ethernet_extender = [''] * 9
    cable_length, latitude, longitude, mac_address, country, state, city, address, description = [''] * 9
    cpe_vlan, sacfa_no = [''] * 2

    # get substation parameters
    if 'name' in substation_payload.keys():
        name = substation_payload['name'] if substation_payload['name'] else ""
    if 'alias' in substation_payload.keys():
        alias = substation_payload['alias'] if substation_payload['alias'] else ""
    if 'device' in substation_payload.keys():
        device = substation_payload['device'] if substation_payload['device'] else ""
    if 'antenna' in substation_payload.keys():
        antenna = substation_payload['antenna'] if substation_payload['antenna'] else ""
    if 'version' in substation_payload.keys():
        version = substation_payload['version'] if substation_payload['version'] else ""
    if 'serial_no' in substation_payload.keys():
        serial_no = substation_payload['serial_no'] if substation_payload['serial_no'] else ""
    if 'building_height' in substation_payload.keys():
        building_height = substation_payload['building_height'] if substation_payload['building_height'] else ""
    if 'tower_height' in substation_payload.keys():
        tower_height = substation_payload['tower_height'] if substation_payload['tower_height'] else ""
    if 'ethernet_extender' in substation_payload.keys():
        ethernet_extender = substation_payload['ethernet_extender'] if substation_payload['ethernet_extender'] else ""
    if 'cable_length' in substation_payload.keys():
        cable_length = substation_payload['cable_length'] if substation_payload['cable_length'] else ""
    if 'latitude' in substation_payload.keys():
        latitude = substation_payload['latitude'] if substation_payload['latitude'] else ""
    if 'longitude' in substation_payload.keys():
        longitude = substation_payload['longitude'] if substation_payload['longitude'] else ""
    if 'mac_address' in substation_payload.keys():
        mac_address = substation_payload['mac_address'] if substation_payload['mac_address'] else ""
    if 'country' in substation_payload.keys():
        country = substation_payload['country'] if substation_payload['country'] else ""
    if 'state' in substation_payload.keys():
        state = substation_payload['state'] if substation_payload['state'] else ""
    if 'city' in substation_payload.keys():
        city = substation_payload['city'] if substation_payload['city'] else ""
    if 'address' in substation_payload.keys():
        address = substation_payload['address'] if substation_payload['address'] else ""
    if 'cpe_vlan' in substation_payload.keys():
        cpe_vlan = substation_payload['cpe_vlan'] if substation_payload['cpe_vlan'] else ""
    if 'sacfa_no' in substation_payload.keys():
        sacfa_no = substation_payload['sacfa_no'] if substation_payload['sacfa_no'] else ""
    if 'description' in substation_payload.keys():
        description = substation_payload['description'] if substation_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING SUB STATION -----------------------------
            try:
                # update substation if it exists in database
                substation = SubStation.objects.get(name=name)
                # alias
                if alias:
                    try:
                        substation.alias = alias
                    except Exception as e:
                        logger.info("Sub Station Alias: ({} - {})".format(alias, e.message))
                # device
                if device:
                    try:
                        substation.device = device
                    except Exception as e:
                        logger.info("Sub Station Device: ({} - {})".format(device, e.message))
                # antenna
                if antenna:
                    try:
                        substation.antenna = antenna
                    except Exception as e:
                        logger.info("Sub Station Antenna: ({} - {})".format(antenna, e.message))
                # version
                if version:
                    try:
                        substation.version = version
                    except Exception as e:
                        logger.info("Sub Station Version: ({} - {})".format(version, e.message))
                # serial no
                if serial_no:
                    try:
                        substation.serial_no = serial_no
                    except Exception as e:
                        logger.info("Sub Station Serial No.: ({} - {})".format(serial_no, e.message))
                # building_height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            substation.building_height = building_height
                        except Exception as e:
                            logger.info("Sub Station Building Height: ({} - {})".format(building_height, e.message))
                # tower_height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            substation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Sub Station Tower Height: ({} - {})".format(antenna, e.message))
                # ethernet extender
                if ethernet_extender:
                    try:
                        if ethernet_extender == "yes":
                            substation.ethernet_extender = "Yes"
                        elif ethernet_extender == "no":
                            substation.ethernet_extender = "No"
                        else:
                            substation.ethernet_extender = ""
                    except Exception as e:
                        logger.info("Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        substation.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        substation.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                try:
                    substation.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        substation_state = get_state(state=state)
                        if not substation_state:
                            raise Exception("While Substation Update: State Not Found")
                        substation.state = substation_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            substation_city = get_city(state=state, city_name=city)
                            if not substation_city:
                                raise Exception("While Substation Update: City Not Found")
                        else:
                            raise Exception("While Substation Update: In City: State Not Found")
                        substation.city = substation_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        substation.address = address
                    except Exception as e:
                        logger.info("Sub Station Address: ({})".format(e.message))
                # cpe vlan
                if cpe_vlan:
                    try:
                        substation.cpe_vlan = cpe_vlan
                    except Exception as e:
                        logger.info("CPE VLAN: ({})".format(e.message))
                # sacfa no
                if sacfa_no:
                    try:
                        substation.sacfa_no = sacfa_no
                    except Exception as e:
                        logger.info("SACFA No.: ({})".format(e.message))
                # description
                if description:
                    try:
                        substation.description = description
                    except Exception as e:
                        logger.info("Sub Station Sector Description: ({} - {})".format(description, e.message))
                # saving sub station
                substation.save()
                return substation
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create substation if it doesn't exist in database
                substation = SubStation()
                # name
                if name:
                    try:
                        substation.name = name
                    except Exception as e:
                        logger.info("Sub Station Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        substation.alias = alias
                    except Exception as e:
                        logger.info("Sub Station Alias: ({} - {})".format(alias, e.message))
                # device
                if device:
                    try:
                        substation.device = device
                    except Exception as e:
                        logger.info("Sub Station Device: ({} - {})".format(device, e.message))
                # antenna
                if antenna:
                    try:
                        substation.antenna = antenna
                    except Exception as e:
                        logger.info("Sub Station Antenna: ({} - {})".format(antenna, e.message))
                # version
                if version:
                    try:
                        substation.version = version
                    except Exception as e:
                        logger.info("Sub Station Version: ({} - {})".format(version, e.message))
                # serial no
                if serial_no:
                    try:
                        substation.serial_no = serial_no
                    except Exception as e:
                        logger.info("Sub Station Serial No.: ({} - {})".format(serial_no, e.message))
                # building_height
                if building_height:
                    if isinstance(building_height, int) or isinstance(building_height, float):
                        try:
                            substation.building_height = building_height
                        except Exception as e:
                            logger.info("Sub Station Building Height: ({} - {})".format(building_height, e.message))
                # tower_height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            substation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Sub Station Tower Height: ({} - {})".format(antenna, e.message))
                # ethernet extender
                if ethernet_extender:
                    try:
                        if ethernet_extender == "yes":
                            substation.ethernet_extender = "Yes"
                        elif ethernet_extender == "no":
                            substation.ethernet_extender = "No"
                        else:
                            substation.ethernet_extender = ""
                    except Exception as e:
                        logger.info("Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if re.match(regex_lat_long, str(latitude).strip()):
                    try:
                        substation.latitude = Decimal(latitude)
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if re.match(regex_lat_long, str(longitude).strip()):
                    try:
                        substation.longitude = Decimal(longitude)
                    except Exception as e:
                        logger.info("Longitude: ({} - {})".format(latitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                try:
                    substation.country = Country.objects.get(pk=1)
                except Exception as e:
                    logger.info("Country: ({}) not exist.".format(e.message))
                # state
                if state:
                    try:
                        substation_state = get_state(state=state)
                        if not substation_state:
                            raise Exception("While Substation Update: State Not Found")
                        substation.state = substation_state
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            substation_city = get_city(state=state, city_name=city)
                            if not substation_city:
                                raise Exception("While Substation Update: City Not Found")
                        else:
                            raise Exception("While Substation Update: In City: State Not Found")
                        substation.city = substation_city
                    except Exception as e:
                        logger.info("City: ({})".format(e.message))
                # address
                if address:
                    try:
                        substation.address = address
                    except Exception as e:
                        logger.info("Sub Station Address: ({})".format(e.message))
                # cpe vlan
                if cpe_vlan:
                    try:
                        substation.cpe_vlan = cpe_vlan
                    except Exception as e:
                        logger.info("CPE VLAN: ({})".format(e.message))
                # sacfa no
                if sacfa_no:
                    try:
                        substation.sacfa_no = sacfa_no
                    except Exception as e:
                        logger.info("SACFA No.: ({})".format(e.message))
                # description
                if description:
                    try:
                        substation.description = description
                    except Exception as e:
                        logger.info("Sub Station Sector Description: ({} - {})".format(description, e.message))
                try:
                    substation.save()
                    return substation
                except Exception as e:
                    logger.info("Sub Station Object: ({} - {})".format(name, e.message))
                    return ""


def create_circuit(circuit_payload):
    """ Create Circuit object

    Args:
        circuit_payload (dict): {
                                    'sector': <Sector: 10.75.158.219>,
                                    'description': 'Circuitcreatedon28-Sep-2014at22: 55: 03.',
                                    'date_of_acceptance': '',
                                    'circuit_id': u'091NEWD623009178956',
                                    'qos_bandwidth': 256.0,
                                    'sub_station': <SubStation: 091newd623009178956>,
                                    'dl_rssi_during_acceptance': u'NA',
                                    'customer': <Customer: lotte_india_corp_ltd>,
                                    'throughput_during_acceptance': u'NA',
                                    'name': '091newd623009178956',
                                    'alias': u'091NEWD623009178956'
                                }

    Returns:
        circuit (class 'inventory.models.Circuit'): <Circuit: 10.75.158.219>

    """

    # dictionary containing circuit payload
    circuit_payload = circuit_payload

    # initializing variables
    name, alias, circuit_type, circuit_id, sector, customer, sub_station, qos_bandwidth = [''] * 8
    dl_rssi_during_acceptance, dl_cinr_during_acceptance, jitter_value_during_acceptance = [''] * 3
    throughput_during_acceptance, date_of_acceptance, description, sold_cir = [''] * 4

    # get circuit parameters
    if 'name' in circuit_payload.keys():
        name = circuit_payload['name'] if circuit_payload['name'] else ""
    if 'alias' in circuit_payload.keys():
        alias = circuit_payload['alias'] if circuit_payload['alias'] else ""
    if 'circuit_type' in circuit_payload.keys():
        circuit_type = circuit_payload['circuit_type'] if circuit_payload['circuit_type'] else ""
    if 'circuit_id' in circuit_payload.keys():
        circuit_id = circuit_payload['circuit_id'] if circuit_payload['circuit_id'] else ""
    if 'sector' in circuit_payload.keys():
        sector = circuit_payload['sector'] if circuit_payload['sector'] else ""
    if 'customer' in circuit_payload.keys():
        customer = circuit_payload['customer'] if circuit_payload['customer'] else ""
    if 'sub_station' in circuit_payload.keys():
        sub_station = circuit_payload['sub_station'] if circuit_payload['sub_station'] else ""
    if 'qos_bandwidth' in circuit_payload.keys():
        qos_bandwidth = circuit_payload['qos_bandwidth'] if circuit_payload['qos_bandwidth'] else ""
    if 'dl_rssi_during_acceptance' in circuit_payload.keys():
        dl_rssi_during_acceptance = circuit_payload['dl_rssi_during_acceptance'] if circuit_payload['dl_rssi_during_acceptance'] else ""
    if 'dl_cinr_during_acceptance' in circuit_payload.keys():
        dl_cinr_during_acceptance = circuit_payload['dl_cinr_during_acceptance'] if circuit_payload['dl_cinr_during_acceptance'] else ""
    if 'jitter_value_during_acceptance' in circuit_payload.keys():
        jitter_value_during_acceptance = circuit_payload['jitter_value_during_acceptance'] if circuit_payload['jitter_value_during_acceptance'] else ""
    if 'throughput_during_acceptance' in circuit_payload.keys():
        throughput_during_acceptance = circuit_payload['throughput_during_acceptance'] if circuit_payload['throughput_during_acceptance'] else ""
    if 'date_of_acceptance' in circuit_payload.keys():
        date_of_acceptance = circuit_payload['date_of_acceptance'] if circuit_payload['date_of_acceptance'] else ""
    if 'description' in circuit_payload.keys():
        description = circuit_payload['description'] if circuit_payload['description'] else ""
    if 'sold_cir' in circuit_payload.keys():
        sold_cir = circuit_payload['sold_cir'] if circuit_payload['sold_cir'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING CIRCUIT -----------------------------
            try:
                # update circuit if it exists in database
                circuit = Circuit.objects.get(name=name)
                # alias
                if alias:
                    try:
                        circuit.alias = alias
                    except Exception as e:
                        logger.info("Circuit Alias: ({} - {})".format(alias, e.message))
                # circuit type
                if circuit_type:
                    try:
                        circuit.circuit_type = circuit_type
                    except Exception as e:
                        logger.info("Circuit Type: ({} - {})".format(circuit_type, e.message))
                # circuit id
                if circuit_id:
                    try:
                        circuit.circuit_id = circuit_id
                    except Exception as e:
                        logger.info("Circuit ID: ({} - {})".format(circuit_id, e.message))
                # sector
                if sector:
                    try:
                        circuit.sector = sector
                    except Exception as e:
                        logger.info("Sector: ({} - {})".format(sector, e.message))
                # customer
                if customer:
                    try:
                        circuit.customer = customer
                    except Exception as e:
                        logger.info("Customer: ({} - {})".format(customer, e.message))
                # sub station
                if sub_station:
                    try:
                        circuit.sub_station = sub_station
                    except Exception as e:
                        logger.info("Sub Station: ({} - {})".format(sub_station, e.message))
                # qos bandwidth
                if qos_bandwidth:
                    if isinstance(qos_bandwidth, int) or isinstance(qos_bandwidth, float):
                        try:
                            circuit.qos_bandwidth = qos_bandwidth
                        except Exception as e:
                            logger.info("QOS (BW): ({} - {})".format(qos_bandwidth, e.message))
                # dl rssi during acceptance
                if dl_rssi_during_acceptance:
                    try:
                        circuit.dl_rssi_during_acceptance = int(dl_rssi_during_acceptance)
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = int(dl_cinr_during_acceptance)
                    except Exception as e:
                        logger.info("CINR During Acceptance: ({} - {})".format(dl_cinr_during_acceptance, e.message))
                # jitter value during acceptance
                if jitter_value_during_acceptance:
                    try:
                        circuit.jitter_value_during_acceptance = jitter_value_during_acceptance
                    except Exception as e:
                        logger.info("Jitter Value During Acceptance: ({} - {})".format(jitter_value_during_acceptance, e.message))
                # throughput during acceptance
                if throughput_during_acceptance:
                    try:
                        circuit.throughput_during_acceptance = throughput_during_acceptance
                    except Exception as e:
                        logger.info("Throughput During Acceptance: ({} - {})".format(throughput_during_acceptance, e.message))
                # date_of_acceptance
                if date_of_acceptance:
                    try:
                        circuit.date_of_acceptance = date_of_acceptance
                    except Exception as e:
                        logger.info("Date Of Acceptance: ({} - {})".format(date_of_acceptance, e.message))
                # description
                if description:
                    try:
                        circuit.description = description
                    except Exception as e:
                        logger.info("Circuit Description: ({} - {})".format(description, e.message))
                # sold cir
                if sold_cir:
                    try:
                        circuit.sold_cir = sold_cir
                    except Exception as e:
                        logger.info("Sold CIR: ({} - {})".format(sold_cir, e.message))
                # saving circuit
                circuit.save()
                return circuit
            except Exception as e:
                # ---------------------------- CREATING CIRCUIT -------------------------------
                # create circuit if it doesn't exist in database
                circuit = Circuit()
                # name
                if name:
                    try:
                        circuit.name = name
                    except Exception as e:
                        logger.info("Circuit Name: ({} - {})".format(name, e.message))
                # alias
                if alias:
                    try:
                        circuit.alias = alias
                    except Exception as e:
                        logger.info("Circuit Alias: ({} - {})".format(alias, e.message))
                # circuit type
                if circuit_type:
                    try:
                        circuit.circuit_type = circuit_type
                    except Exception as e:
                        logger.info("Circuit Type: ({} - {})".format(circuit_type, e.message))
                # circuit id
                if circuit_id:
                    try:
                        circuit.circuit_id = circuit_id
                    except Exception as e:
                        logger.info("Circuit ID: ({} - {})".format(circuit_id, e.message))
                # sector
                if sector:
                    try:
                        circuit.sector = sector
                    except Exception as e:
                        logger.info("Sector: ({} - {})".format(sector, e.message))
                # customer
                if customer:
                    try:
                        circuit.customer = customer
                    except Exception as e:
                        logger.info("Customer: ({} - {})".format(customer, e.message))
                # sub station
                if sub_station:
                    try:
                        circuit.sub_station = sub_station
                    except Exception as e:
                        logger.info("Sub Station: ({} - {})".format(sub_station, e.message))
                # qos bandwidth
                if qos_bandwidth:
                    if isinstance(qos_bandwidth, int) or isinstance(qos_bandwidth, float):
                        try:
                            circuit.qos_bandwidth = qos_bandwidth
                        except Exception as e:
                            logger.info("QOS (BW): ({} - {})".format(qos_bandwidth, e.message))
                # dl rssi during acceptance
                if dl_rssi_during_acceptance:
                    try:
                        circuit.dl_rssi_during_acceptance = int(dl_rssi_during_acceptance)
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = int(dl_cinr_during_acceptance)
                    except Exception as e:
                        logger.info("CINR During Acceptance: ({} - {})".format(dl_cinr_during_acceptance, e.message))
                # jitter value during acceptance
                if jitter_value_during_acceptance:
                    try:
                        circuit.jitter_value_during_acceptance = jitter_value_during_acceptance
                    except Exception as e:
                        logger.info("Jitter Value During Acceptance: ({} - {})".format(jitter_value_during_acceptance, e.message))
                # throughput during acceptance
                if throughput_during_acceptance:
                    try:
                        circuit.throughput_during_acceptance = throughput_during_acceptance
                    except Exception as e:
                        logger.info("Throughput During Acceptance: ({} - {})".format(throughput_during_acceptance, e.message))
                # date_of_acceptance
                if date_of_acceptance:
                    try:
                        circuit.date_of_acceptance = date_of_acceptance
                    except Exception as e:
                        logger.info("Date Of Acceptance: ({} - {})".format(date_of_acceptance, e.message))
                # description
                if description:
                    try:
                        circuit.description = description
                    except Exception as e:
                        logger.info("Circuit Description: ({} - {})".format(description, e.message))
                # sold cir
                if sold_cir:
                    try:
                        circuit.sold_cir = sold_cir
                    except Exception as e:
                        logger.info("Sold CIR: ({} - {})".format(sold_cir, e.message))
                try:
                    circuit.save()
                    return circuit
                except Exception as e:
                    logger.info("Circuit Object: ({} - {})".format(name, e.message))
                    return ""


def create_device_port(name, alias, value):
    """ Create or Update device port

    Args:
        name (str): 'pmp1'
        alias (str): 'PMP Port 1'
        value (int): 1

    Returns:
        port (<class 'device.models.DevicePort'>): pmp1

    """
    try:
        # ---------------------------- UPDATING DEVICE PORT -------------------------------
        port = DevicePort.objects.get(name=name, value=value)
        port.name = name
        port.alias = alias
        port.value = value
        port.save()
        return port
    except Exception as e:
        # ---------------------------- CREATING DEVICE PORT -------------------------------
        port = DevicePort()
        port.name = name
        port.alias = alias
        port.value = value
        try:
            port.save()
            return port
        except Exception as e:
            logger.info("Port can't be created. Exception: ", e.message)


def get_ptp_machine_and_site(ip):
    """ Get PTP Machine object

    Args:
        ip (unicode): u'10.1.231.179'

    Returns:
        machine (dict): {
                            'machine': "",
                            'site': ""
                        }

    """

    # machine
    machine = ""

    # site
    site = ""
    try:
        # check whether IP is public or private
        test_ip = IP(ip)
        if test_ip.iptype() == 'PRIVATE':
            machine = Machine.objects.get(name='vrfprv')
            site = SiteInstance.objects.get(name='vrfprv_slave_1')
        elif test_ip.iptype() == 'PUBLIC':
            machine = Machine.objects.get(name='pub')
            site = SiteInstance.objects.get(name='pub_slave_1')
        else:
            machine = ""
    except Exception as e:
        logger.info(e.message)
    output = {'machine': machine, 'site': site}
    return output


def get_port_name_and_number(ports):
    """ Get Port Name and Number of first port

    Args:
        ports (unicode): u'Gi0/1,Gi0/2'

    Returns:
        [port_name, port_number] (list): ['Gi0', '1']

    """

    try:
        port = ports.split(',', 1)[0]
        port_name, port_number = port.rsplit('/', 1)
        return [port_name, port_number]
    except Exception as e:
        return ""


def validate_date(date_string):
    """ Get date string if it's a valid 'date' else return empty string

    Args:
        date_string (unicode): u'15-Aug-2014'

    Returns:
        date_string (str): '15-Aug-2014'

    """

    # 'date of acceptance' validation (must be like '15-Aug-2014')
    if date_string:
        try:
            # datetime.datetime.strptime(date_string, '%d-%b-%Y')
            # date_string = date_string
            parse(str(date_string))
            # date_string = datetime.datetime.strptime(str(date_string), '%d-%b-%Y')
        except Exception as e:
            date_string = ""
            logger.info("Datetime Exception", e.message)
        return date_string


def special_chars_name_sanitizer_with_lower_case(name):
    """ Clean and remove all special characters form string and replace them (special characters) from underscore

    Args:
        name (unicode): u'Maniyar Complex'

    Returns:
        name (str): 'maniyar_complex'

    """
    # remove all non-word characters (everything except numbers and letters)
    if isinstance(name, int) or isinstance(name, float):
        name = int(name)
        output = re.sub(r"[^\w\s+]", '_', str(name))
        # replace all runs of whitespace with a single underscore, convert to lower chars and then strip '_'
        output = re.sub(r"\s+", '_', output).lower().strip('_')
    elif isinstance(name, unicode) or isinstance(name, str):
        output = re.sub(r"[^\w\s+]", '_', name.encode('utf-8').strip())
        # replace all runs of whitespace with a single underscore, convert to lower chars and then strip '_'
        output = re.sub(r"\s+", '_', output).lower().strip('_')
    else:
        output = ""
    return unicode(output)


def circuit_id_sanitizer(name):
    """ Clean and remove all special characters form string and replace them (special characters) from underscore

    Args:
        name (unicode): u'Maniyar Complex'

    Returns:
        name (str): 'Maniyar Complex'

    """
    # remove all non-word characters (everything except numbers and letters)
    if isinstance(name, int) or isinstance(name, float):
        name = int(name)
        output = name
    elif isinstance(name, str) or isinstance(name, unicode):
        name = name.replace('.', '')
        output = name
    else:
        output = ""
    return unicode(output)


def ip_sanitizer(name):
    """ Check and clean ip address

    Args:
        name (unicode): u'192.168.1.1'

    Returns:
        name (str): '192.168.1.1'

    """
    name = name
    if isinstance(name, str):
        name = name.strip()
        try:
            IP(name)
        except Exception as e:
            name = ""
    elif isinstance(name, unicode):
        name = name.encode('utf-8').strip()
        try:
            IP(name)
        except Exception as e:
            name = ""
    else:
        name = ""

    return name


def get_state(state=None):
    """ Return id of state or None

    Kwargs:
        state (unicode): u'West Bengal'

    Returns:
        state_objects[0] (<class 'device.models.State'>): state object for e.g. Delhi

    """
    if state:
        state_objects = State.objects.filter(state_name__icontains=state)
        if len(state_objects):
            return state_objects[0]
    return None


def get_city(state=None, city_name=None):
    """ Return id of city or None

    Kwargs:
        state (unicode): u'Tamil Nadu'
        city (unicode): u'Chennai'

    Returns:
        city_objects[0] (<class 'device.models.City'>): city object for e.g. Delhi

    """
    if state and city_name:
        city_objects = City.objects.filter(city_name__icontains=city_name, state__state_name__icontains=state)
        if len(city_objects):
            return city_objects[0]
    return None


def sanitize_mac_address(mac=None):
    """ Check and clean mac address

    Kwargs:
        mac (unicode): u'0a:00:3e:66:fd:94'

    Returns:
        mac (unicode): u'0a:00:3e:66:fd:94'

    """
    number_types = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
    if isinstance(mac, number_types):
        mac = str(mac)

    mac = ''.join(e for e in mac if e.isalnum()).lower()
    if len(mac) == 12:
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    else:
        mac = ""
    return mac


def get_machine_details(mc_name, machine_numbers=None):
    """ Send dictionary containing information of requested machines

    Args:
        machine_numbers (list): [1, 2, 3, 4]

    Returns:
        ospf_machines_dict (dict):  {
                                        'ospf4': [
                                            {
                                                u'ospf4_slave_1': 0
                                            }
                                        ],
                                        'ospf1': [
                                            {
                                                u'ospf1_slave_1': 41
                                            },
                                            {
                                                u'ospf1_slave_2': 0
                                            }
                                        ],
                                        'ospf3': [
                                            {
                                                u'ospf3_slave_1': 0
                                            }
                                        ],
                                        'ospf2': [
                                            {
                                                u'ospf2_slave_1': 0
                                            }
                                        ]
                                    }

    """

    # machine info dictionary
    machines_dict = dict()

    if mc_name and machine_numbers:
        for machine_number in machine_numbers:
            # machine name
            machine_name = str(mc_name) + str(machine_number)

            machines_dict[machine_name] = list()

            # get machine
            machine = ""
            try:
                machine = Machine.objects.get(name=machine_name)
            except Exception as e:
                logger.info("Machine doesn't exist.:", e.message)

            # get all sites associated with current machine
            try:
                sites = machine.siteinstance_set.all()
            except Exception as e:
                sites = []
                logger.info("No sites available.")

            if sites:
                for site in sites:
                    # site instance dictionary
                    site_dict = dict()
                    site_dict[site.name] = len(Device.objects.filter(site_instance=site))
                    # append site instance in machine sites list
                    machines_dict[machine_name].append(site_dict)
            else:
                machines_dict[machine_name] = {}
            machine_name = ""

        return machines_dict

    elif mc_name and not machine_numbers:
        # machine name
        machine_name = str(mc_name)

        machines_dict[machine_name] = list()

        # get machine
        machine = ""
        try:
            machine = Machine.objects.get(name=machine_name)
        except Exception as e:
            logger.info("Machine doesn't exist.:", e.message)

        # get all sites associated with current machine
        sites = machine.siteinstance_set.all()

        if sites:
            for site in sites:
                # site instance dictionary
                site_dict = dict()
                site_dict[site.name] = len(Device.objects.filter(site_instance=site))
                # append site instance in machine sites list
                machines_dict[machine_name].append(site_dict)

            return machines_dict
    else:
        return ""


def get_machine_and_site(machines_dict):
    """ Send dictionary containing information of requested machines

    Args:
        machines_dict (list): {
                                    'ospf1': [
                                        {
                                            u'ospf1_slave_1': 49
                                        },
                                        {
                                            u'ospf1_slave_2': 0
                                        }
                                    ]
                                }

    Returns:
        (dict):  {
                    'machine': <Machine: ospf1>,
                    'site': <SiteInstance: ospf1_slave_1>
                }

    """

    if machines_dict:
        for machine, sites in machines_dict.iteritems():
            try:
                current_machine = machine
            except Exception as e:
                logger.info("PMP/Wimax machine. Exception: ", e.message)
            try:
                current_machine = Machine.objects.get(name=machine)
                for site in sites:
                    for name, number_of_devices in site.iteritems():
                        if number_of_devices < 1400:
                            current_site = SiteInstance.objects.get(name=name)
                            return {'machine': current_machine, 'site': current_site}
                        else:
                            logger.error("******************** Machine/Sites limit reached.")
                            return ""            
            except Exception as e:
                logger.info("******************** M/C Exception: ", e.message)
                return ""


def get_ip_network(ip):
    """ Get IP network i.e public or private

    Args:
        ip (unicode): u'10.1.231.179'

    Returns:
        ip_network (str): 'public'

    """
    # ip network
    ip_network = ""

    try:

        # check whether IP is public or private
        test_ip = IP(ip)
        if test_ip.iptype() == 'PRIVATE':
            ip_network = "private"
        elif test_ip.iptype() == 'PUBLIC':
            ip_network = "public"
        else:
            ip_network = ""
    except Exception as e:
        logger.info(e.message)
    return ip_network

# ******************************* START GIS INVENTORY DOWNLOAD **********************************
@task
def generate_gis_inventory_excel(base_stations="", username="", fulltime="", gis_excel_download_id=""):

    # list of ptp rows
    ptp_rows = []

    # list of ptp bh rows
    ptp_bh_rows = []

    # list of pmp bs
    pmp_bs_rows = []

    # list of pmp sm sheet
    pmp_sm_rows = []

    # list of wimax bs rows
    wimax_bs_rows = []

    # list of wimax ss rows
    wimax_ss_rows = []

    # selected inventory
    selected_inventory = dict()

    # ptp dictionary
    ptp_fields = ['State', 'City', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                  'QOS (BW)', 'Latitude', 'Longitude', 'MIMO/Diversity', 'Antenna Height', 'Polarization',
                  'Antenna Type', 'Antenna Gain', 'Antenna Mount Type', 'Ethernet Extender', 'Building Height',
                  'Tower/Pole Height', 'Cable Length', 'RSSI During Acceptance', 'Throughput During Acceptance',
                  'Date Of Acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU Used', 'BS Switch IP', 'Aggregation Switch',
                  'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP', 'Converter Type',
                  'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet',
                  'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'BSO Circuit ID', 'SS City', 'SS State',
                  'SS Circuit ID', 'SS Customer Name', 'SS Customer Address', 'SS BS Name', 'SS QOS (BW)',
                  'SS Latitude', 'SS Longitude', 'SS Antenna Height', 'SS Antenna Type', 'SS Antenna Gain',
                  'SS Antenna Mount Type', 'SS Ethernet Extender', 'SS Building Height', 'SS Tower/Pole Height',
                  'SS Cable Length', 'SS RSSI During Acceptance', 'SS Throughput During Acceptance',
                  'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC',
                  'BS Product Type', 'BS Frequency', 'BS UAS', 'BS RSSI', 'BS Estimated Throughput',
                  'BS Utilisation DL', 'BS Utilisation UL', 'BS Uptime', 'BS Link Distance', 'BS CBW', 'BS Latency',
                  'BS PD', 'BS Auto Negotiation', 'BS Duplex', 'BS Speed', 'BS Link',
                  'SS Product Type', 'SS Frequency', 'SS UAS', 'SS RSSI', 'SS Estimated Throughput',
                  'SS Utilisation DL', 'SS Utilisation UL', 'SS Uptime', 'SS Link Distance', 'SS CBW', 'SS Latency',
                  'SS PD', 'SS Auto Negotiation', 'SS Duplex', 'SS Speed', 'SS Link']

    # ptp bh dictionary
    ptp_bh_fields = ['State', 'City', 'Circuit ID', 'Circuit Type', 'Customer Name', 'BS Address', 'BS Name',
                     'QOS (BW)', 'Latitude', 'Longitude', 'MIMO/Diversity', 'Antenna Height', 'Polarization',
                     'Antenna Type', 'Antenna Gain', 'Antenna Mount Type', 'Ethernet Extender', 'Building Height',
                     'Tower/Pole Height', 'Cable Length', 'RSSI During Acceptance', 'Throughput During Acceptance',
                     'Date Of Acceptance', 'BH BSO', 'IP', 'MAC', 'HSSU Used', 'BS Switch IP', 'Aggregation Switch',
                     'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP', 'Converter Type',
                     'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity', 'BH Offnet/Onnet',
                     'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'BSO CKT ID', 'SS City', 'SS State',
                     'SS Circuit ID', 'SS Customer Name', 'SS Customer Address', 'SS BS Name', 'SS QOS (BW)',
                     'SS Latitude', 'SS Longitude', 'SS Antenna Height', 'SS Antenna Type', 'SS Antenna Gain',
                     'SS Antenna Mount Type', 'SS Ethernet Extender', 'SS Building Height', 'SS Tower/Pole Height',
                     'SS Cable Length', 'SS RSSI During Acceptance', 'SS Throughput During Acceptance',
                     'SS Date Of Acceptance', 'SS BH BSO', 'SS IP', 'SS MAC', 'SS MIMO/Diversity',
                     'SS Polarization',
                     'BS Product Type', 'BS Frequency', 'BS UAS', 'BS RSSI', 'BS Estimated Throughput',
                     'BS Utilisation DL', 'BS Utilisation UL', 'BS Uptime', 'BS Link Distance', 'BS CBW',
                     'BS Latency', 'BS PD', 'BS Auto Negotiation', 'BS Duplex', 'BS Speed', 'BS Link',
                     'SS Product Type', 'SS Frequency', 'SS UAS', 'SS RSSI', 'SS Estimated Throughput',
                     'SS Utilisation DL', 'SS Utilisation UL', 'SS Uptime', 'SS Link Distance', 'SS CBW',
                     'SS Latency', 'SS PD', 'SS Auto Negotiation', 'SS Duplex', 'SS Speed', 'SS Link']

    # pmp bs dictionary
    pmp_bs_fields = ['State', 'City', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                     'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                     'ODU IP', 'Sector Name', 'Make Of Antenna', 'Polarization', 'Antenna Tilt', 'Antenna Height',
                     'Antenna Beamwidth', 'Azimuth', 'Sync Splitter Used', 'Type Of GPS', 'BS Switch IP',
                     'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP',
                     'Converter Type', 'BH Configured On Switch/Converter', 'Switch/Converter Port', 'BH Capacity',
                     'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID', 'PE Hostname', 'PE IP', 'DR Site',
                     'Sector ID', 'BSO Circuit ID', 'Latency', 'PD', 'Frequency', 'Cell Radius', 'Utilization DL',
                     'Utilization UL', 'Sector Uptime', 'TX Power', 'RX Power']

    # pmp ss dictionary
    pmp_sm_fields = ['Customer Name', 'Circuit ID', 'SS IP', 'Site ID', 'QOS (BW)', 'Latitude', 'Longitude', 'MAC',
                     'Building Height', 'Tower/Pole Height', 'Antenna Height', 'Antenna Beamwidth',
                     'Polarization', 'Antenna Type', 'SS Mount Type', 'Ethernet Extender', 'Cable Length',
                     'RSSI During Acceptance', 'CINR During Acceptance', 'Customer Address', 'Date Of Acceptance',
                     'Lens/Reflector', 'AP IP', 'Frequency', 'RSSI DL', 'RSSI UL', 'Jitter DL',
                     'Jitter UL', 'Transmit Power', 'Polled SS IP', 'Polled SS MAC', 'Polled BS IP',
                     'Polled BS MAC', 'Session Uptime', 'Latency', 'PD', 'Utilization DL', 'Utilization UL',
                     'Auto Negotiation', 'Duplex', 'Speed', 'Link']

    # wimax bs dictionary
    wimax_bs_fields = ['State', 'City', 'Address', 'BS Name', 'Type Of BS (Technology)', 'Site Type',
                       'Infra Provider', 'Site ID', 'Building Height', 'Tower Height', 'Latitude', 'Longitude',
                       'IDU IP', 'Sector Name', 'Make Of Antenna', 'Polarization', 'Antenna Tilt', 'Antenna Height',
                       'Antenna Beamwidth', 'Azimuth', 'Installation Of Splitter', 'Type Of GPS', 'BS Switch IP',
                       'Aggregation Switch', 'Aggregation Switch Port', 'BS Converter IP', 'POP Converter IP',
                       'Converter Type', 'BH Configured On Switch/Converter', 'Switch/Converter Port',
                       'BH Capacity', 'BH Offnet/Onnet', 'Backhaul Type', 'BH Circuit ID', 'PE Hostname',
                       'Sector Utilization DL', 'Sector Utilization UL', 'PE IP', 'DR Site', 'DR Master/Slave',
                       'Sector ID', 'BSO Circuit ID', 'PMP', 'Vendor', 'Frequency', 'MRC', 'IDU Type', 'System Uptime',
                       'Latency', 'PD']

    # wimax ss dictionary
    wimax_ss_fields = ['Customer Name', 'Circuit ID', 'SS IP', 'QOS (BW)', 'Latitude', 'Longitude', 'MAC',
                       'Building Height', 'Tower/Pole Height', 'Antenna Height', 'Antenna Beamwidth',
                       'Polarization', 'Antenna Type', 'SS Mount Type', 'Ethernet Extender', 'Cable Length',
                       'RSSI During Acceptance', 'CINR During Acceptance', 'Customer Address', 'Date Of Acceptance',
                       'Vendor', 'Frequency', 'Sector ID', 'Polled SS IP', 'Polled SS MAC', 'RSSI DL', 'RSSI UL',
                       'CINR DL', 'CINR UL', 'INTRF DL', 'INTRF UL', 'PTX', 'Session Uptime', 'Device Uptime',
                       'Modulation UL FEC', 'Modulation DL FEC', 'Latency', 'PD', 'Utilization DL',
                       'Utilization UL', 'Auto Negotiation', 'Duplex', 'Speed', 'Link']

    # get base stations id's
    bs_ids = base_stations

    # loop on base stations by using bs_ids list conatining base stations id's
    try:
        for bs_id in bs_ids:
            # base station
            base_station = BaseStation.objects.get(pk=int(bs_id))

            # sectors associated with base station (base_station)
            sectors = base_station.sector.all()

            # loop on sectors to get inventory rows by technology
            for sector in sectors:
                # sector technology
                technology = sector.bs_technology.name
                if technology == "P2P":
                    rows = get_selected_ptp_inventory(base_station, sector)
                    # insert 'ptp' data dictionary in 'ptp_rows' list
                    ptp_rows.extend(rows['ptp'])
                    # insert 'ptp_bh' data dictionary in 'ptp_bh_rows' list
                    ptp_bh_rows.extend(rows['ptp_bh'])
                elif technology == "PMP":
                    rows = get_selected_pmp_inventory(base_station, sector)
                    # insert 'pmp bs' data dictionary in 'pmp_bs_rows' list
                    pmp_bs_rows.extend(rows['pmp_bs'])
                    # insert 'pmp_sm' data dictionary in 'pmp_sm_rows' list
                    pmp_sm_rows.extend(rows['pmp_sm'])
                elif technology == "WiMAX":
                    rows = get_selected_wimax_inventory(base_station, sector)
                    # insert 'wimax bs' data dictionary in 'wimax_bs_rows' list
                    wimax_bs_rows.extend(rows['wimax_bs'])
                    # insert 'wimax_ss' data dictionary in 'wimax_ss_rows' list
                    wimax_ss_rows.extend(rows['wimax_ss'])
                else:
                    pass
    except Exception as e:
        logger.info("Something wrongs with base station in initial loop. Exception: {}".format(e.message))

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['ptp'] = ptp_rows

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['ptp_bh'] = ptp_bh_rows

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['pmp_bs'] = pmp_bs_rows

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['pmp_sm'] = pmp_sm_rows

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['wimax_bs'] = wimax_bs_rows

    # insert 'ptp rows' in selected inventory dictionary
    selected_inventory['wimax_ss'] = wimax_ss_rows

    # inventory excel workbook
    inventory_wb = xlwt.Workbook()

    # ***************************** PTP *******************************
    # remove duplicate dictionaries from ptp list
    ptp_rows = remove_duplicate_dict_from_list(ptp_rows)

    # ptp bs excel rows
    ptp_excel_rows = []
    for val in ptp_rows:
        temp_list = list()
        for key in ptp_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        ptp_excel_rows.append(temp_list)

    # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_ptp = inventory_wb.add_sheet("PTP")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(ptp_fields):
            ws_ptp.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(ptp_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_ptp.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # ***************************** PTP BH *******************************
    # remove duplicate dictionaries from ptp bh list
    ptp_bh_rows = remove_duplicate_dict_from_list(ptp_bh_rows)

    # ptp bh bs excel rows
    ptp_bh_excel_rows = []
    for val in ptp_bh_rows:
        temp_list = list()
        for key in ptp_bh_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        ptp_bh_excel_rows.append(temp_list)

    # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_ptp_bh = inventory_wb.add_sheet("PTP BH")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(ptp_bh_fields):
            ws_ptp_bh.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(ptp_bh_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_ptp_bh.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # ***************************** PMP BS *******************************
    # remove duplicate dictionaries from pmp bs list
    pmp_bs_rows = remove_duplicate_dict_from_list(pmp_bs_rows)

    # pmp bs excel rows
    pmp_bs_excel_rows = []
    for val in pmp_bs_rows:
        temp_list = list()
        for key in pmp_bs_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        pmp_bs_excel_rows.append(temp_list)

    # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_pmp_bs = inventory_wb.add_sheet("PMP BS")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(pmp_bs_fields):
            ws_pmp_bs.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(pmp_bs_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_pmp_bs.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # ***************************** PMP SM *******************************
    # remove duplicate dictionaries from pmp sm list
    pmp_sm_rows = remove_duplicate_dict_from_list(pmp_sm_rows)

    # pmp sm excel rows
    pmp_sm_excel_rows = []
    for val in pmp_sm_rows:
        temp_list = list()
        for key in pmp_sm_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        pmp_sm_excel_rows.append(temp_list)

    # wimax sm sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_pmp_sm = inventory_wb.add_sheet("PMP SM")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(pmp_sm_fields):
            ws_pmp_sm.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(pmp_sm_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_pmp_sm.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # ***************************** Wimax BS *******************************
    # remove duplicate dictionaries from wimax bs list
    wimax_bs_rows = remove_duplicate_dict_from_list(wimax_bs_rows)

    # wimax bs excel rows
    wimax_bs_excel_rows = []
    for val in wimax_bs_rows:
        temp_list = list()
        for key in wimax_bs_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        wimax_bs_excel_rows.append(temp_list)

    # wimax bs sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_wimax_bs = inventory_wb.add_sheet("Wimax BS")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(wimax_bs_fields):
            ws_wimax_bs.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(wimax_bs_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_wimax_bs.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # ***************************** Wimax SS *******************************
    # remove duplicate dictionaries from wimax ss list
    wimax_ss_rows = remove_duplicate_dict_from_list(wimax_ss_rows)

    # wimax ss excel rows
    wimax_ss_excel_rows = []
    for val in wimax_ss_rows:
        temp_list = list()
        for key in wimax_ss_fields:
            try:
                temp_list.append(val[key])
            except Exception as e:
                temp_list.append("")
                logger.info(e.message)
        wimax_ss_excel_rows.append(temp_list)

    # wimax ss sheet (contain by inventory excel workbook i.e inventory_wb)
    ws_wimax_ss = inventory_wb.add_sheet("Wimax SS")

    # style for header row in excel
    style = xlwt.easyxf('pattern: pattern solid, fore_colour tan;')

    # creating excel headers
    try:
        for i, col in enumerate(wimax_ss_fields):
            ws_wimax_ss.write(0, i, col.decode('utf-8', 'ignore').strip(), style)
    except Exception as e:
        logger.info("Problem in creating excel headers. Exception: ", e.message)

    # creating excel rows
    try:
        for i, l in enumerate(wimax_ss_excel_rows):
            i += 1
            for j, col in enumerate(l):
                ws_wimax_ss.write(i, j, col)
    except Exception as e:
        logger.info("Problem in creating excel rows. Exception: ", e.message)

    # if directory for excel sheet doesn't exist than create one
    if not os.path.exists(MEDIA_ROOT + 'inventory_files/map_inventory_downloads'):
        os.makedirs(MEDIA_ROOT + 'inventory_files/map_inventory_downloads')

    # get gis excel download object
    gis_excel_download_obj = ""
    try:
        gis_excel_download_obj = GISExcelDownload.objects.get(id=gis_excel_download_id)
    except Exception as e:
        logger.info(e.message)

    # ***************************** Saving Excel (Start) ******************************
    if gis_excel_download_obj:
        filename = 'inventory_files/map_inventory_downloads/{}_{}_gis_inventory_excel.xls'.format(fulltime, username)
        # saving bulk upload errors excel sheet
        try:
            inventory_wb.save(MEDIA_ROOT + filename)
            gis_excel_download_obj.file_path = filename
            gis_excel_download_obj.description = "Successfully download inventory on {}.".format(fulltime)
            gis_excel_download_obj.status = 1
            gis_excel_download_obj.save()
        except Exception as e:
            gis_excel_download_obj.status = 2
            gis_excel_download_obj.description = "Failed to download inventory on {}.".format(fulltime)
            gis_excel_download_obj.save()
            logger.info(e.message)
    # ****************************** Saving Excel (End) *******************************


def get_selected_ptp_inventory(base_station, sector):
    # result dictionary (contains ptp and ptp bh inventory)
    result = dict()

    # base station device name
    bs_device_name = ""
    try:
        bs_device_name = sector.sector_configured_on.device_name
    except Exception as e:
        logger.info("PTP BS Device not exist. Exception: ", e.message)

    # base station machine
    bs_machine_name = ""
    try:
        bs_machine_name = sector.sector_configured_on.machine.name
    except Exception as e:
        logger.info("PTP BS Machine not found.  Exception: ", e.message)

    # ptp rows list
    ptp_rows = list()

    # ptp bh rows list
    ptp_bh_rows = list()

    # circuits associated with current sector
    circuits = sector.circuit_set.all()

    # loop through circuits; if available to get inventory rows
    if circuits:
        for circuit in circuits:
            # sub station
            sub_station = circuit.sub_station

            # sub station device name
            ss_device_name = ""
            try:
                ss_device_name = sub_station.device.device_name
            except Exception as e:
                logger.info("PTP SS device not found. Exception: ", e.message)

            # sub station machine
            ss_machine_name = ""
            try:
                ss_machine_name = sub_station.device.machine.name
            except Exception as e:
                logger.info("PTP SS machine not found. Exception: ", e.message)

            # backhaul
            backhaul = base_station.backhaul

            # customer
            customer = circuit.customer

            # ptp row dictionary
            ptp_row = dict()

            # state
            try:
                ptp_row['State'] = base_station.state.state_name
            except Exception as e:
                logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

            # city
            try:
                ptp_row['City'] = base_station.city.city_name
            except Exception as e:
                logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

            # circuit id
            try:
                if circuit.circuit_type == "Customer":
                    ptp_row['Circuit ID'] = circuit.circuit_id
                elif circuit.circuit_type == "Backhaul":
                    ptp_row['Circuit ID'] = circuit.circuit_id.split("#")[-1]
                else:
                    pass
            except Exception as e:
                logger.info("Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

            # circuit type
            try:
                ptp_row['Circuit Type'] = circuit.circuit_type
            except Exception as e:
                logger.info("Circuit Type not exist for base station ({}).".format(base_station.name, e.message))

            # customer name
            try:
                ptp_row['Customer Name'] = customer.alias
            except Exception as e:
                logger.info("Customer Name not exist for base station ({}).".format(base_station.name, e.message))

            # bs address
            try:
                ptp_row['BS Address'] = base_station.address
            except Exception as e:
                logger.info("BS Address not exist for base station ({}).".format(base_station.name, e.message))

            # bs name
            try:
                ptp_row['BS Name'] = base_station.alias
            except Exception as e:
                logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

            # qos bandwidth
            try:
                ptp_row['QOS (BW)'] = circuit.qos_bandwidth
            except Exception as e:
                logger.info("QOS (BW) not exist for base station ({}).".format(base_station.name, e.message))

            # latitude
            try:
                ptp_row['Latitude'] = base_station.latitude
            except Exception as e:
                logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

            # longitude
            try:
                ptp_row['Longitude'] = base_station.longitude
            except Exception as e:
                logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

            # antenna height
            try:
                ptp_row['Antenna Height'] = sector.antenna.height
            except Exception as e:
                logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

            # polarization
            try:
                ptp_row['Polarization'] = sector.antenna.polarization
            except Exception as e:
                logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

            # antenna type
            try:
                ptp_row['Antenna Type'] = sector.antenna.antenna_type
            except Exception as e:
                logger.info("Antenna Type not exist for base station ({}).".format(base_station.name, e.message))

            # antenna gain
            try:
                ptp_row['Antenna Gain'] = sector.antenna.gain
            except Exception as e:
                logger.info("Antenna Gain not exist for base station ({}).".format(base_station.name, e.message))

            # antenna mount type
            try:
                ptp_row['Antenna Mount Type'] = sector.antenna.mount_type
            except Exception as e:
                logger.info("Antenna Mount Type not exist for base station ({}).".format(base_station.name,
                                                                                         e.message))

            # ethernet extender
            try:
                ptp_row['Ethernet Extender'] = sub_station.ethernet_extender
            except Exception as e:
                logger.info("Ethernet Extender not exist for base station ({}).".format(base_station.name,
                                                                                        e.message))

            # building height
            try:
                ptp_row['Building Height'] = base_station.building_height
            except Exception as e:
                logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

            # tower/pole height
            try:
                ptp_row['Tower/Pole Height'] = base_station.tower_height
            except Exception as e:
                logger.info("Tower/Pole Height not exist for base station ({}).".format(base_station.name,
                                                                                        e.message))

            # cable length
            try:
                ptp_row['Cable Length'] = sub_station.cable_length
            except Exception as e:
                logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

            # rssi during acceptance
            try:
                ptp_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
            except Exception as e:
                logger.info("RSSI During Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                             e.message))

            # throughput during acceptance
            try:
                ptp_row['Throughput During Acceptance'] = circuit.throughput_during_acceptance
            except Exception as e:
                logger.info("Throughput During Acceptance not exist for base station ({}).".format(
                    base_station.name,
                    e.message))

            # date of acceptance
            try:
                ptp_row['Date Of Acceptance'] = circuit.date_of_acceptance
            except Exception as e:
                logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                         e.message))

            # bh bso
            try:
                ptp_row['BH BSO'] = base_station.bh_bso
            except Exception as e:
                logger.info("BH BSO not exist for base station ({}).".format(base_station.name, e.message))

            # ip
            try:
                ptp_row['IP'] = sector.sector_configured_on.ip_address
            except Exception as e:
                logger.info("IP not exist for base station ({}).".format(base_station.name, e.message))

            # mac
            try:
                ptp_row['MAC'] = sector.sector_configured_on.mac_address
            except Exception as e:
                logger.info("MAC not exist for base station ({}).".format(base_station.name, e.message))

            # hssu used
            try:
                ptp_row['HSSU Used'] = base_station.hssu_used
            except Exception as e:
                logger.info("HSSU Used not exist for base station ({}).".format(base_station.name, e.message))

            # bs switch ip
            try:
                ptp_row['BS Switch IP'] = base_station.bs_switch.ip_address
            except Exception as e:
                logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

            # aggregation switch
            try:
                ptp_row['Aggregation Switch'] = backhaul.aggregator.ip_address
            except Exception as e:
                logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                         e.message))

            # aggregation swith port
            try:
                ptp_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
            except Exception as e:
                logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                              e.message))

            # bs conveter ip
            try:
                ptp_row['BS Converter IP'] = backhaul.bh_switch.ip_address
            except Exception as e:
                logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

            # pop converter ip
            try:
                ptp_row['POP Converter IP'] = backhaul.pop.ip_address
            except Exception as e:
                logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                                       e.message))

            # converter type
            try:
                ptp_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
            except Exception as e:
                logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

            # bh configured switch or converter
            try:
                ptp_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
            except Exception as e:
                logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
                    base_station.name,
                    e.message))

            # bh configured switch or converter port
            try:
                ptp_row['Switch/Converter Port'] = backhaul.bh_port_name
            except Exception as e:
                logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

            # bh capacity
            try:
                ptp_row['BH Capacity'] = backhaul.bh_capacity
            except Exception as e:
                logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

            # bh offnet/onnet
            try:
                ptp_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
            except Exception as e:
                logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

            # backhaul type
            try:
                ptp_row['Backhaul Type'] = backhaul.bh_type
            except Exception as e:
                logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

            # bh circuit id
            try:
                ptp_row['BH Circuit ID'] = backhaul.bh_circuit_id
            except Exception as e:
                logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

            # pe hostname
            try:
                ptp_row['PE Hostname'] = backhaul.pe_hostname
            except Exception as e:
                logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

            # pe ip
            try:
                ptp_row['PE IP'] = backhaul.pe_ip
            except Exception as e:
                logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

            # bso circuit id
            try:
                ptp_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
            except Exception as e:
                logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

            # ********************************* PTP BS Perf Info *************************************
            # bs pl/pd (packet loss/drop)
            pl = ""
            try:
                pl = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                  data_source='pl').using(
                                                  alias=bs_machine_name)[0].current_value
                ptp_row['BS PD'] = pl
            except Exception as e:
                logger.info("BS PD not exist for base station ({}).".format(base_station.name, e.message))

            # bs latency
            try:
                ptp_row['BS Latency'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='rta').using(
                                                                     alias=bs_machine_name)[0].current_value
            except Exception as e:
                logger.info("BS Latency not exist for base station ({}).".format(base_station.name, e.message))

            if pl != "100":
                # bs product type
                try:
                    ptp_row['BS Product Type'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                                data_source='producttype').using(
                                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Product Type not exist for base station ({}).".format(base_station.name, e.message))

                # bs frequency
                try:
                    ptp_row['BS Frequency'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Frequency not exist for base station ({}).".format(base_station.name, e.message))

                # bs uas
                try:
                    ptp_row['BS UAS'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='uas').using(
                                                                     alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS UAS not exist for base station ({}).".format(base_station.name, e.message))

                # mimo/diversity
                try:
                    ptp_rows['MIMO/Diversity'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                                service_name='radwin_odu_sn_invent',
                                                                                data_source='odu_sn').using(
                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("MIMO/Diversity not exist for base station ({}).".format(base_station.name, e.message))

                # bs rssi
                try:
                    ptp_row['BS RSSI'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                      data_source='rssi').using(
                                                                      alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS RSSI not exist for base station ({}).".format(base_station.name, e.message))

                # bs estimated throughput
                try:
                    ptp_row['BS Estimated Throughput'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_service_throughput',
                                                                        data_source='service_throughput').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Estimated Throughput not exist for base station ({}).".format(base_station.name,
                                                                                                  e.message))

                # bs utilization dl
                try:
                    ptp_row['BS Utilisation DL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_dl_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Utilisation DL not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # bs utilization ul
                try:
                    ptp_row['BS Utilisation UL'] = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                        service_name='radwin_ul_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Utilisation UL not exist for base station ({}).".format(base_station.name,
                                                                                            e.message))

                # bs uptime
                try:
                    bs_uptime = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                             service_name='radwin_uptime',
                                                             data_source='uptime').using(
                        alias=bs_machine_name)[0].current_value
                    ptp_row['BS Uptime'] = display_time(bs_uptime)
                except Exception as e:
                    logger.info("BS Uptime not exist for base station ({}).".format(base_station.name, e.message))

                # bs link distance
                try:
                    ptp_row['BS Link Distance'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                                 data_source='link_distance').using(
                                                                                 alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Link Distance not exist for base station ({}).".format(base_station.name,
                                                                                           e.message))

                # bs cbw
                try:
                    ptp_row['BS CBW'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                       data_source='cbw').using(
                                                                       alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS CBW not exist for base station ({}).".format(base_station.name, e.message))

                # bs auto negotiation
                try:
                    ptp_row['BS Auto Negotiation'] = Status.objects.filter(device_name=bs_device_name,
                                                                           service_name='radwin_autonegotiation_status',
                                                                           data_source='1').using(
                                                                           alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Auto Negotiation not exist for base station ({}).".format(base_station.name,
                                                                                              e.message))

                # bs duplex
                try:
                    ptp_row['BS Duplex'] = Status.objects.filter(device_name=bs_device_name,
                                                                 service_name='radwin_port_mode_status',
                                                                 data_source='1').using(
                                                                 alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Duplex not exist for base station ({}).".format(base_station.name, e.message))

                # bs speed
                try:
                    ptp_row['BS Speed'] = Status.objects.filter(device_name=bs_device_name,
                                                                service_name='radwin_port_speed_status',
                                                                data_source='1').using(
                                                                alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Speed not exist for base station ({}).".format(base_station.name, e.message))

                # bs link
                try:
                    ptp_row['BS Link'] = Status.objects.filter(device_name=bs_device_name,
                                                               service_name='radwin_link_ethernet_status',
                                                               data_source='Management_Port_on_Odu').using(
                                                               alias=bs_machine_name)[0].current_value
                except Exception as e:
                    logger.info("BS Link not exist for base station ({}).".format(base_station.name, e.message))

            # ********************************** PTP Far End (SS) ************************************

            # ss city
            try:
                ptp_row['SS City'] = sub_station.city.city_name
            except Exception as e:
                logger.info("SS City not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss state
            try:
                ptp_row['SS State'] = sub_station.state.state_name
            except Exception as e:
                logger.info("SS State not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss circuit id
            try:
                if circuit.circuit_type == "Customer":
                    ptp_row['SS Circuit ID'] = circuit.circuit_id
                elif circuit.circuit_type == "Backhaul":
                    ptp_row['SS Circuit ID'] = circuit.circuit_id.split("#")[0]
                else:
                    pass
            except Exception as e:
                logger.info("SS Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss customer name
            try:
                ptp_row['SS Customer Name'] = customer.alias
            except Exception as e:
                logger.info("SS Customer Name not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss customer address
            try:
                ptp_row['SS Customer Address'] = customer.address
            except Exception as e:
                logger.info("SS Customer Address not exist for sub station ({}).".format(sub_station.name,
                                                                                         e.message))

            # ss bs name
            try:
                ptp_row['SS BS Name'] = base_station.alias
            except Exception as e:
                logger.info("SS BS Name not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss qos bandwidth
            try:
                ptp_row['SS QOS (BW)'] = circuit.qos_bandwidth
            except Exception as e:
                logger.info("SS QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss latitude
            try:
                ptp_row['SS Latitude'] = sub_station.latitude
            except Exception as e:
                logger.info("SS Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss longitude
            try:
                ptp_row['SS Longitude'] = sub_station.longitude
            except Exception as e:
                logger.info("SS Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss antenna height
            try:
                ptp_row['SS Antenna Height'] = sub_station.antenna.height
            except Exception as e:
                logger.info("SS Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss antenna type
            try:
                ptp_row['SS Antenna Type'] = sub_station.antenna.antenna_type
            except Exception as e:
                logger.info("SS Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss antenna gain
            try:
                ptp_row['SS Antenna Gain'] = sub_station.antenna.gain
            except Exception as e:
                logger.info("SS Antenna Gain not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss antenna mount type
            try:
                ptp_row['SS Antenna Mount Type'] = sub_station.antenna.mount_type
            except Exception as e:
                logger.info("SS Antenna Mount Type not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

            # ss ethernet extender
            try:
                ptp_row['SS Ethernet Extender'] = sub_station.ethernet_extender
            except Exception as e:
                logger.info("SS Ethernet Extender not exist for sub station ({}).".format(sub_station.name,
                                                                                          e.message))

            # ss building height
            try:
                ptp_row['SS Building Height'] = sub_station.building_height
            except Exception as e:
                logger.info("SS Building Height not exist for sub station ({}).".format(sub_station.name,
                                                                                        e.message))

            # ss tower or pole height
            try:
                ptp_row['SS Tower/Pole Height'] = sub_station.tower_height
            except Exception as e:
                logger.info("SS Tower/Pole Height not exist for sub station ({}).".format(sub_station.name,
                                                                                          e.message))

            # ss cable length
            try:
                ptp_row['SS Cable Length'] = sub_station.cable_length
            except Exception as e:
                logger.info("SS Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss rssi during acceptance
            try:
                ptp_row['SS RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
            except Exception as e:
                logger.info("SS RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                               e.message))

            # ss throughput during acceptance
            try:
                ptp_row['SS Throughput During Acceptance'] = circuit.throughput_during_acceptance
            except Exception as e:
                logger.info("SS Throughput During Acceptance not exist for sub station ({}).".format(
                    sub_station.name,
                    e.message))

            # ss date of acceptance
            try:
                ptp_row['SS Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
            except Exception as e:
                logger.info("SS Date Of Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

            # ss bh bso
            try:
                ptp_row['SS BH BSO'] = base_station.bh_bso
            except Exception as e:
                logger.info("SS BH BSO not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss ip
            try:
                ptp_row['SS IP'] = sub_station.device.ip_address
            except Exception as e:
                logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss mac
            try:
                ptp_row['SS MAC'] = sub_station.device.mac_address
            except Exception as e:
                logger.info("SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss polarization
            try:
                ptp_row['SS Polarization'] = sub_station.antenna.polarization
            except Exception as e:
                logger.info("SS Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

            # ********************************* PTP SS Perf Info *************************************
            pl = ""
            # ss pl/pd (packet loss/drop)
            try:
                pl = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                   data_source='pl').using(
                                                   alias=ss_machine_name)[0].current_value
                ptp_row['SS PD'] = pl
            except Exception as e:
                logger.info("SS PD not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss latency
            try:
                ptp_row['SS Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                     data_source='rta').using(
                                                                     alias=ss_machine_name)[0].current_value
            except Exception as e:
                logger.info("SS Latency not exist for sub station ({}).".format(sub_station.name, e.message))

            if pl != "100":
                # ss auto negotiation
                try:
                    ptp_row['SS Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                           service_name='radwin_autonegotiation_status',
                                                                           data_source='1').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Auto Negotiation not exist for sub station ({}).".format(sub_station.name,
                                                                                             e.message))

                # mimo/diversity
                try:
                    ptp_rows['SS MIMO/Diversity'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                   service_name='radwin_odu_sn_invent',
                                                                                   data_source='odu_sn').using(
                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS MIMO/Diversity not exist for base station ({}).".format(base_station.name, e.message))

                # ss product type
                try:
                    ptp_row['SS Product Type'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='producttype').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Product Type not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss frequency
                try:
                    ptp_row['SS Frequency'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss uas
                try:
                    ptp_row['SS UAS'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                     data_source='uas').using(
                                                                     alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS UAS not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss rssi
                try:
                    ptp_row['SS RSSI'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                      data_source='rssi').using(
                                                                      alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS RSSI not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss estimated throughput
                try:
                    ptp_row['SS Estimated Throughput'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_service_throughput',
                                                                        data_source='service_throughput').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Estimated Throughput not exist for sub station ({}).".format(sub_station.name,
                                                                                                 e.message))

                # ss utilization dl
                try:
                    ptp_row['SS Utilisation DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_dl_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Utilisation DL not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

                # ss utilization ul
                try:
                    ptp_row['SS Utilisation UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_ul_utilization',
                                                                        data_source='Management_Port_on_Odu').using(
                                                                        alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Utilisation UL not exist for sub station ({}).".format(sub_station.name,
                                                                                           e.message))

                # ss uptime
                try:
                    ss_uptime = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                        service_name='radwin_uptime',
                                                                        data_source='uptime').using(
                                                                        alias=ss_machine_name)[0].current_value
                    ptp_row['SS Uptime'] = display_time(ss_uptime)
                except Exception as e:
                    logger.info("SS Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss link distance
                try:
                    ptp_row['SS Link Distance'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                 data_source='link_distance').using(
                                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Link Distance not exist for sub station ({}).".format(sub_station.name,
                                                                                          e.message))

                # ss cbw
                try:
                    ptp_row['SS CBW'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                       data_source='cbw').using(
                                                                       alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS CBW not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss duplex
                try:
                    ptp_row['SS Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                 service_name='radwin_port_mode_status',
                                                                 data_source='1').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss speed
                try:
                    ptp_row['SS Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                service_name='radwin_port_speed_status',
                                                                data_source='1').using(
                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # ss link
                try:
                    ptp_row['SS Link'] = Status.objects.filter(device_name=ss_device_name,
                                                               service_name='radwin_link_ethernet_status',
                                                               data_source='Management_Port_on_Odu').using(
                                                               alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("SS Link not exist for sub station ({}).".format(sub_station.name, e.message))

            # filter 'ptp' and 'ptp bh' rows
            if circuit.circuit_type == "Customer":
                ptp_rows.append(ptp_row)
            elif circuit.circuit_type == "Backhaul":
                ptp_bh_rows.append(ptp_row)
            else:
                pass

    # insert 'ptp' rows in result dictionary
    result['ptp'] = ptp_rows if ptp_rows else ""

    # insert 'ptp bh' rows in result dictionary
    result['ptp_bh'] = ptp_bh_rows if ptp_bh_rows else ""

    return result

def get_selected_pmp_inventory(base_station, sector):
    # result dictionary (contains ptp and ptp bh inventory)
    result = dict()

    # base station device name
    bs_device_name = ""
    try:
        bs_device_name = sector.sector_configured_on.device_name
    except Exception as e:
        logger.info("PMP BS Device not exist. Exception: ", e.message)

    # bs device type
    bs_device_type = None
    try:
        bs_device_type = DeviceType.objects.get(id=sector.sector_configured_on.device_type).name
    except Exception as e:
        logger.info(e.message)

    # base station machine
    bs_machine_name = ""
    try:
        bs_machine_name = sector.sector_configured_on.machine.name
    except Exception as e:
        logger.info("PMP BS Machine not found.  Exception: ", e.message)

    # pmp bs rows list
    pmp_bs_rows = list()

    # pmp sm rows list
    pmp_sm_rows = list()

    # backhaul
    backhaul = base_station.backhaul

    # ptp row dictionary
    pmp_bs_row = dict()

    # circuits associated with current sector
    circuits = sector.circuit_set.all()

    # *********************************** Near End (PMP BS) *********************************

    # state
    try:
        pmp_bs_row['State'] = base_station.state.state_name
    except Exception as e:
        logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

    # city
    try:
        pmp_bs_row['City'] = base_station.city.city_name
    except Exception as e:
        logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

    # address
    try:
        pmp_bs_row['Address'] = base_station.address
    except Exception as e:
        logger.info("Address not exist for base station ({}).".format(base_station.name, e.message))

    # bs name
    try:
        pmp_bs_row['BS Name'] = base_station.alias
    except Exception as e:
        logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

    # site id
    try:
        pmp_bs_row['Site ID'] = base_station.bs_site_id
    except Exception as e:
        logger.info("Site ID not exist for base station ({}).".format(base_station.name, e.message))

    # type of bs (technology)
    try:
        pmp_bs_row['Type Of BS (Technology)'] = base_station.bs_type
    except Exception as e:
        logger.info("Type Of BS (Technology) not exist for base station ({}).".format(base_station.name,
                                                                                      e.message))

    # site type
    try:
        pmp_bs_row['Site Type'] = base_station.bs_site_type
    except Exception as e:
        logger.info("Site Type not exist for base station ({}).".format(base_station.name, e.message))

    # infra provider
    try:
        pmp_bs_row['Infra Provider'] = base_station.infra_provider
    except Exception as e:
        logger.info("Infra Provider not exist for base station ({}).".format(base_station.name, e.message))

    # building height
    try:
        pmp_bs_row['Building Height'] = base_station.building_height
    except Exception as e:
        logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

    # tower height
    try:
        pmp_bs_row['Tower Height'] = base_station.tower_height
    except Exception as e:
        logger.info("Tower Height not exist for base station ({}).".format(base_station.name, e.message))

    # latitude
    try:
        pmp_bs_row['Latitude'] = base_station.latitude
    except Exception as e:
        logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

    # longitude
    try:
        pmp_bs_row['Longitude'] = base_station.longitude
    except Exception as e:
        logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

    # odu ip
    try:
        pmp_bs_row['ODU IP'] = sector.sector_configured_on.ip_address
    except Exception as e:
        logger.info("ODU IP not exist for base station ({}).".format(base_station.name, e.message))

    # sector name
    try:
        pmp_bs_row['Sector Name'] = sector.name.split("_")[-1]
    except Exception as e:
        logger.info("Sector Name not exist for base station ({}).".format(base_station.name, e.message))

    # make of antenna
    try:
        pmp_bs_row['Make Of Antenna'] = sector.antenna.make_of_antenna
    except Exception as e:
        logger.info("Make Of Antenna not exist for base station ({}).".format(base_station.name,
                                                                              e.message))

    # polarization
    try:
        pmp_bs_row['Polarization'] = sector.antenna.polarization
    except Exception as e:
        logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

    # antenna tilt
    try:
        pmp_bs_row['Antenna Tilt'] = sector.antenna.tilt
    except Exception as e:
        logger.info("Antenna Tilt not exist for base station ({}).".format(base_station.name, e.message))

    # antenna height
    try:
        pmp_bs_row['Antenna Height'] = sector.antenna.height
    except Exception as e:
        logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

    # antenna beamwidth
    try:
        pmp_bs_row['Antenna Beamwidth'] = sector.antenna.beam_width
    except Exception as e:
        logger.info("Antenna Beamwidth not exist for base station ({}).".format(base_station.name,
                                                                                e.message))

    # azimuth
    try:
        pmp_bs_row['Azimuth'] = sector.antenna.azimuth_angle
    except Exception as e:
        logger.info("Azimuth not exist for base station ({}).".format(base_station.name, e.message))

    # sync splitter used
    try:
        pmp_bs_row['Sync Splitter Used'] = sector.antenna.sync_splitter_used
    except Exception as e:
        logger.info("Sync Splitter Used not exist for base station ({}).".format(base_station.name,
                                                                                 e.message))

    # type of gps
    try:
        pmp_bs_row['Type Of GPS'] = base_station.gps_type
    except Exception as e:
        logger.info("Type Of GPS not exist for base station ({}).".format(base_station.name, e.message))

    # bs switch ip
    try:
        pmp_bs_row['BS Switch IP'] = base_station.bs_switch.ip_address
    except Exception as e:
        logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

    # aggregation switch
    try:
        pmp_bs_row['Aggregation Switch'] = backhaul.aggregator.ip_address
    except Exception as e:
        logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                 e.message))

    # aggregation swith port
    try:
        pmp_bs_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
    except Exception as e:
        logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                      e.message))

    # bs conveter ip
    try:
        pmp_bs_row['BS Converter IP'] = backhaul.bh_switch.ip_address
    except Exception as e:
        logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

    # pop converter ip
    try:
        pmp_bs_row['POP Converter IP'] = backhaul.pop.ip_address
    except Exception as e:
        logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                               e.message))

    # converter type
    try:
        pmp_bs_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
    except Exception as e:
        logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

    # bh configured switch or converter
    try:
        pmp_bs_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
    except Exception as e:
        logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
            base_station.name,
            e.message))

    # bh configured switch or converter port
    try:
        pmp_bs_row['Switch/Converter Port'] = backhaul.bh_port_name
    except Exception as e:
        logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                    e.message))

    # bh capacity
    try:
        pmp_bs_row['BH Capacity'] = backhaul.bh_capacity
    except Exception as e:
        logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

    # bh offnet/onnet
    try:
        pmp_bs_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
    except Exception as e:
        logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

    # backhaul type
    try:
        pmp_bs_row['Backhaul Type'] = backhaul.bh_type
    except Exception as e:
        logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

    # bh circuit id
    try:
        pmp_bs_row['BH Circuit ID'] = backhaul.bh_circuit_id
    except Exception as e:
        logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

    # pe hostname
    try:
        pmp_bs_row['PE Hostname'] = backhaul.pe_hostname
    except Exception as e:
        logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

    # pe ip
    try:
        pmp_bs_row['PE IP'] = backhaul.pe_ip
    except Exception as e:
        logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

    # bso circuit id
    try:
        pmp_bs_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
    except Exception as e:
        logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

    # dr site
    try:
        pmp_bs_row['DR Site'] = sector.dr_site
    except Exception as e:
        logger.info("DR Site not exist for base station ({}).".format(base_station.name, e.message))

    # sector id
    try:
        pmp_bs_row['Sector ID'] = sector.sector_id
    except Exception as e:
        logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

    # ************************************* BS Perf Parameters **********************************
    # pl
    pl = ""
    try:
        pl = NetworkStatus.objects.filter(device_name=bs_device_name,
                                          data_source='pl').using(
                                          alias=bs_machine_name)[0].current_value
        pmp_bs_row['PD'] = pl
    except Exception as e:
        logger.info("PL not exist for base station ({}).".format(base_station.name, e.message))

    # latency
    try:
        pmp_bs_row['Latency'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                             data_source='rta').using(
                                                             alias=bs_machine_name)[0].current_value
    except Exception as e:
        logger.info("Latency not exist for base station ({}).".format(base_station.name, e.message))

    if pl != "100":
        # frequency
        try:
            pmp_bs_row['Frequency'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='frequency').using(
                                                                     alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("Frequency not exist for base station ({}).".format(base_station.name, e.message))

        # cell radius
        try:
            pmp_bs_row['Cell Radius'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                       data_source='cell_radius').using(
                                                                       alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("Cell Radius not exist for base station ({}).".format(base_station.name, e.message))

        # dl utilization
        try:
            if bs_device_type == "Radwin5KBS":
                pmp_bs_row['Utilization DL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='rad5k_bs_dl_utilization',
                    data_source='dl_utilization').using(
                    alias=bs_machine_name)[0].current_value
            else:
                pmp_bs_row['Utilization DL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='cambium_dl_utilization',
                    data_source='dl_utilization').using(
                    alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("Utilization DL not exist for base station ({}).".format(base_station.name, e.message))

        # ul utilization
        try:
            if bs_device_type == "Radwin5KBS":
                pmp_bs_row['Utilization UL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='rad5k_bs_ul_utilization',
                    data_source='ul_utilization').using(
                    alias=bs_machine_name)[0].current_value
            else:
                pmp_bs_row['Utilization UL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='cambium_ul_utilization',
                    data_source='ul_utilization').using(
                    alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("Utilization UL not exist for base station ({}).".format(base_station.name, e.message))

        # uptime
        try:
            sector_uptime = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                                       data_source='uptime').using(
                                                                       alias=bs_machine_name)[0].current_value
            pmp_bs_row['Sector Uptime'] = display_time(sector_uptime)
        except Exception as e:
            logger.info("Sector Uptime not exist for base station ({}).".format(base_station.name, e.message))

        # transmit power
        try:
            pmp_bs_row['TX Power'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                    data_source='transmit_power').using(
                                                                    alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("TX Power not exist for base station ({}).".format(base_station.name, e.message))

        # frequency
        try:
            pmp_bs_row['RX Power'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                    data_source='commanded_rx_power').using(
                                                                    alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("RX Power not exist for base station ({}).".format(base_station.name, e.message))

    # loop through circuits; if available to get inventory rows
    if circuits:

        for circuit in circuits:
            # sub station
            sub_station = circuit.sub_station

            # sub station device name
            ss_device_name = ""
            try:
                ss_device_name = sub_station.device.device_name
            except Exception as e:
                logger.info("PMP SS device not found. Exception: ", e.message)

            # ss device type
            ss_device_type = None
            try:
                ss_device_type = DeviceType.objects.get(id=sub_station.device.device_type).name
            except Exception as e:
                logger.info(e.message)

            # sub station machine
            ss_machine_name = ""
            try:
                ss_machine_name = sub_station.device.machine.name
            except Exception as e:
                logger.info("PMP SS machine not found. Exception: ", e.message)

            

            # customer
            customer = circuit.customer

            # ptp row dictionary
            pmp_sm_row = dict()

            # ********************************** Far End (PMP SM) ********************************

            # customer name
            try:
                pmp_sm_row['Customer Name'] = customer.alias
            except Exception as e:
                logger.info("Customer Name not exist for base station ({}).".format(sub_station.name, e.message))

            # circuit id
            try:
                pmp_sm_row['Circuit ID'] = circuit.circuit_id
            except Exception as e:
                logger.info("Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

            # site id
            try:
                pmp_sm_row['Site ID'] = base_station.bs_site_id
            except Exception as e:
                logger.info("Site ID not exist for base station ({}).".format(base_station.name, e.message))

            # ap ip
            try:
                pmp_sm_row['AP IP'] = sector.sector_configured_on.ip_address
            except Exception as e:
                logger.info("AP IP not exist for base station ({}).".format(base_station.name, e.message))

            # ss ip
            try:
                pmp_sm_row['SS IP'] = sub_station.device.ip_address
            except Exception as e:
                logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

            # qos bandwidth
            try:
                pmp_sm_row['QOS (BW)'] = circuit.qos_bandwidth
            except Exception as e:
                logger.info("QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

            # latitude
            try:
                pmp_sm_row['Latitude'] = sub_station.latitude
            except Exception as e:
                logger.info("Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # longitude
            try:
                pmp_sm_row['Longitude'] = sub_station.longitude
            except Exception as e:
                logger.info("Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # mac address
            try:
                pmp_sm_row['MAC'] = sub_station.mac_address
            except Exception as e:
                logger.info("MAC not exist for sub station ({}).".format(sub_station.name, e.message))

            # building height
            try:
                pmp_sm_row['Building Height'] = sub_station.building_height
            except Exception as e:
                logger.info("Building Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # tower/pole height
            try:
                pmp_sm_row['Tower/Pole Height'] = sub_station.tower_height
            except Exception as e:
                logger.info("Tower/Pole Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna height
            try:
                pmp_sm_row['Antenna Height'] = sub_station.antenna.height
            except Exception as e:
                logger.info("Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna beamwidth
            try:
                pmp_sm_row['Antenna Beamwidth'] = sub_station.antenna.beam_width
            except Exception as e:
                logger.info("Antenna Beamwidth not exist for sub station ({}).".format(sub_station.name, e.message))

            # polarization
            try:
                pmp_sm_row['Polarization'] = sub_station.antenna.polarization
            except Exception as e:
                logger.info("Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna type
            try:
                pmp_sm_row['Antenna Type'] = sub_station.antenna.antenna_type
            except Exception as e:
                logger.info("Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss mount type
            try:
                pmp_sm_row['SS Mount Type'] = sub_station.antenna.mount_type
            except Exception as e:
                logger.info("SS Mount Type not exist for sub station ({}).".format(sub_station.name, e.message))

            # ethernet extender
            try:
                pmp_sm_row['Ethernet Extender'] = sub_station.ethernet_extender
            except Exception as e:
                logger.info("Ethernet Extender not exist for sub station ({}).".format(sub_station.name, e.message))

            # cable length
            try:
                pmp_sm_row['Cable Length'] = sub_station.cable_length
            except Exception as e:
                logger.info("Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

            # rssi during acceptance
            try:
                pmp_sm_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
            except Exception as e:
                logger.info("RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                            e.message))

            # cinr during acceptance
            try:
                pmp_sm_row['CINR During Acceptance'] = circuit.dl_cinr_during_acceptance
            except Exception as e:
                logger.info("CINR During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                            e.message))

            # Customer Address
            try:
                pmp_sm_row['Customer Address'] = customer.address
            except Exception as e:
                logger.info("Customer Address not exist for sub station ({}).".format(sub_station.name, e.message))

            # date of acceptance
            try:
                pmp_sm_row['Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
            except Exception as e:
                logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                         e.message))

            # ************************************* SS Perf Parameters **********************************
            # pl
            pl = ""
            try:
                pl = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                  data_source='pl').using(
                                                  alias=ss_machine_name)[0].current_value
                pmp_sm_row['PD'] = pl
            except Exception as e:
                logger.info("PD not exist for sub station ({}).".format(sub_station.name, e.message))

            # latency
            try:
                pmp_sm_row['Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                     data_source='rta').using(
                                                                     alias=ss_machine_name)[0].current_value
            except Exception as e:
                logger.info("Latency not exist for sub station ({}).".format(sub_station.name, e.message))

            if pl != "100":
                # frequency
                try:
                    pmp_sm_row['Frequency'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl rssi
                try:
                    pmp_sm_row['RSSI DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='dl_rssi').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul rssi
                try:
                    pmp_sm_row['RSSI UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='ul_rssi').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl jitter
                try:
                    pmp_sm_row['Jitter DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_jitter').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Jitter DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul jitter
                try:
                    pmp_sm_row['Jitter UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_jitter').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Jitter UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # transmit power
                try:
                    pmp_sm_row['Transmit Power'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                  data_source='transmit_power').using(
                                                                                  alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Transmit Power not exist for sub station ({}).".format(sub_station.name, e.message))

                # polles ss ip
                try:
                    pmp_sm_row['Polled SS IP'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='ss_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss mac
                try:
                    pmp_sm_row['Polled SS MAC'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                 data_source='ss_mac').using(
                                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled bs ip
                try:
                    pmp_sm_row['Polled BS IP'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='bs_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled BS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polles bs mac
                try:
                    if ss_device_name == "Radwin5KSS":
                        pmp_sm_row['Polled BS MAC'] = InventoryStatus.objects.filter(
                            device_name=ss_device_name,
                            service_name="rad5k_ss_conn_bs_ip_invent",
                            data_source='bs_ip').using(
                            alias=ss_machine_name)[0].current_value
                    else:
                        pmp_sm_row['Polled BS MAC'] = InventoryStatus.objects.filter(
                            device_name=ss_device_name,
                            data_source='ss_connected_bs_mac').using(
                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled BS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # uptime
                try:
                    if ss_device_name == "Radwin5KSS":
                        session_uptime = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                      service_name='rad5k_ss_session_uptime_invent',
                                                                      data_source='session_uptime').using(
                                                                      alias=ss_machine_name)[0].current_value
                        pmp_sm_row['Session Uptime'] = display_time(session_uptime)
                    else:
                        session_uptime = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                      service_name='cambium_session_uptime_system',
                                                                      data_source='uptime').using(
                                                                      alias=ss_machine_name)[0].current_value
                        pmp_sm_row['Session Uptime'] = display_time(session_uptime)

                except Exception as e:
                    logger.info("Session Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # dl utilization
                try:
                    if ss_device_name == "Radwin5KSS":
                        pmp_sm_row['Utilization DL'] = ServiceStatus.objects.filter(
                            device_name=ss_device_name,
                            service_name='rad5k_ss_dl_utilization',
                            data_source='dl_utilization').using(
                            alias=ss_machine_name)[0].current_value
                    else:
                        pmp_sm_row['Utilization DL'] = ServiceStatus.objects.filter(
                            device_name=ss_device_name,
                            service_name='cambium_ss_dl_utilization',
                            data_source='dl_utilization').using(
                            alias=ss_machine_name)[0].current_value

                except Exception as e:
                    logger.info("Utilization DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ul utilization
                try:
                    if ss_device_name == "Radwin5KSS":
                        pmp_sm_row['Utilization UL'] = ServiceStatus.objects.filter(
                            device_name=ss_device_name,
                            service_name='rad5k_ss_ul_utilization',
                            data_source='ul_utilization').using(
                            alias=ss_machine_name)[0].current_value
                    else:
                        pmp_sm_row['Utilization UL'] = ServiceStatus.objects.filter(
                            device_name=ss_device_name,
                            service_name='cambium_ss_ul_utilization',
                            data_source='ul_utilization').using(
                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # auto negotiation
                try:
                    pmp_sm_row['Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                           data_source='autonegotiation').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Auto Negotiation not exist for sub station ({}).".format(sub_station.name, e.message))

                # duplex
                try:
                    pmp_sm_row['Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                 data_source='duplex').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # speed
                try:
                    pmp_sm_row['Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                data_source='ss_speed').using(
                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # link state
                try:
                    pmp_sm_row['Link'] = Status.objects.filter(device_name=ss_device_name,
                                                               data_source='link_state').using(
                                                               alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Link not exist for sub station ({}).".format(sub_station.name, e.message))

            # append 'pmp_bs_row' dictionary in 'pmp_bs_rows'
            pmp_bs_rows.append(pmp_bs_row)

            # append 'pmp_sm_row' dictionary in 'pmp_sm_rows'
            pmp_sm_rows.append(pmp_sm_row)
    else :
        # append 'pmp_bs_row' dictionary in 'pmp_bs_rows'
        pmp_bs_rows.append(pmp_bs_row)

    # insert 'pmp bs' rows in result dictionary
    result['pmp_bs'] = pmp_bs_rows if pmp_bs_rows else ""

    # insert 'pmp sm' rows in result dictionary
    result['pmp_sm'] = pmp_sm_rows if pmp_sm_rows else ""

    return result


def get_selected_wimax_inventory(base_station, sector):
    # result dictionary (contains ptp and ptp bh inventory)
    result = dict()

    # base station device name
    bs_device_name = ""
    try:
        bs_device_name = sector.sector_configured_on.device_name
    except Exception as e:
        logger.info("BS Device not exist. Exception: ", e.message)

    # base station machine
    bs_machine_name = ""
    try:
        bs_machine_name = sector.sector_configured_on.machine.name
    except Exception as e:
        logger.info("BS Machine not found.  Exception: ", e.message)

    # wimax bs rows list
    wimax_bs_rows = list()

    # wimax ss rows list
    wimax_ss_rows = list()
    
    # backhaul
    backhaul = base_station.backhaul

    # circuits associated with current sector
    circuits = sector.circuit_set.all()

    # ptp row dictionary
    wimax_bs_row = dict()

    # *********************************** Near End (Wimax BS) *********************************
    # state
    try:
        wimax_bs_row['State'] = base_station.state.state_name
    except Exception as e:
        logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

    # city
    try:
        wimax_bs_row['City'] = base_station.city.city_name
    except Exception as e:
        logger.info("City not exist for base station ({}).".format(base_station.name, e.message))

    # address
    try:
        wimax_bs_row['Address'] = base_station.address
    except Exception as e:
        logger.info("Address not exist for base station ({}).".format(base_station.name, e.message))

    # address
    try:
        wimax_bs_row['Site ID'] = base_station.bs_site_id
    except Exception as e:
        logger.info("Site ID not exist for base station ({}).".format(base_station.name, e.message))

    # bs name
    try:
        wimax_bs_row['BS Name'] = base_station.alias
    except Exception as e:
        logger.info("BS Name not exist for base station ({}).".format(base_station.name, e.message))

    # type of bs (technology)
    try:
        wimax_bs_row['Type Of BS (Technology)'] = base_station.bs_type
    except Exception as e:
        logger.info("Type Of BS (Technology) not exist for base station ({}).".format(base_station.name,
                                                                                      e.message))

    # site type
    try:
        wimax_bs_row['Site Type'] = base_station.bs_site_type
    except Exception as e:
        logger.info("Site Type not exist for base station ({}).".format(base_station.name, e.message))

    # infra provider
    try:
        wimax_bs_row['Infra Provider'] = base_station.infra_provider
    except Exception as e:
        logger.info("Infra Provider not exist for base station ({}).".format(base_station.name, e.message))

    # building height
    try:
        wimax_bs_row['Building Height'] = base_station.building_height
    except Exception as e:
        logger.info("Building Height not exist for base station ({}).".format(base_station.name, e.message))

    # tower height
    try:
        wimax_bs_row['Tower Height'] = base_station.tower_height
    except Exception as e:
        logger.info("Tower Height not exist for base station ({}).".format(base_station.name, e.message))

    # latitude
    try:
        wimax_bs_row['Latitude'] = base_station.latitude
    except Exception as e:
        logger.info("Latitude not exist for base station ({}).".format(base_station.name, e.message))

    # longitude
    try:
        wimax_bs_row['Longitude'] = base_station.longitude
    except Exception as e:
        logger.info("Longitude not exist for base station ({}).".format(base_station.name, e.message))

    # idu ip
    try:
        wimax_bs_row['IDU IP'] = sector.sector_configured_on.ip_address
    except Exception as e:
        logger.info("IDU IP not exist for base station ({}).".format(base_station.name, e.message))

    # vendor
    try:
        wimax_bs_row['Vendor'] = DeviceVendor.objects.get(id=sector.sector_configured_on.device_vendor).alias
    except Exception as e:
        logger.info("IDU Vendor not exist for base station ({}).".format(base_station.name, e.message))

    # sector name
    try:
        wimax_bs_row['Sector Name'] = sector.alias
    except Exception as e:
        logger.info("Sector Name not exist for base station ({}).".format(base_station.name, e.message))

    # make of antenna
    try:
        wimax_bs_row['Make Of Antenna'] = sector.antenna.make_of_antenna
    except Exception as e:
        logger.info("Make Of Antenna not exist for base station ({}).".format(base_station.name,
                                                                              e.message))

    # polarization
    try:
        wimax_bs_row['Polarization'] = sector.antenna.polarization
    except Exception as e:
        logger.info("Polarization not exist for base station ({}).".format(base_station.name, e.message))

    # antenna tilt
    try:
        wimax_bs_row['Antenna Tilt'] = sector.antenna.tilt
    except Exception as e:
        logger.info("Antenna Tilt not exist for base station ({}).".format(base_station.name, e.message))

    # antenna height
    try:
        wimax_bs_row['Antenna Height'] = sector.antenna.height
    except Exception as e:
        logger.info("Antenna Height not exist for base station ({}).".format(base_station.name, e.message))

    # antenna beamwidth
    try:
        wimax_bs_row['Antenna Beamwidth'] = sector.antenna.beam_width
    except Exception as e:
        logger.info("Antenna Beamwidth not exist for base station ({}).".format(base_station.name, e.message))

    # azimuth
    try:
        wimax_bs_row['Azimuth'] = sector.antenna.azimuth_angle
    except Exception as e:
        logger.info("Azimuth not exist for base station ({}).".format(base_station.name, e.message))

    # installation of splitter
    try:
        wimax_bs_row['Installation Of Splitter'] = sector.antenna.sync_splitter_used
    except Exception as e:
        logger.info("Installation Of Splitter not exist for base station ({}).".format(base_station.name, e.message))

    # type of gps
    try:
        wimax_bs_row['Type Of GPS'] = base_station.gps_type
    except Exception as e:
        logger.info("Type Of GPS not exist for base station ({}).".format(base_station.name, e.message))

    # bs switch ip
    try:
        wimax_bs_row['BS Switch IP'] = base_station.bs_switch.ip_address
    except Exception as e:
        logger.info("BS Switch IP not exist for base station ({}).".format(base_station.name, e.message))

    # aggregation switch
    try:
        wimax_bs_row['Aggregation Switch'] = backhaul.aggregator.ip_address
    except Exception as e:
        logger.info("Aggregation Switch not exist for base station ({}).".format(base_station.name,
                                                                                 e.message))

    # aggregation switch port
    try:
        wimax_bs_row['Aggregation Switch Port'] = backhaul.aggregator_port_name
    except Exception as e:
        logger.info("Aggregation Switch Port not exist for base station ({}).".format(base_station.name,
                                                                                      e.message))

    # bs converter ip
    try:
        wimax_bs_row['BS Converter IP'] = backhaul.bh_switch.ip_address
    except Exception as e:
        logger.info("State not exist for base station ({}).".format(base_station.name, e.message))

    # pop converter ip
    try:
        wimax_bs_row['POP Converter IP'] = backhaul.pop.ip_address
    except Exception as e:
        logger.info("POP Converter IP not exist for base station ({}).".format(base_station.name,
                                                                               e.message))

    # converter type
    try:
        wimax_bs_row['Converter Type'] = DeviceType.objects.get(pk=backhaul.bh_switch.device_type).alias
    except Exception as e:
        logger.info("Converter Type not exist for base station ({}).".format(base_station.name, e.message))

    # bh configured switch or converter
    try:
        wimax_bs_row['BH Configured On Switch/Converter'] = backhaul.bh_configured_on.ip_address
    except Exception as e:
        logger.info("BH Configured On Switch/Converter not exist for base station ({}).".format(
            base_station.name,
            e.message))

    # bh configured switch or converter port
    try:
        wimax_bs_row['Switch/Converter Port'] = backhaul.bh_port_name
    except Exception as e:
        logger.info("Switch/Converter Port not exist for base station ({}).".format(base_station.name,
                                                                                    e.message))

    # bh capacity
    try:
        wimax_bs_row['BH Capacity'] = backhaul.bh_capacity
    except Exception as e:
        logger.info("BH Capacity not exist for base station ({}).".format(base_station.name, e.message))

    # bh offnet/onnet
    try:
        wimax_bs_row['BH Offnet/Onnet'] = backhaul.bh_connectivity
    except Exception as e:
        logger.info("BH Offnet/Onnet not exist for base station ({}).".format(base_station.name, e.message))

    # backhaul type
    try:
        wimax_bs_row['Backhaul Type'] = backhaul.bh_type
    except Exception as e:
        logger.info("Backhaul Type not exist for base station ({}).".format(base_station.name, e.message))

    # bh circuit id
    try:
        wimax_bs_row['BH Circuit ID'] = backhaul.bh_circuit_id
    except Exception as e:
        logger.info("BH Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

    # pe hostname
    try:
        wimax_bs_row['PE Hostname'] = backhaul.pe_hostname
    except Exception as e:
        logger.info("PE Hostname not exist for base station ({}).".format(base_station.name, e.message))

    # pe ip
    try:
        wimax_bs_row['PE IP'] = backhaul.pe_ip
    except Exception as e:
        logger.info("PE IP not exist for base station ({}).".format(base_station.name, e.message))

    # bso circuit id
    try:
        wimax_bs_row['BSO Circuit ID'] = backhaul.ttsl_circuit_id
    except Exception as e:
        logger.info("BSO Circuit ID not exist for base station ({}).".format(base_station.name, e.message))

    # dr site
    try:
        wimax_bs_row['DR Site'] = sector.dr_site
    except Exception as e:
        logger.info("DR Site not exist for base station ({}).".format(base_station.name, e.message))

    # sector id
    try:
        wimax_bs_row['Sector ID'] = sector.sector_id
    except Exception as e:
        logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

    # pmp
    try:
        wimax_bs_row['PMP'] = sector.name.split("_")[-1]
    except Exception as e:
        logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

    # sector id
    try:
        wimax_bs_row['Sector ID'] = sector.sector_id
    except Exception as e:
        logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

    # dr site master/slave
    if sector.dr_site.lower() == "yes":
        wimax_bs_row['DR Master/Slave'] = "Master"
    else:
        wimax_bs_row['DR Master/Slave'] = ""

    # ************************************* BS Perf Parameters **********************************
    # pl
    pl = ""
    try:
        pl = NetworkStatus.objects.filter(device_name=bs_device_name,
                                          data_source='pl').using(
                                          alias=bs_machine_name)[0].current_value
        wimax_bs_row['PD'] = pl
    except Exception as e:
        logger.info("PD not exist for base station ({}).".format(base_station.name, e.message))

    # latency
    try:
        wimax_bs_row['Latency'] = NetworkStatus.objects.filter(device_name=bs_device_name,
                                                               data_source='rta').using(
            alias=bs_machine_name)[0].current_value
    except Exception as e:
        logger.info("Latency not exist for base station ({}).".format(base_station.name, e.message))

    if pl != "100":
        # sector utilization
        try:
            # by splitting last string after underscore from sector name; we get pmp port number
            if sector.name.split("_")[-1] == '1':
                wimax_bs_row['Sector Utilization DL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp1_dl_util_bgp').using(
                    alias=bs_machine_name)[0].current_value

                wimax_bs_row['Sector Utilization UL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp1_ul_util_bgp').using(
                    alias=bs_machine_name)[0].current_value
                wimax_bs_row['Frequency'] = InventoryStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp1_frequency_invent',
                    data_source='frequency').using(
                    alias=bs_machine_name)[0].current_value
            elif sector.name.split("_")[-1] == '2':
                wimax_bs_row['Sector Utilization DL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp2_dl_util_bgp').using(
                    alias=bs_machine_name)[0].current_value
                wimax_bs_row['Sector Utilization UL'] = ServiceStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp2_ul_util_bgp').using(
                    alias=bs_machine_name)[0].current_value
                wimax_bs_row['Frequency'] = InventoryStatus.objects.filter(
                    device_name=bs_device_name,
                    service_name='wimax_pmp2_frequency_invent',
                    data_source='frequency').using(
                    alias=bs_machine_name)[0].current_value
            else:
                pass
        except Exception as e:
            logger.info("Sector Utilization DL/UL or Frequecy not exist for base station ({}).".format(
                base_station.name,
                e.message))

        # mrc
        try:
            # by splitting last string after underscore from sector name; we get pmp port number
            if sector.name.split("_")[-1] == '1':
                wimax_bs_row['MRC'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='pmp1_mrc').using(
                                                                     alias=bs_machine_name)[0].current_value
            elif sector.name.split("_")[-1] == '2':
                wimax_bs_row['MRC'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                     data_source='pmp2_mrc').using(
                                                                     alias=bs_machine_name)[0].current_value
            else:
                pass
        except Exception as e:
            logger.info("MRC not exist for base station ({}).".format(base_station.name, e.message))

        # idu type
        try:
            wimax_bs_row['IDU Type'] = InventoryStatus.objects.filter(device_name=bs_device_name,
                                                                      data_source='idu_type').using(
                                                                      alias=bs_machine_name)[0].current_value
        except Exception as e:
            logger.info("IDU Type not exist for base station ({}).".format(base_station.name, e.message))

        # system uptime
        try:
            system_uptime = ServiceStatus.objects.filter(device_name=bs_device_name,
                                                         service_name='wimax_bs_uptime',
                                                         data_source='uptime').using(
                                                         alias=bs_machine_name)[0].current_value
            wimax_bs_row['System Uptime'] = display_time(system_uptime)
        except Exception as e:
            logger.info("System Uptime not exist for base station ({}).".format(base_station.name, e.message))

    # loop through circuits; if available to get inventory rows
    if circuits:
        for circuit in circuits:
            # sub station
            sub_station = circuit.sub_station

            # sub station device name
            ss_device_name = ""
            try:
                ss_device_name = sub_station.device.device_name
            except Exception as e:
                logger.info("WiMAX SS device not found. Exception: ", e.message)

            # sub station machine
            ss_machine_name = ""
            try:
                ss_machine_name = sub_station.device.machine.name
            except Exception as e:
                logger.info("WiMAX SS machine not found. Exception: ", e.message)

            # customer
            customer = circuit.customer

            # ptp row dictionary
            wimax_ss_row = dict()

            # ********************************** Far End (Wimax SS) ********************************

            # customer name
            try:
                wimax_ss_row['Customer Name'] = customer.alias
            except Exception as e:
                logger.info("Customer Name not exist for base station ({}).".format(sub_station.name, e.message))

            # circuit id
            try:
                wimax_ss_row['Circuit ID'] = circuit.circuit_id
            except Exception as e:
                logger.info("Circuit ID not exist for sub station ({}).".format(sub_station.name, e.message))

            # sector id
            try:
                wimax_ss_row['Sector ID'] = sector.sector_id
            except Exception as e:
                logger.info("Sector ID not exist for base station ({}).".format(base_station.name, e.message))

            # ss ip
            try:
                wimax_ss_row['SS IP'] = sub_station.device.ip_address
            except Exception as e:
                logger.info("SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss vendor
            try:
                wimax_ss_row['Vendor'] = DeviceVendor.objects.get(id=sub_station.device.device_vendor).alias
            except Exception as e:
                logger.info("Vendor not exist for sub station ({}).".format(sub_station.name, e.message))

            # qos bandwidth
            try:
                wimax_ss_row['QOS (BW)'] = circuit.qos_bandwidth
            except Exception as e:
                logger.info("QOS (BW) not exist for sub station ({}).".format(sub_station.name, e.message))

            # latitude
            try:
                wimax_ss_row['Latitude'] = sub_station.latitude
            except Exception as e:
                logger.info("Latitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # longitude
            try:
                wimax_ss_row['Longitude'] = sub_station.longitude
            except Exception as e:
                logger.info("Longitude not exist for sub station ({}).".format(sub_station.name, e.message))

            # mac address
            try:
                wimax_ss_row['MAC'] = sub_station.device.mac_address
            except Exception as e:
                logger.info("MAC not exist for sub station ({}).".format(sub_station.name, e.message))

            # building height
            try:
                wimax_ss_row['Building Height'] = sub_station.building_height
            except Exception as e:
                logger.info("Building Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # tower/pole height
            try:
                wimax_ss_row['Tower/Pole Height'] = sub_station.tower_height
            except Exception as e:
                logger.info("Tower/Pole Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna height
            try:
                wimax_ss_row['Antenna Height'] = sub_station.antenna.height
            except Exception as e:
                logger.info("Antenna Height not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna beamwidth
            try:
                wimax_ss_row['Antenna Beamwidth'] = sub_station.antenna.beam_width
            except Exception as e:
                logger.info("Antenna Beamwidth not exist for sub station ({}).".format(sub_station.name, e.message))

            # polarization
            try:
                wimax_ss_row['Polarization'] = sub_station.antenna.polarization
            except Exception as e:
                logger.info("Polarization not exist for sub station ({}).".format(sub_station.name, e.message))

            # antenna type
            try:
                wimax_ss_row['Antenna Type'] = sub_station.antenna.antenna_type
            except Exception as e:
                logger.info("Antenna Type not exist for sub station ({}).".format(sub_station.name, e.message))

            # ss mount type
            try:
                wimax_ss_row['SS Mount Type'] = sub_station.antenna.mount_type
            except Exception as e:
                logger.info("SS Mount Type not exist for sub station ({}).".format(sub_station.name, e.message))

            # ethernet extender
            try:
                wimax_ss_row['Ethernet Extender'] = sub_station.ethernet_extender
            except Exception as e:
                logger.info("Ethernet Extender not exist for sub station ({}).".format(sub_station.name, e.message))

            # cable length
            try:
                wimax_ss_row['Cable Length'] = sub_station.cable_length
            except Exception as e:
                logger.info("Cable Length not exist for sub station ({}).".format(sub_station.name, e.message))

            # rssi during acceptance
            try:
                wimax_ss_row['RSSI During Acceptance'] = circuit.dl_rssi_during_acceptance
            except Exception as e:
                logger.info("RSSI During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                            e.message))

            # cinr during acceptance
            try:
                wimax_ss_row['CINR During Acceptance'] = circuit.dl_cinr_during_acceptance
            except Exception as e:
                logger.info("CINR During Acceptance not exist for sub station ({}).".format(sub_station.name,
                                                                                            e.message))

            # Customer Address
            try:
                wimax_ss_row['Customer Address'] = customer.address
            except Exception as e:
                logger.info("Customer Address not exist for sub station ({}).".format(sub_station.name, e.message))

            # date of acceptance
            try:
                wimax_ss_row['Date Of Acceptance'] = circuit.date_of_acceptance.strftime('%d/%b/%Y')
            except Exception as e:
                logger.info("Date Of Acceptance not exist for base station ({}).".format(base_station.name,
                                                                                         e.message))

            # ************************************* SS Perf Parameters **********************************
            # pl (packet loss)
            pl = ""
            try:
                pl = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                  data_source='pl').using(
                                                  alias=ss_machine_name)[0].current_value
                wimax_ss_row['PD'] = pl
            except Exception as e:
                logger.info("PD not exist for sub station ({}).".format(sub_station.name, e.message))

            # latency
            try:
                wimax_ss_row['Latency'] = NetworkStatus.objects.filter(device_name=ss_device_name,
                                                                       data_source='rta').using(
                                                                       alias=ss_machine_name)[0].current_value
            except Exception as e:
                logger.info("Latency not exist for sub station ({}).".format(sub_station.name, e.message))

            if pl != "100":
                # frequency
                try:
                    wimax_ss_row['Frequency'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                             service_name='wimax_ss_frequency',
                                                                             data_source='frequency').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Frequency not exist for sub station ({}).".format(sub_station.name, e.message))

                # sector id
                try:
                    # by splitting last string after underscore from sector name; we get pmp port number
                    if sector.name.split("_")[-1] == '1':
                        wimax_ss_row['Sector ID'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                        data_source='sector_id_pmp1').using(
                                                                        alias=ss_machine_name)[0].current_value
                    elif sector.name.split("_")[-1] == '2':
                        wimax_ss_row['Sector ID'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                        data_source='sector_id_pmp2').using(
                                                                        alias=ss_machine_name)[0].current_value
                    else:
                        pass
                except Exception as e:
                    logger.info("Sector ID not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss ip
                try:
                    wimax_ss_row['Polled SS IP'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                                data_source='ss_ip').using(
                                                                                alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS IP not exist for sub station ({}).".format(sub_station.name, e.message))

                # polled ss mac
                try:
                    wimax_ss_row['Polled SS MAC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                             data_source='ss_mac').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Polled SS MAC not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi dl
                try:
                    wimax_ss_row['RSSI DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_rssi').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # rssi ul
                try:
                    wimax_ss_row['RSSI UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_rssi').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("RSSI UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # cinr dl
                try:
                    wimax_ss_row['CINR DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='dl_cinr').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("CINR DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # cinr ul
                try:
                    wimax_ss_row['CINR UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                           data_source='ul_cinr').using(
                                                                           alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("CINR UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # intrf dl
                try:
                    wimax_ss_row['INTRF DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='dl_intrf').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("INTRF DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # intrf ul
                try:
                    wimax_ss_row['INTRF UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='ul_intrf').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("INTRF UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # ptx
                try:
                    wimax_ss_row['PTX'] = InventoryStatus.objects.filter(device_name=ss_device_name,
                                                                         data_source='ss_ptx').using(
                                                                         alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("PTX not exist for sub station ({}).".format(sub_station.name, e.message))

                # session uptime
                try:
                    system_uptime = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                  data_source='session_uptime').using(
                                                                  alias=ss_machine_name)[0].current_value
                    wimax_ss_row['Session Uptime'] = display_time(system_uptime)
                except Exception as e:
                    logger.info("Session Uptime not exist for sub station ({}).".format(sub_station.name, e.message))

                # device uptime
                try:
                    device_uptime = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                              data_source='uptime').using(
                                                              alias=ss_machine_name)[0].current_value
                    wimax_ss_row['Device Uptime'] = display_time(device_uptime)
                except Exception as e:
                    logger.info("Device Uptime  not exist for sub station ({}).".format(sub_station.name, e.message))

                # modulation dl fec
                try:
                    wimax_ss_row['Modulation DL FEC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='modulation_dl_fec').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Modulation DL FEC not exist for sub station ({}).".format(sub_station.name, e.message))

                # modulation ul fec
                try:
                    wimax_ss_row['Modulation UL FEC'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='modulation_ul_fec').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Modulation UL FEC not exist for sub station ({}).".format(sub_station.name, e.message))

                # utilization dl
                try:
                    wimax_ss_row['Utilization DL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='dl_utilization').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization DL not exist for sub station ({}).".format(sub_station.name, e.message))

                # utilization ul
                try:
                    wimax_ss_row['Utilization UL'] = ServiceStatus.objects.filter(device_name=ss_device_name,
                                                                            data_source='ul_utilization').using(
                                                                            alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Utilization UL not exist for sub station ({}).".format(sub_station.name, e.message))

                # auto negotiation
                try:
                    wimax_ss_row['Auto Negotiation'] = Status.objects.filter(device_name=ss_device_name,
                                                                             data_source='autonegotiation').using(
                                                                             alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Auto Negotiation not exist for sub station ({}).".format(sub_station.name, e.message))

                # duplex
                try:
                    wimax_ss_row['Duplex'] = Status.objects.filter(device_name=ss_device_name,
                                                                   data_source='duplex').using(
                                                                   alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Duplex not exist for sub station ({}).".format(sub_station.name, e.message))

                # speed
                try:
                    wimax_ss_row['Speed'] = Status.objects.filter(device_name=ss_device_name,
                                                                   data_source='ss_speed').using(
                                                                   alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Speed not exist for sub station ({}).".format(sub_station.name, e.message))

                # link
                try:
                    wimax_ss_row['Link'] = Status.objects.filter(device_name=ss_device_name,
                                                                 data_source='link_state').using(
                                                                 alias=ss_machine_name)[0].current_value
                except Exception as e:
                    logger.info("Link not exist for sub station ({}).".format(sub_station.name, e.message))

            # append 'wimax_bs_row' dictionary in 'wimax_bs_rows'
            wimax_bs_rows.append(wimax_bs_row)

            # *********************************** DR Site Handling ************************************
            if (sector.dr_site.lower() == "yes") and sector.dr_configured_on:
                try:
                    copy_bs_row = copy.deepcopy(wimax_bs_row)
                    copy_bs_row['IDU IP'] = sector.dr_configured_on.ip_address
                    copy_bs_row['DR Master/Slave'] = "Slave"
                    wimax_bs_rows.append(copy_bs_row)
                except Exception as e:
                    logger.info("DR Device not exist. Exception: ", e.message)

            # append 'wimax_ss_row' dictionary in 'wimax_ss_rows'
            wimax_ss_rows.append(wimax_ss_row)
    else:
        # append 'wimax_bs_row' dictionary in 'wimax_bs_rows'
        wimax_bs_rows.append(wimax_bs_row)

    # insert 'wimax bs' rows in result dictionary
    result['wimax_bs'] = wimax_bs_rows if wimax_bs_rows else ""

    # insert 'wimax ss' rows in result dictionary
    result['wimax_ss'] = wimax_ss_rows if wimax_ss_rows else ""

    return result


def remove_duplicate_dict_from_list(input_list=None):
    """ Remove duplicate dictionaries from list of dictionaries

        :Parameters:
            - 'input_list' (list) - list of dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            },
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]

        :Returns:
           - 'result_list' (list) - list of dictionaries containing unique dictionaries for e.g.
                                        [
                                            {
                                                'City': u'Kolkata',
                                                'AntennaHeight': 27.0,
                                                'BHCircuitID': u'COPF-5712',
                                                'PEIP': u'192.168.216.37',
                                                'TypeOfBS(Technology)': u'WIMAX',
                                                'Polarization': u'Vertical',
                                                'State': u'WestBengal',
                                                'InfraProvider': u'WTTIL',
                                                'Latitude': 22.572833333333,
                                                'SiteType': u'RTT',
                                                'PMP': u'1',
                                                'BHConfiguredOnSwitch/Converter': u'10.175.132.67',
                                                'TypeOfGPS': u'AQtime',
                                                'IDUIP': u'10.172.72.2',
                                                'Address': u'35,
                                                CollegeSt.Kolkata,
                                                NearCalcuttaMedicalCollegeHospital',
                                                'BHOffnet/Onnet': u'ONNET',
                                                'MakeOfAntenna': u'Xhat',
                                                'SectorName': u'1',
                                                'BSName': u'BBGanguly',
                                                'Longitude': 88.362472222222,
                                                'TowerHeight': 13.0,
                                                'Azimuth': 30.0,
                                                'AntennaTilt': 2.0,
                                                'BHCapacity': 1000L,
                                                'AggregationSwitchPort': u'Ring',
                                                'Switch/ConverterPort': u'Gi0/1',
                                                'DRSite': u'No',
                                                'BackhaulType': u'DarkFibre',
                                                'BSOCircuitID': None,
                                                'SectorID': u'00: 0A: 10: 09: 00: 61',
                                                'InstallationOfSplitter': None,
                                                'PEHostname': u'kk-tcn-tcn-mi01-rt01',
                                                'BSSwitchIP': u'10.175.132.67',
                                                'BuildingHeight': 18.0,
                                                'AntennaBeamwidth': 60.0
                                            }
                                        ]
    """

    # list of dictionaries to be returned as a result
    result_list = []

    # temporary set containing dictionaries values in tuples for e.g
    # set([((key, value), (key, value), (key, value)), ((key, value), (key, value), (key, value))]

    temp_set = set()

    # loop through input list (list of dictionaries which needs to be filtered)
    for d in input_list:
        # t is set of dictionary values tuple for e.g
        # ((key, value), (key, value), (key, value), (key, value))
        # (('City', u'Kolkata'), ('Antenna Height', 29.0), ('BH Circuit ID', u'COPF-571'), ('PE IP', u'192.168.216.37'))
        t = tuple(d.items())
        if t not in temp_set:
            # adding tuple 't' to 'temp_set'
            temp_set.add(t)
            # append dictionary 'd' to 'result_list'
            result_list.append(d)

    return result_list

# ********************************* END GIS INVENTORY DOWNLOAD **********************************
#################################################################################################
## TOPOLOGY UPDATE ##
#################################################################################################
from performance.models import Topology, InventoryStatus, ServiceStatus
# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway
from organization.models import Organization
from device.models import DeviceTechnology, SiteInstance
from inventory.models import Sector, Circuit, SubStation
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway
#The Django !!
from django.db.models import Count, Q


def get_organizations():
    """
    Get all the organizations in list format
    :return:
    """
    orgs = Organization.objects.filter().annotate(Count('id')).values_list('id',flat=True)
    list(orgs).sort() #just for fun
    return orgs


def get_devices(technology='WiMAX', rf_type=None, site_name=None):
    """

    :param technology:
    :return:
    """
    organizations = get_organizations()

    technology = DeviceTechnology.objects.get(name__icontains=technology).id

    required_columns = ['id',
                        'device_name',
                        'machine__name'
                        ]

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    if rf_type and rf_type == 'customer':
        network_devices = inventory_utils.organization_customer_devices(
            organizations=organizations,
            technology=technology
        )

    else:
        network_devices = inventory_utils.organization_network_devices(
            organizations=organizations,
            technology=technology
        )

    if site_name and SiteInstance.objects.filter(name=site_name).exists():
        return network_devices.filter(site_instance__name=site_name).values(*required_columns)

    return network_devices.values(*required_columns)


@task()
def get_topology(technology, rf_type=None, site_name=None):
    """
    Get the current topology per technology WiMAX/PMP
    :param technology:
    :return:
    """

    count = False
    sector_objects = Sector.objects.none()
    required_columns = [
        'id',
        'sector_id',
        'sector_configured_on'
    ]
    # network_devices = get_devices(technology, rf_type=rf_type, site_name=site_name)
    technology = DeviceTechnology.objects.get(name__icontains=technology).id
    
    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    if site_name and SiteInstance.objects.filter(name=site_name).exists():
        sector_objects = inventory_utils.organization_sectors(
            organization=None,
            technology=technology
        ).filter(sector_configured_on__site_instance__name=site_name)

    else:
        sector_objects = inventory_utils.organization_sectors(
            organization=None,
            technology=technology
        )

    all_sectors = sector_objects.values(*required_columns)

    sector_list = []
    for sector in all_sectors:
        sector_list.append(sector['sector_id'])
    sector_list = set(sector_list)  # unique sector ids

    #topology is now synced at the central database only. no need to creating topology
    topology = Topology.objects.filter(sector_id__in=sector_list)
    required_topology = topology.values('connected_device_ip', 'sector_id', 'connected_device_mac', 'mac_address', 'ip_address')

    sector_ips = topology.values_list('ip_address', flat=True).distinct()

    ss_macs = topology.values_list('connected_device_mac', flat=True).distinct()

    polled_sectors = sector_objects.filter(sector_id__in=topology.values_list('sector_id', flat=True))

    polled_circuits = Circuit.objects.select_related(
        'sub_station',
        'sub_station__device',
        'sector'
        ).filter(
            sub_station__in=SubStation.objects.filter(
                device__ip_address__in=topology.values_list('connected_device_ip', flat=True)
            )
        )

    # ss_mac_update_required = polled_circuits.exclude(
    #     Q(sub_station__mac_address__in=ss_macs)
    #     |
    #     Q(sub_station__device__mac_address__isnull=ss_macs)
    # )
    #
    # # ss with mac address as null
    # ss_null_mac = ss_mac_update_required.filter(
    #     Q(sub_station__mac_address__isnull=True)
    #     |
    #     Q(sub_station__device__mac_address__isnull=True)
    # )
    #
    # # circuits with no sectors connected
    # circuit_null_sector = polled_circuits.filter(
    #     sector__isnull=True
    # )

    polled_devices = Device.objects.filter(ip_address__in=sector_ips)  # just work with sector devices here
    # because the ss devices can be get directly with SS only

    if topology.exists() and polled_sectors.exists():  # evaluate the query set
        # # Create instance of 'NocoutUtilsGateway' class
        # nocout_utils = NocoutUtilsGateway()
        # index_this = topology
        # indexed_topology = nocout_utils.indexed_query_set(
        #     query_set=index_this,
        #     indexes=['sector_id', 'connected_device_ip'],
        #     values=['sector_id', 'connected_device_ip', 'connected_device_mac', 'mac_address', 'ip_address'],
        #     is_raw=False
        # )
        # ss_indexed_topology = nocout_utils.indexed_query_set(
        #     query_set=index_this,
        #     indexes=['connected_device_ip'],
        #     values=['sector_id', 'connected_device_ip', 'connected_device_mac', 'mac_address', 'ip_address'],
        #     is_raw=False
        # )
        # index_this = polled_sectors
        # sector_indexed_topology = nocout_utils.indexed_query_set(
        #     query_set=index_this,
        #     indexes=['sector_id'],
        #     values=['sector_id', 'id'],
        #     is_raw=False
        # )
        pass
    else:
        return False

    save_circuit_list = []
    save_device_list = []
    save_ss_list = []

    # for circuit in polled_circuits:
    #     required_index = (circuit.sector.sector_id, circuit.sub_station.device.ip_address)
    #     if required_index in indexed_topology:
    #         # that means there is no need to update a circuit
    #         continue
    #     # else the index is not present
    #     # so the circuit is required to be updated with new sector
    #     ss_ip_index = circuit.sub_station.device.ip_address
    #     if ss_ip_index in ss_indexed_topology:
    #         try:
    #             ss_indexed_sector_id = ss_indexed_topology[ss_ip_index][0]['sector_id']
    #             # this is a values list for sector object
    #             circuit.sector = sector_indexed_topology[ss_indexed_sector_id][0]
    #             save_circuit_list.append(circuit)
    #         except Exception as e:
    #             logger.exception(e)
    #             continue


    processed_mac = {}
    for topos in required_topology:
        if (topos['connected_device_mac']) and (topos['connected_device_mac'] not in processed_mac):
            processed_mac[topos['connected_device_mac']] = topos['connected_device_mac']
            ss_ip = topos['connected_device_ip']
            sector_id = topos['sector_id']
            sector_ip = topos['ip_address']
            try:
                circuit_obj = polled_circuits.select_related('sub_station',
                                                             'sub_station__device',
                                                             'sector'
                ).get(
                    sub_station__device__ip_address=ss_ip
                )
                ss_obj = circuit_obj.sub_station

                if topos['connected_device_mac'] and ss_obj.mac_address != topos['connected_device_mac']:
                    ss_obj.mac_address = topos['connected_device_mac']
                    #first resolve for ss
                    save_ss_list.append(ss_obj)
                    #first resolve for ss device
                    ss_device_obj = circuit_obj.sub_station.device
                    ss_device_obj.mac_address = topos['connected_device_mac']
                    save_device_list.append(ss_device_obj)

                sector_object = polled_sectors.get(sector_id=sector_id)

                if topos['mac_address']:
                    sector_device_obj = polled_devices.get(ip_address=sector_ip)
                    sector_device_obj.mac_address = topos['mac_address']
                    save_device_list.append(sector_device_obj)

                #resolve for circuit
                #circuit_obj = ss_obj.circuit_set.get()
                #if circuit_obj.sector.sector_id != sector_id:
                circuit_obj.sector = sector_object
                save_circuit_list.append(circuit_obj)

            except Exception as e:
                #ss object is not found
                #the issue might be that SS does not exists in the database
                #if there is no SS then do no care and continue for existing SS
                #or there are multiple SS on a single device
                #which is wrong in any case
                #or lastly there are multiple circuit on the SS which is again an inventory mistake
                continue
    g_jobs = list()

    if len(save_circuit_list):
        # SectorCapacityStatus.objects.bulk_create(bulk_create_scs)
        g_jobs.append(bulk_update_create.s(bulky=save_circuit_list, action='update'))

    if len(save_device_list):
        g_jobs.append(bulk_update_create.s(bulky=save_device_list, action='update'))

    if len(save_ss_list):
        g_jobs.append(bulk_update_create.s(bulky=save_ss_list, action='update'))

    if not len(g_jobs):
        return False

    job = group(g_jobs)
    result = job.apply_async()
    # for r in result.get():
    #     ret |= r
    return True


@task()
def topology_site_wise(technology):
    """
    this would create jobs per site wise. per technology wise. for WiMAX it would have nearly 1000 to 1500
    devices at a time
    which would reduce the CPU load, but will open up a lot of parallel processes

    :return: True if any of the task gets positive results else False
    """
    sites = SiteInstance.objects.all().values_list('name', flat=True)
    g_jobs = list()

    for site in sites:
        g_jobs.append(get_topology.s(technology=technology, rf_type=None, site_name=site))

    job = group(g_jobs)
    result = job.apply_async()

    # for r in result.get():
    #     ret |= r

    return True


@task(default_retry_delay=30, max_retries=2)
def bulk_update_create(bulky, action='update', model=None):
    """

    :param bulky: bulk object list
    :param action: create or update?
    :param model: model object
    :return:
    """
    logger.debug("####################################### bulky - {}".format(bulky))
    if bulky and len(bulky):

        if action == 'update':
            try:
                bulk_update_internal_no_save(bulky)
            except Exception as e:
                logger.debug("******************************** Update Error: {}".format(e.message))
                return False
            # for update_this in bulky:
            #     try:
            #         update_this.save()
            #     except Exception as e:
            #         logger.exception(e)
            #         continue
            return True

        elif action == 'create':
            if model:
                try:
                    model.objects.bulk_create(bulky)
                except Exception as e:
                    logger.debug("******************************** Create Error: {}".format(e.message))
                    return False
            return True

    return True


# for updating in bulk we would use transactions
from django.db import transaction


@transaction.atomic()
def bulk_update_decorated(bulky):
    """

    :param bulky: model object list
    :return: True
    """
    sid = None
    for update_this in bulky:
        update_this.save()            # transaction is having an element
        sid = transaction.savepoint()
    transaction.savepoint_commit(sid)  # on loop exit commit
    return True


def bulk_update_internal(bulky):
    """

    :param bulky: model object list
    :return: True
    """
    sid = None
    with transaction.atomic():
        for update_this in bulky:
            update_this.save()
            sid = transaction.savepoint()
        transaction.savepoint_commit(sid)  # on loop exit commit
    return True


def bulk_update_internal_no_save(bulky):
    """

    :param bulky: model object list
    :return: True
    """
    with transaction.atomic():
        for update_this in bulky:
            update_this.save()
    return True


@task
def update_topology():
    """
    Update mapping of sector, sub station in circuit using topology.
    """
    logger.error('Update Topology - Started')
    # Radwin device technology.
    radwin5k_types = None
    try:
        radwin5k_types = DeviceType.objects.filter(name__icontains='radwin5k').values_list('id', flat=True)
    except Exception as e:
        pass

    # Radwin5K: Device mapper.
    radwin5k_devices = Device.objects.filter(
        device_type__in=set(radwin5k_types)
    ).values('ip_address', 'machine__name')

    # Radwin5K machines.
    radwin5k_machines = set(radwin5k_devices.values_list('machine__name', flat=True))

    # Radwin5K: Device IP and MAC Info.
    radwin5k_mac_info = []
    for machine in radwin5k_machines:
        temp_macs = InventoryStatus.objects.filter(
            ip_address__in=set(radwin5k_devices.filter(
                machine__name=machine
            ).values_list('ip_address', flat=True)),
            service_name__in=['rad5k_bs_mac_invent', 'rad5k_ss_mac_invent']
        ).values(
            'ip_address',
            'current_value'
        ).using(alias=machine)
        
        radwin5k_mac_info.extend(temp_macs)

    # Radwin5K: Device IP and MAC Mapper.
    radwin5k_mac_mapper = {}
    for row in radwin5k_mac_info:
        if row.get('ip_address') and row.get('ip_address') not in radwin5k_mac_mapper:
            radwin5k_mac_mapper[row['ip_address']] = row
        else:
            continue

    # MAC regex.
    mac_regex = "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"

    # Sector ID's from inventory.
    sector_ids = set(Sector.objects.filter(sector_id__isnull=False).values_list('sector_id', flat=True))

    # Sector ID's from topology.
    topo_sector_ids = list(set(Topology.objects.values_list('sector_id', flat=True)))

    # Radwin5K: Special case where sector id cannot be considered.
    radwin5k_topology = Topology.objects.filter(
        service_name="rad5k_topology_discover"
    ).values('connected_device_ip',
        'sector_id',
        'connected_device_mac',
        'mac_address',
        'ip_address'
    )

    # Radwin 5K: Sector configured on ip's.
    radwin5k_sector_ips = set(radwin5k_topology.values_list('ip_address', flat=True))

    # Radwin 5K: Sub station ip's.
    radwin5k_ss_ips = set(radwin5k_topology.values_list('connected_device_ip', flat=True))

    # Sectors & sub stations mapping from Topology.
    topology = Topology.objects.filter(
        Q(sector_id__in=topo_sector_ids) | Q(connected_device_ip__in=radwin5k_ss_ips)
    ).values(
        'connected_device_ip',
        'sector_id',
        'connected_device_mac',
        'mac_address',
        'ip_address'
    )

    # ################################### MAPPERS START #####################################

    # Sectors from Inventory corressponding to sector_id's fetched from Topology.
    sectors = Sector.objects.filter(sector_id__in=topo_sector_ids)

    # Sector ID's list.
    sector_ids = sectors.values_list('sector_id', flat=True)

    # SectorIP's list.
    sector_ips = sectors.values_list('sector_configured_on__ip_address', flat=True)

    dr_ips = sectors.values_list('dr_configured_on__ip_address', flat=True)

    # Sectors Mapper: {<sector_id> + <sector_configured_on__ip_address>: <sector object>, ....}
    sectors_mapper = {}
    for s_id, s_ip, dr_ip, obj in zip(sector_ids, sector_ips, dr_ips, sectors):
        if s_id and s_ip:
            key = s_id.strip().lower() + "|" + s_ip.strip()
            sectors_mapper[key] = obj
        if s_id and dr_ip:
            key = s_id.strip().lower() + "|" + dr_ip.strip()
            sectors_mapper[key] = obj

    # Radwin 5K sectors.
    radwin5k_sectors = Sector.objects.filter(
        Q(sector_id__isnull=False)
        &
        (
            Q(sector_configured_on__ip_address__in=radwin5k_sector_ips)
            |
            Q(dr_configured_on__ip_address__in=radwin5k_sector_ips)
        )
    )

    # Radwin 5K sector configured on ip's list.
    radwin5k_sector_ips = radwin5k_sectors.values_list('sector_configured_on__ip_address', flat=True)

    # Radwin 5K sectors Mapper: {<sector_configured_on__ip_address>: <sector object>, ....}
    radwin5k_sectors_mapper = {}
    for s_ip, obj in zip(radwin5k_sector_ips, radwin5k_sectors):
        if s_ip:
            key = s_ip.strip()
            radwin5k_sectors_mapper[key] = obj

    # BS devices corressponding to the sector_configured_on ip's from Topology.
    bs_devices = Device.objects.filter(ip_address__in=topology.values_list('ip_address', flat=True))

    # BS devices IP's list.
    bs_devices_ips = bs_devices.values_list('ip_address', flat=True)

    # BS Devices Mapper: {<sector_configured_on__ip_address>: <device object>, ....}
    bs_devices_mapper = {}
    for ip, bs_device in zip(bs_devices_ips, bs_devices):
        bs_devices_mapper[ip] = bs_device

    # Sectors & sub stations mapping from Circuit.
    circuits = Circuit.objects.filter(
        sub_station__device__ip_address__isnull=False,
        sector__sector_id__isnull=False
    ).select_related(
        'sub_station',
        'sub_station__device__ip_address',
        'sector__sector_id'
    ).order_by('name')

    # Sub Station devices IP's list corressponding to the connected_device_ip ip's.
    circuits_ss_ips = circuits.values_list('sub_station__device__ip_address', flat=True)

    # Circuit Mapper: {<sub_station__device__ip_address>: <circuit object>, ....}
    circuits_mapper = {}
    for ss_ip, circuit in zip(circuits_ss_ips, circuits):
        circuits_mapper[ss_ip] = circuit

    # ################################### MAPPERS END #######################################

    # Serialized sectors & sub stations mapping from Topology.
    serialized_topology = list(topology)

    # List of sectors & sub stations mapping from Topology.
    sectors_list = circuits.values(
        'sector__sector_id',
        'sub_station__device__ip_address',
        'sub_station__device__mac_address',
        'sector__sector_configured_on__ip_address',
        'sector__sector_configured_on__mac_address'
    )

    # Serialized sectors & sub stations mapping from Circuit.
    serialized_sectors_list = [{'connected_device_ip': a['sub_station__device__ip_address'],
                                'sector_id': a['sector__sector_id'],
                                'connected_device_mac': a['sub_station__device__mac_address'],
                                'mac_address': a['sector__sector_configured_on__mac_address'],
                                'ip_address': a['sector__sector_configured_on__ip_address']} for a in sectors_list]

    # Updated mapping.
    updated_mapping = compare_lists_of_dicts(serialized_sectors_list, serialized_topology)

    # Lists containing objects needs to be updated in database.
    update_ss_list = []
    update_device_list = []
    update_circuit_list = []
    # Update inventory from updated topology.
    for info in updated_mapping:
        # Get circuit from inventory.
        circuit = None
        sector = None
        ss = None
        ss_device = None
        sector_device = None
        try:
            circuit = circuits_mapper[info['connected_device_ip']]
        except Exception as e:
            continue

        if circuit:
            # Update sub station.
            try:
                ss = circuit.sub_station
                if radwin5k_mac_mapper.get(info['connected_device_ip']):
                    ss.mac_address = radwin5k_mac_mapper[info['connected_device_ip']]['current_value']
                else:
                    ss.mac_address = info['connected_device_mac']

                update_ss_list.append(ss)
            except Exception as e:
                pass
            # Update sub station device.
            try:
                ss_device = circuit.sub_station.device
                if radwin5k_mac_mapper.get(info['connected_device_ip']):
                    ss_device.mac_address = radwin5k_mac_mapper[info['connected_device_ip']]['current_value']
                else:
                    ss_device.mac_address = info['connected_device_mac']
                
                update_device_list.append(ss_device)
            except Exception as e:
                pass
            # Update sector device.
            try:
                sector_device = bs_devices_mapper[info['ip_address']]
                #if re.match(mac_regex, info['mac_address'].lower()):
                if radwin5k_mac_mapper.get(info['ip_address']):
                    sector_device.mac_address = radwin5k_mac_mapper[info['ip_address']]['current_value']
                else:
                    sector_device.mac_address = info['mac_address']
                
                update_device_list.append(sector_device)
            except Exception as e:
                logger.error('BS Device Exception -----')
                logger.error(e)
                logger.error('BS Device Exception -----')
                pass
            # Update circuit.
            try:
                if radwin5k_ss_ips.get(info['connected_device_ip']):
                    circuit.sector = radwin5k_sectors_mapper[info['ip_address'].strip()]
                else:
                    circuit.sector = sectors_mapper[info['sector_id'].strip().lower() + "|" + info['ip_address'].strip()]
                update_circuit_list.append(circuit)
            except Exception as e:
                pass

    g_jobs = list()

    if len(update_ss_list):
        g_jobs.append(bulk_update_create.s(bulky=update_ss_list, action='update'))

    if len(update_device_list):
        g_jobs.append(bulk_update_create.s(bulky=update_device_list, action='update'))

    if len(update_circuit_list):
        g_jobs.append(bulk_update_create.s(bulky=update_circuit_list, action='update'))

    if not len(g_jobs):
        return False

    job = group(g_jobs)
    result = job.apply_async()
    logger.error('Update Topology Task -------- END')
    return result


def compare_lists_of_dicts(list1, list2):
    check = set([(d['connected_device_ip'] if d['connected_device_ip'] else '',
                  d['sector_id'] if d['sector_id'] else '',
                  d['connected_device_mac'] if d['connected_device_mac'] else '',
                  d['mac_address'] if d['mac_address'] else '',
                  d['ip_address'] if d['ip_address'] else ''
                  ) for d in list1])

    return [d for d in list2 if (d['connected_device_ip'] if d['connected_device_ip'] else '',
                                 d['sector_id'] if d['sector_id'] else '',
                                 d['connected_device_mac'] if d['connected_device_mac'] else '',
                                 d['mac_address'] if d['mac_address'] else '',
                                 d['ip_address'] if d['ip_address'] else ''
                                 ) not in check]


@task()
def check_alarms_for_no_pps(alarm_type=None):
    """
    Check for 'Synchronization_problem__no_PPS' event in current_alarms & clear_alarms table
    """

    if alarm_type.lower() == 'current':
        current_model  = CurrentAlarms
        pps_flag = True
    elif alarm_type.lower() == 'clear':
        current_model  = ClearAlarms
        pps_flag = False
    else:
        return False

    ip_address_list = list(current_model.objects.filter(eventname='Synchronization_problem__no_PPS', is_active=1).using(TRAPS_DATABASE).values_list('ip_address', flat=True))
    wimax_tech_id = DeviceTechnology.objects.filter(name='WiMAX').values_list('id', flat=True)

    bs_id_list = Sector.objects.filter(sector_configured_on__ip_address__in=ip_address_list, sector_configured_on__device_technology__in=wimax_tech_id).values_list('base_station__id', flat=True)

    if bs_id_list.exists():
        try:
            BaseStation.objects.filter(id__in=bs_id_list).update(has_pps_alarm=pps_flag)
        except Exception, e:
            logger.error('Check Alarms Exception')
            logger.error(e)
        

    return True