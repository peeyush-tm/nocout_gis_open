from celery import task
from models import GISInventoryBulkImport
from device.models import State, City
import logging
import os
import re
import xlwt
import datetime

from nocout.settings import MEDIA_ROOT

# logger = logging.getLogger(__name__)

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

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
            azimuth_angles_list = range(0, 361)               # 0.......360
            building_height_list = range(0, 100)              # 0.......99
            tower_height_list = range(0, 100)                 # 0.......99
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
            gis_bulk_obj.valid_filename =  '/media/inventory_files/valid/{}_valid_{}.xls'.format(full_time, filename)
            gis_bulk_obj.invalid_filename = '/media/inventory_files/invalid/{}_invalid_{}.xls'.format(full_time, filename)
        except Exception as e:
            logger.exception(e.message)
        gis_bulk_obj.status = 1
        gis_bulk_obj.save()
        return gis_bulk_obj.original_filename
    except Exception as e:
        gis_bulk_obj = GISInventoryBulkImport.objects.get(pk=gis_obj_id)
        gis_bulk_obj.status = 2
        gis_bulk_obj.save()
        logger.exception(e.message)
