from celery import task
from models import GISInventoryBulkImport
from machine.models import Machine
from site_instance.models import SiteInstance
from device.models import Device, DeviceTechnology
from inventory.models import Antenna, Backhaul, BaseStation, Sector, Customer, SubStation, Circuit
from device.models import State, City
from nocout.settings import MEDIA_ROOT
from IPy import IP
import os
import re
import time
import xlrd
import xlwt
import datetime
import logging

logger = logging.getLogger(__name__)

# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)


@task()
def validate_gis_inventory_excel_sheet(gis_obj_id, complete_d, sheet_name, keys_list, full_time, filename):
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
                        if not re.match(regex_alnum_comma_fslash, aggregation_switch_port.strip()):
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
                    if not re.match(regex_alnum_comma_fslash, switch_or_converter_port.strip()):
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

            # # 'date of acceptance' validation (must be like '15-Aug-2014')
            # try:
            #     if date_of_acceptance:
            #         try:
            #             datetime.datetime.strptime(date_of_acceptance, '%d-%b-%Y')
            #         except Exception as e:
            #             errors += 'Date Of Acceptance must be like (15-Aug-2014).\n'
            # except Exception as e:
            #     pass

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
                        if not re.match(regex_alnum_comma_fslash, hssu_port.strip()):
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
def bulk_upload_ptp_inventory(gis_id, organization, sheettype):
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
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)
    elif sheettype == 'invalid':
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.invalid_filename)
    else:
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    complete_d = list()

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

    try:
        for row in complete_d:
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

            # if bs ip and ss ip are same in inventory then skip it's insertion in database
            if all(k in row for k in ("IP", "SS IP")):
                if ip_sanitizer(row['IP']) == ip_sanitizer(row['SS IP']):
                    print "************************************ Sampe IP rows - ", row['IP'], row['SS IP']
                    continue

            try:
                # ----------------------------- Base Station Device ---------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'] if 'IP' in row.keys() else "")
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['IP']):
                    # base station data
                    base_station_data = {
                        'device_name': row['IP'] if 'IP' in row.keys() else "",
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
                else:
                    base_station = ""
            except Exception as e:
                base_station = ""

            try:
                # ----------------------------- Sub Station Device ---------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'])
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['SS IP']):
                    # sub station data
                    sub_station_data = {
                        'device_name': row['SS IP'] if 'SS IP' in row.keys() else "",
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
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------ Create BS Switch -----------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'])
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['BS Switch IP']):
                    # bs switch data
                    bs_switch_data = {
                        'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 7,
                        'device_vendor': 9,
                        'device_model': 12,
                        'device_type': 12,
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
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'])
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['Aggregation Switch']):
                    # aggregation switch data
                    aggregation_switch_data = {
                        'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 7,
                        'device_vendor': 9,
                        'device_model': 12,
                        'device_type': 12,
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
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'])
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['BS Converter IP']):
                    # bs converter data
                    bs_converter_data = {
                        'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
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
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine and site
                result = get_ptp_machine_and_site(row['IP'])
                machine = ""
                site = ""
                if 'machine' in result.keys():
                    machine = result['machine']
                if 'site' in result.keys():
                    site = result['site']

                if ip_sanitizer(row['POP Converter IP']):
                    # pop converter data
                    pop_converter_data = {
                        'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
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
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # sector antenna data
                sector_antenna_data = {
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
                # sub station antenna data
                substation_antenna_data = {
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
                    bh_configured_on = Device.objects.get(device_name=row['BH Configured On Switch/Converter'])
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
                # base station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['BS Name'] if 'BS Name' in row.keys() else "")

                try:
                    if all(k in row for k in ("City", "State")):
                        # concatinate city and state in bs name
                        name = "{}_{}_{}".format(name, row['City'][:3].lower() if 'City' in row.keys() else "",
                                                 row['State'][:3].lower() if 'State' in row.keys() else "")
                except Exception as e:
                    logger.info(e.message)

                print "************************** bs name - ", name
                alias = row['BS Name'] if 'BS Name' in row.keys() else ""
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'bs_switch': bs_switch,
                    'backhaul': backhaul,
                    'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                    'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
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
                if 'IP' in row.keys():
                    if ip_sanitizer(row['IP']):
                        # sector data
                        sector_data = {
                            'name': row['IP'] if 'IP' in row.keys() else "",
                            'alias': row['IP'] if 'IP' in row.keys() else "",
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
                # sub station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                alias = row['SS IP'] if 'SS IP' in row.keys() else ""
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
                # customer data
                # sanitize customer name
                name = special_chars_name_sanitizer(row['SS Customer Name'] if 'SS Customer Name' in row.keys() else "")
                alias = row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""

                try:
                    if 'SS Circuit ID' in row.keys():
                        # concatinate city and state in bs name
                        name = "{}_{}".format(name, special_chars_name_sanitizer(row['SS Circuit ID']))
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
                # sanitize circuit name
                name = special_chars_name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'SS Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['SS Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # circuit data
                alias = row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "",
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

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_ptp_bh_inventory(gis_id, organization, sheettype):
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
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)
    elif sheettype == 'invalid':
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.invalid_filename)
    else:
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    complete_d = list()

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

    try:
        for row in complete_d:
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

            # if bs ip and ss ip are same in inventory then skip it's insertion in database
            if all(k in row for k in ("IP", "SS IP")):
                if ip_sanitizer(row['IP']) == ip_sanitizer(row['SS IP']):
                    print "************************************ Sampe IP rows - ", row['IP'], row['SS IP']
                    continue

            try:
                # ----------------------------- Base Station Device ---------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                name = special_chars_name_sanitizer(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                if 'IP' in row.keys():
                    if ip_sanitizer(row['IP']):
                        # base station data
                        base_station_data = {
                            'device_name': name,
                            'device_alias': row['Circuit ID'] if 'Circuit ID' in row.keys() else "",
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
                    else:
                        base_station = ""
                else:
                    base_station = ""
            except Exception as e:
                base_station = ""

            try:
                # ----------------------------- Sub Station Device ---------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                name = special_chars_name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                if ip_sanitizer(row['SS IP']):
                    # sub station data
                    sub_station_data = {
                        'device_name': name,
                        'device_alias': row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "",
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
                else:
                    sub_station = ""
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------ Create BS Switch -----------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                if ip_sanitizer(row['BS Switch IP']):
                    # bs switch data
                    bs_switch_data = {
                        'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 7,
                        'device_vendor': 9,
                        'device_model': 12,
                        'device_type': 12,
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
                else:
                    bs_switch = ""
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                if ip_sanitizer(row['Aggregation Switch']):
                    # aggregation switch data
                    aggregation_switch_data = {
                        'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                        'organization': organization,
                        'machine': machine,
                        'site': site,
                        'device_technology': 7,
                        'device_vendor': 9,
                        'device_model': 12,
                        'device_type': 12,
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
                else:
                    aggregation_switch = ""
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                if ip_sanitizer(row['BS Converter IP']):
                    # bs converter data
                    bs_converter_data = {
                        'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
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
                else:
                    bs_converter = ""
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine and site
                machine = ""
                site = ""

                # get machine
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    logger.info(e.message)

                # get site
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    logger.info(e.message)

                if ip_sanitizer(row['POP Converter IP']):
                    # pop converter data
                    pop_converter_data = {
                        'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
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
                else:
                    pop_converter = ""
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # sector antenna data
                sector_antenna_data = {
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
                # sub station antenna data
                substation_antenna_data = {
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
                    bh_configured_on = Device.objects.get(device_name=row['BH Configured On Switch/Converter'])
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
                # base station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['BS Name'] if 'BS Name' in row.keys() else "")

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
                    'bs_switch': bs_switch,
                    'backhaul': backhaul,
                    'bh_bso': row['BH BSO'] if 'BH BSO' in row.keys() else "",
                    'hssu_used': row['HSSU Used'] if 'HSSU Used' in row.keys() else "",
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
                if 'IP' in row.keys():
                    if ip_sanitizer(row['IP']):
                        # sector data
                        sector_data = {
                            'name': row['IP'] if 'IP' in row.keys() else "",
                            'alias': row['IP'] if 'IP' in row.keys() else "",
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
                # sub station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")
                alias = row['SS IP'] if 'SS IP' in row.keys() else ""
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
                # customer data
                # sanitize customer name
                name = special_chars_name_sanitizer(row['SS Customer Name'] if 'SS Customer Name' in row.keys() else "")
                alias = row['SS Customer Name'] if 'SS Customer Name' in row.keys() else ""

                try:
                    if 'SS Circuit ID' in row.keys():
                        # concatinate city and state in bs name
                        name = "{}_{}".format(name, special_chars_name_sanitizer(row['SS Circuit ID']))
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
                # sanitize circuit name
                name = special_chars_name_sanitizer(row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'SS Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['SS Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # concatinating bs circuit id and ss circuit id
                if all(k in row for k in ("Circuit ID", "SS Circuit ID")):
                    circuit_id = "{}#{}".format(row['SS Circuit ID'], row['Circuit ID'])
                else:
                    circuit_id = row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""

                # circuit data
                alias = row['SS Circuit ID'] if 'SS Circuit ID' in row.keys() else ""
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

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_pmp_bs_inventory(gis_id, organization, sheettype):
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
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)
    elif sheettype == 'invalid':
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.invalid_filename)
    else:
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    complete_d = list()

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

    try:
        for row in complete_d:
            # initialize variables
            base_station = ""
            bs_switch = ""
            aggregation_switch = ""
            bs_converter = ""
            pop_converter = ""
            backhaul = ""
            basestation = ""
            sector = ""

            try:
                # ----------------------------- Base Station Device ---------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf1')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf1_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # base station data
                base_station_data = {
                    'device_name': row['ODU IP'] if 'ODU IP' in row.keys() else "",
                    'organization': organization,
                    'machine': machine,
                    'site': site,
                    'device_technology': 4,
                    'device_vendor': 4,
                    'device_model': 4,
                    'device_type': 6,
                    'ip': row['ODU IP'] if 'ODU IP' in row.keys() else "",
                    'mac': "",
                    'state': row['State'] if 'State' in row.keys() else "",
                    'city': row['City'] if 'City' in row.keys() else "",
                    'latitude': row['Latitude'] if 'Latitude' in row.keys() else "",
                    'longitude': row['Longitude'] if 'Longitude' in row.keys() else "",
                    'address': row['Address'] if 'Address' in row.keys() else "",
                    'description': 'Base Station created on {}.'.format(full_time)
                }
                # base station object
                base_station = create_device(base_station_data)
            except Exception as e:
                base_station = ""

            try:
                # ------------------------------ BS Switch -----------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf2')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf2_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # base station data
                bs_switch_data = {
                    'device_name': row['BS Switch IP'] if 'BS Switch IP' in row.keys() else "",
                    'organization': organization,
                    'machine': machine,
                    'site': site,
                    'device_technology': 7,
                    'device_vendor': 9,
                    'device_model': 12,
                    'device_type': 12,
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
            except Exception as e:
                bs_switch = ""

            try:
                # --------------------------- Aggregation Switch IP ---------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf3')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf3_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # aggregation switch data
                aggregation_switch_data = {
                    'device_name': row['Aggregation Switch'] if 'Aggregation Switch' in row.keys() else "",
                    'organization': organization,
                    'machine': machine,
                    'site': site,
                    'device_technology': 7,
                    'device_vendor': 9,
                    'device_model': 12,
                    'device_type': 12,
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
            except Exception as e:
                aggregation_switch = ""

            try:
                # -------------------------------- BS Converter IP ---------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf4')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf4_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # bs converter data
                bs_converter_data = {
                    'device_name': row['BS Converter IP'] if 'BS Converter IP' in row.keys() else "",
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
            except Exception as e:
                bs_converter = ""

            try:
                # -------------------------------- POP Converter IP ---------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf5')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf5_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # pop converter data
                pop_converter_data = {
                    'device_name': row['POP Converter IP'] if 'POP Converter IP' in row.keys() else "",
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
            except Exception as e:
                pop_converter = ""

            try:
                # ------------------------------- Sector Antenna -------------------------------
                # sector antenna data
                sector_antenna_data = {
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
                    bh_configured_on = Device.objects.get(device_name=row['BH Configured On Switch/Converter'])
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
                # base station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['BS Name'] if 'BS Name' in row.keys() else "")
                alias = row['BS Name'] if 'BS Name' in row.keys() else ""
                basestation_data = {
                    'name': name,
                    'alias': alias,
                    'bs_switch': bs_switch,
                    'bs_site_id': row['Site ID'] if 'Site ID' in row.keys() else "",
                    'bs_site_type': row['Site Type'] if 'Site Type' in row.keys() else "",
                    'bs_type': row['Type Of BS (Technology)'] if 'Type Of BS (Technology)' in row.keys() else "",
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
                # sector name
                name = ""
                if 'Sector Name' in row.keys():
                    name = "{}_{}".format(row['Sector Name'] if 'Sector Name' in row.keys() else "", row['ODU IP'] if 'ODU IP' in row.keys() else "")
                # sector data
                sector_data = {
                    'name': name,
                    'alias': row['Sector Name'] if 'Sector Name' in row.keys() else "",
                    'base_station': basestation,
                    'bs_technology': 4,
                    'sector_configured_on': base_station,
                    'antenna': sector_antenna,
                    'description': 'Sector created on {}.'.format(full_time)
                }

                # sector object
                sector = create_sector(sector_data)
            except Exception as e:
                sector = ""
        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


@task()
def bulk_upload_pmp_sm_inventory(gis_id, organization, sheettype):
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
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.valid_filename)
    elif sheettype == 'invalid':
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.invalid_filename)
    else:
        book = xlrd.open_workbook(MEDIA_ROOT + gis_bu_obj.invalid_filename)

    sheet = book.sheet_by_index(0)

    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols) if sheet.cell(0, col_index).value]
    keys_list = [x.encode('utf-8').strip() for x in keys]
    complete_d = list()

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

    try:
        for row in complete_d:
            # initialize variables
            # initialize variables
            sub_station = ""
            substation_antenna = ""
            sector = ""
            customer = ""
            circuit = ""

            try:
                # ----------------------------- Sub Station Device ---------------------------
                # get machine
                machine = ""
                try:
                    machine = Machine.objects.get(name='ospf1')
                except Exception as e:
                    machine = ""
                    logger.info(e.message)

                # get site_instance
                try:
                    site = SiteInstance.objects.get(name='ospf1_slave_1')
                except Exception as e:
                    site = ""
                    logger.info(e.message)

                # sub station data
                sub_station_data = {
                    'device_name': row['SS IP'] if 'SS IP' in row.keys() else "",
                    'organization': organization,
                    'machine': machine,
                    'site': site,
                    'device_technology': 4,
                    'device_vendor': 4,
                    'device_model': 5,
                    'device_type': 9,
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
            except Exception as e:
                sub_station = ""

            try:
                # ------------------------------- Sub Station Antenna -------------------------------
                # sub station antenna data
                substation_antenna_data = {
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
                # sub station data
                # sanitize bs name
                name = special_chars_name_sanitizer(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")
                alias = row['SS IP'] if 'SS IP' in row.keys() else ""
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
                # customer data
                # sanitize customer name
                name = special_chars_name_sanitizer(row['Customer Name'] if 'Customer Name' in row.keys() else "")
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

            try:
                # ------------------------------- Circuit -------------------------------
                # sanitize circuit name
                name = special_chars_name_sanitizer(row['Circuit ID'] if 'Circuit ID' in row.keys() else "")

                # validate date of acceptance
                if 'Date Of Acceptance' in row.keys():
                    date_of_acceptance = validate_date(row['Date Of Acceptance'])
                else:
                    date_of_acceptance = ""

                # circuit data
                alias = row['Circuit ID'] if 'Circuit ID' in row.keys() else ""
                circuit_data = {
                    'name': name,
                    'alias': alias,
                    'circuit_id': row['Circuit ID'] if 'Circuit ID' in row.keys() else "",
                    'sector': "",
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

        # updating upload status in 'GISInventoryBulkImport' model
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 2
        gis_obj.save()
    except Exception as e:
        gis_obj = GISInventoryBulkImport.objects.get(pk=gis_id)
        gis_obj.upload_status = 3
        gis_obj.save()


def create_device(device_payload):
    """ Create Device object

    Args:
        device_payload (dict): {
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

    # get device parameters
    if 'device_name' in device_payload.keys():
        device_name = device_payload['device_name'].encode('utf-8').strip() if device_payload['device_name'] else ""
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

    # update device if it exists in database
    if device_name:
        if device_name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING DEVICE -------------------------------
            try:
                # device object
                device = Device.objects.get(device_name=device_name, ip_address=ip_address)
                # device alias
                if device_alias:
                    try:
                        device.device_alias = device_alias
                    except Exception as e:
                        logger.info("Device Alias: ({} - {})".format(device_alias, e.message))
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
                        logger.info("Device Model: ({} - {})".format(device_model, e.message))
                # device type
                if device_type:
                    try:
                        device.device_type = device_type
                    except Exception as e:
                        logger.info("Device Type: ({} - {})".format(device_type, e.message))
                # parent
                try:
                    device.parent = Device.objects.all()[0]
                except Exception as e:
                    logger.info("Parent: ({})".format(e.message))
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
                if latitude and isinstance(latitude, float):
                    try:
                        device.latitude = latitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude and isinstance(longitude, float):
                    try:
                        device.longitude = longitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                device.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Device Update: State Not Found")
                        device.state = device_state_id
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Device Update: City Not Found")
                        else:
                            raise Exception("While Device Update: In City: State Not Found")
                        device.city = device_city_id
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
                # parent
                try:
                    device.parent = Device.objects.all()[0]
                except Exception as e:
                    logger.info("Parent: ({})".format(e.message))
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
                if latitude and isinstance(latitude, float):
                    try:
                        device.latitude = latitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude and isinstance(longitude, float):
                    try:
                        device.longitude = longitude
                    except Exception as e:
                        logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # timezone
                device.timezone = 'Asia/Kolkata'
                # country
                device.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Device Update: State Not Found")
                        device.state = device_state_id
                    except Exception as e:
                        logger.info("State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Device Update: City Not Found")
                        else:
                            raise Exception("While Device Update: In City: State Not Found")
                        device.city = device_city_id
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
    if 'ip' in antenna_payload.keys():
        name = antenna_payload['ip'] if antenna_payload['ip'] else ""
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
    bh_connectivity, bh_circuit_id, ttsl_circuit_id, dr_site, description = [''] * 5

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
    if 'bh_connectivity' in backhaul_payload.keys():
        bh_connectivity = backhaul_payload['bh_connectivity'] if backhaul_payload['bh_connectivity'] else ""
    if 'bh_circuit_id' in backhaul_payload.keys():
        bh_circuit_id = backhaul_payload['bh_circuit_id'] if backhaul_payload['bh_circuit_id'] else ""
    if 'bh_capacity' in backhaul_payload.keys():
        pobh_capacityp = backhaul_payload['bh_capacity'] if backhaul_payload['bh_capacity'] else ""
    if 'ttsl_circuit_id' in backhaul_payload.keys():
        ttsl_circuit_id = backhaul_payload['ttsl_circuit_id'] if backhaul_payload['ttsl_circuit_id'] else ""
    if 'dr_site' in backhaul_payload.keys():
        dr_site = backhaul_payload['dr_site'] if backhaul_payload['dr_site'] else ""
    if 'description' in backhaul_payload.keys():
        description = backhaul_payload['description'] if backhaul_payload['description'] else ""

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
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit IB: ({} - {})".format(ttsl_circuit_id, e.message))
                # dr site
                if dr_site:
                    try:
                        backhaul.dr_site = dr_site
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
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
                # ttsl circuit id
                if ttsl_circuit_id:
                    try:
                        backhaul.ttsl_circuit_id = ttsl_circuit_id
                    except Exception as e:
                        logger.info("BSO Circuit IB: ({} - {})".format(ttsl_circuit_id, e.message))
                # dr site
                if dr_site:
                    try:
                        backhaul.dr_site = dr_site
                    except Exception as e:
                        logger.info("DR Site: ({} - {})".format(dr_site, e.message))
                # description
                if description:
                    try:
                        backhaul.description = description
                    except Exception as e:
                        logger.info("Description: ({} - {})".format(description, e.message))
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
    name, alias, bs_site_id, bs_site_type, bs_switch, backhaul, bs_type, bh_bso, hssu_used = [''] * 9
    latitude, longitude, infra_provider, gps_type, building_height, tower_height, country, state, city = [''] * 9
    address, description = [''] * 2

    # get base station parameters
    if 'name' in basestation_payload.keys():
        name = basestation_payload['name'] if basestation_payload['name'] else ""
    if 'alias' in basestation_payload.keys():
        alias = basestation_payload['alias'] if basestation_payload['alias'] else ""
    if 'bs_site_id' in basestation_payload.keys():
        bs_site_id = basestation_payload['bs_site_id'] if basestation_payload['bs_site_id'] else ""
    if 'bs_site_type' in basestation_payload.keys():
        bs_site_type = basestation_payload['bs_site_type'] if basestation_payload['bs_site_type'] else ""
    if 'bs_switch' in basestation_payload.keys():
        bs_switch = basestation_payload['bs_switch'] if basestation_payload['bs_switch'] else ""
    if 'backhaul' in basestation_payload.keys():
        backhaul = basestation_payload['backhaul'] if basestation_payload['backhaul'] else ""
    if 'bs_type' in basestation_payload.keys():
        bs_type = basestation_payload['bs_type'] if basestation_payload['bs_type'] else ""
    if 'bh_bso' in basestation_payload.keys():
        bh_bso = basestation_payload['bh_bso'] if basestation_payload['bh_bso'] else ""
    if 'switch_port' in basestation_payload.keys():
        switch_port = basestation_payload['switch_port'] if basestation_payload['switch_port'] else ""
    if 'latitude' in basestation_payload.keys():
        latitude = basestation_payload['latitude'] if basestation_payload['latitude'] else ""
    if 'longitude' in basestation_payload.keys():
        longitude = basestation_payload['longitude'] if basestation_payload['longitude'] else ""
    if 'pop_port' in basestation_payload.keys():
        pop_port = basestation_payload['pop_port'] if basestation_payload['pop_port'] else ""
    if 'infra_provider' in basestation_payload.keys():
        infra_provider = basestation_payload['infra_provider'] if basestation_payload['infra_provider'] else ""
    if 'gps_type' in basestation_payload.keys():
        gps_type = basestation_payload['gps_type'] if basestation_payload['gps_type'] else ""
    if 'building_height' in basestation_payload.keys():
        building_height = basestation_payload['building_height'] if basestation_payload['building_height'] else ""
    if 'tower_height' in basestation_payload.keys():
        tower_height = basestation_payload['tower_height'] if basestation_payload['tower_height'] else ""
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

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
            # ---------------------------- UPDATING BASE STATION -----------------------------
            print "************************************ updating base station - ", name
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
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            basestation.latitude = latitude
                        except Exception as e:
                            logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            basestation.longitude = longitude
                        except Exception as e:
                            logger.info("Longitude: ({} - {})".format(longitude, e.message))
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
                # tower height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            basestation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                basestation.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Base Station Update: State Not Found")
                        basestation.state = device_state_id
                    except Exception as e:
                        logger.info("BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Base Station: City Not Found")
                        else:
                            raise Exception("While Base Station: In City: State Not Found")
                        basestation.city = device_city_id
                    except Exception as e:
                        logger.info("BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
                # saving base station
                basestation.save()
                return basestation
            except Exception as e:
                # ---------------------------- CREATING BASE STATION -------------------------------
                # create basestation if it doesn't exist in database
                print "************************************ create base station - ", name
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
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            basestation.latitude = latitude
                        except Exception as e:
                            logger.info("Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            basestation.longitude = longitude
                        except Exception as e:
                            logger.info("Longitude: ({} - {})".format(longitude, e.message))
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
                # tower height
                if tower_height:
                    if isinstance(tower_height, int) or isinstance(tower_height, float):
                        try:
                            basestation.tower_height = tower_height
                        except Exception as e:
                            logger.info("Tower Height: ({} - {})".format(tower_height, e.message))
                # country
                basestation.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Base Station Update: State Not Found")
                        basestation.state = device_state_id
                    except Exception as e:
                        logger.info("BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Base Station: City Not Found")
                        else:
                            raise Exception("While Base Station: In City: State Not Found")
                        basestation.city = device_city_id
                    except Exception as e:
                        logger.info("BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        basestation.address = address
                    except Exception as e:
                        logger.info("BS Address: ({} - {})".format(address, e.message))
                # description
                if description:
                    try:
                        basestation.description = description
                    except Exception as e:
                        logger.info("BS Description: ({} - {})".format(description, e.message))
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
    description = ''

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
    if 'modulation' in sector_payload.keys():
        modulation = sector_payload['modulation'] if sector_payload['modulation'] else ""
    if 'description' in sector_payload.keys():
        description = sector_payload['description'] if sector_payload['description'] else ""

    if name:
        if name not in ['NA', 'na', 'N/A', 'n/a']:
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

    # initializing variables
    name, alias, device, antenna, version, serial_no, building_height, tower_height, ethernet_extender = [''] * 9
    cable_length, latitude, longitude, mac_address, country, state, city, address, description = [''] * 9

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
                        substation.ethernet_extender = ethernet_extender
                    except Exception as e:
                        logger.info("Sub Station Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            substation.latitude = latitude
                        except Exception as e:
                            logger.info("Sub Station Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            substation.longitude = longitude
                        except Exception as e:
                            logger.info("Sub Station Longitude: ({} - {})".format(longitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                substation.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Base Station Insert: State Not Found")
                        substation.state = device_state_id
                    except Exception as e:
                        logger.info("Sub Station BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Base Station: City Not Found")
                        else:
                            raise Exception("While Base Station: In City: State Not Found")
                        substation.city = device_city_id
                    except Exception as e:
                        logger.info("Sub Station BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        substation.address = address
                    except Exception as e:
                        logger.info("Sub Station Address: ({})".format(e.message))
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
                        substation.ethernet_extender = ethernet_extender
                    except Exception as e:
                        logger.info("Sub Station Ethernet Extender: ({} - {})".format(ethernet_extender, e.message))
                # cable length
                if cable_length:
                    if isinstance(cable_length, int) or isinstance(cable_length, float):
                        try:
                            substation.cable_length = cable_length
                        except Exception as e:
                            logger.info("Sub Station Cable Length: ({} - {})".format(cable_length, e.message))
                # latitude
                if latitude:
                    if isinstance(latitude, int) or isinstance(latitude, float):
                        try:
                            substation.latitude = latitude
                        except Exception as e:
                            logger.info("Sub Station Latitude: ({} - {})".format(latitude, e.message))
                # longitude
                if longitude:
                    if isinstance(longitude, int) or isinstance(longitude, float):
                        try:
                            substation.longitude = longitude
                        except Exception as e:
                            logger.info("Sub Station Longitude: ({} - {})".format(longitude, e.message))
                # mac_address
                if mac_address:
                    try:
                        substation.mac_address = mac_address
                    except Exception as e:
                        logger.info("Sub Station MAC Address: ({} - {})".format(mac_address, e.message))
                # country
                substation.country = 1
                # state
                if state:
                    try:
                        device_state_id = get_state(state=state)#State.objects.get(state_name=state).id
                        if not device_state_id:
                            raise Exception("While Sub Station Insert: State Not Found")
                        substation.state = device_state_id
                    except Exception as e:
                        logger.info("Sub Station BS State: ({})".format(e.message))
                # city
                if city:
                    try:
                        if state:
                            device_city_id = get_city(state=state, city_name=city)#City.objects.get(city_name=city).id
                            if not device_city_id:
                                raise Exception("While Sub Station Insert: City Not Found")
                        else:
                            raise Exception("While Sub Station Insert: In City: State Not Found")
                        substation.city = device_city_id
                    except Exception as e:
                        logger.info("Sub Station BS City: ({})".format(e.message))
                # address
                if address:
                    try:
                        substation.address = address
                    except Exception as e:
                        logger.info("Sub Station Address: ({})".format(e.message))
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
    throughput_during_acceptance, date_of_acceptance, description = [''] * 3

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
                        circuit.dl_rssi_during_acceptance = dl_rssi_during_acceptance
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = dl_cinr_during_acceptance
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
                        circuit.dl_rssi_during_acceptance = dl_rssi_during_acceptance
                    except Exception as e:
                        logger.info("RSSI During Acceptance: ({} - {})".format(dl_rssi_during_acceptance, e.message))
                # dl cinr during acceptance
                if dl_cinr_during_acceptance:
                    try:
                        circuit.dl_cinr_during_acceptance = dl_cinr_during_acceptance
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
                try:
                    circuit.save()
                    return circuit
                except Exception as e:
                    logger.info("Circuit Object: ({} - {})".format(name, e.message))
                    return ""


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
            datetime.datetime.strptime(date_string, '%d-%b-%Y')
            date_string = date_string
        except Exception as e:
            date_string = ""
        return date_string


def special_chars_name_sanitizer(name):
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
    """

    :param state:
    :return:
    """
    if state:
        state_objects = State.objects.filter(state_name__icontains=state)
        if len(state_objects):
            return state_objects[0].id
    return None


def get_city(state=None, city_name=None):
    """

    :param state:
    :return:
    """
    if state and city_name:
        city_objects = City.objects.filter(city_name__icontains=city_name, state__state_name__icontains=state)
        if len(city_objects):
            return city_objects[0].id
    return None


def sanitize_mac_address(mac=None):
    mac = ''.join(e for e in mac if e.isalnum()).lower()
    if len(mac) == 12:
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    else:
        mac = ""

