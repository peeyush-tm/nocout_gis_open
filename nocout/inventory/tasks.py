from celery import task
from models import GISInventoryBulkImport
import logging
import re
import xlwt

logger = logging.getLogger(__name__)


@task()
def validate_gis_inventory_excel_sheet(gis_obj_id, complete_d, sheet_name, keys_list):
    valid_rows_dicts = []
    invalid_rows_dicts = []
    valid_rows_lists = []
    invalid_rows_lists = []
    sheetname = sheet_name

    for d in complete_d:

        # wimax bs fields but common with pmp bs
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

        if 'Antenna Polarisation' in d.keys():
            antenna_polarization = d['Antenna Polarisation']

        if 'Antenna Tilt' in d.keys():
            antenna_tilt = int(d['Antenna Tilt']) if isinstance(d['Antenna Tilt'], float) else d['Antenna Tilt']

        if 'Antenna Height' in d.keys():
            antenna_height = d['Antenna Height']

        if 'Antenna Beamwidth' in d.keys():
            antenna_beamwidth = int(d['Antenna Beamwidth']) if isinstance(d['Antenna Beamwidth'], float) else d['Antenna Beamwidth']

        if 'Azimuth' in d.keys():
            azimuth = d['Azimuth']

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

        if 'DR Site' in d.keys():
            dr_site = d['DR Site']

        if 'TTSL Circuit ID' in d.keys():
            ttsl_circuit_id = d['TTSL Circuit ID']

        # wimax bs fields
        if 'PMP' in d.keys():
            pmp = int(d['PMP']) if isinstance(d['PMP'], float) else d['PMP']

        if 'Installation Of Splitter' in d.keys():
            installation_of_splitter = d['Installation Of Splitter']

        if 'IDU IP' in d.keys():
            idu_ip = d['IDU IP']

        # pmp bs fields
        if 'Sync Splitter Used' in d.keys():
            sync_splitter_used = d['Sync Splitter Used']

        if 'ODU IP' in d.keys():
            odu_ip = d['ODU IP']

        # wimax & pmp ss common fields
        if 'Customer Name' in d.keys():
            customer_name = d['Customer Name']

        if 'Circuit ID' in d.keys():
            ckt_id = d['Circuit ID']

        if 'QOS (BW)' in d.keys():
            qos_bw = d['QOS (BW)']

        if 'Tower/Pole Height' in d.keys():
            tower_pole_height = d['Tower/Pole Height']

        if 'Antenna Height' in d.keys():
            ss_antenna_height = d['Antenna Height']

        if 'Polarisation' in d.keys():
            polarization = d['Polarisation']

        if 'Antenna Type' in d.keys():
            antenna_type = d['Antenna Type']

        if 'SS Mount Type' in d.keys():
            ss_mount_type = d['SS Mount Type']

        if 'Ethernet Extender' in d.keys():
            ethernet_extender = d['Ethernet Extender']

        if 'Cable Length' in d.keys():
            cable_length = d['Cable Length']

        if 'DL RSSI During Acceptance' in d.keys():
            dl_rssi_during_acceptance = d['DL RSSI During Acceptance']

        if 'CINR During Acceptance' in d.keys():
            dl_cinr_during_acceptance = d['CINR During Acceptance']

        if 'Customer Address' in d.keys():
            customer_address = d['Customer Address']

        if 'Date Of Acceptance' in d.keys():
            date_of_acceptance = d['Date Of Acceptance']

        if 'SS IP' in d.keys():
            ss_ip = d['SS IP']

        # pmp sm fields
        if 'Lens/Reflector' in d.keys():
            lens_or_reflector = d['Lens/Reflector']

        # ptp bs fields
        if 'Circuit Type' in d.keys():
            circuit_type = d['Circuit Type']

        if 'BS Address' in d.keys():
            bs_address = d['BS Address']

        if 'Antenna Gain' in d.keys():
            antenna_gain = d['Antenna Gain']

        if 'Antenna Mount Type' in d.keys():
            antenna_mount_type = d['Antenna Mount Type']

        if 'RSSI During Acceptance' in d.keys():
            rssi_during_acceptance = d['RSSI During Acceptance']

        if 'Throughput During Acceptance' in d.keys():
            throughput_during_acceptance = d['Throughput During Acceptance']

        if 'BH BSO' in d.keys():
            bh_bso = d['BH BSO'] if d['BH BSO'] else ""

        if 'IP' in d.keys():
            ip = d['IP'] if d['IP'] else ""

        if 'MAC' in d.keys():
            mac = d['MAC'] if d['MAC'] else ""

        # ptp ss fields
        if 'MIMO/Diversity' in d.keys():
            mimo = d['MIMO/Diversity']

        # errors field for excel sheet validation errors
        errors = ""

        # dropdown lists
        types_of_bs_list = ['WIMAX', 'CAMBIUM', 'RADWIN']
        site_types_list = ['GBT', 'RTT', 'POLE']
        infra_provider_list = ['TVI', 'VIOM', 'INDUS', 'ATC', 'IDEA', 'QUIPPO', 'SPICE', 'TTML', 'TCL', 'TOWER VISION', 'RIL', 'WTTIL', 'OTHER']
        make_of_antenna_list = ['MTI H Pol', 'Xhat', 'Andrew', 'MTI', 'Twin', 'Proshape']
        antenna_polarisation_list = ['Vertical', 'Horizontal', 'Cross', 'Dual']
        antenna_type_list = ['Narrowbeam', 'Normal', 'Internal']
        ss_mount_type_list = ['Wall mount', 'Pole mount', 'Mast', 'Window Mount', 'Grill Mount', 'Pole']
        bh_off_or_onnet_list = ['OFFNET', 'ONNET', 'OFFNET+ONNET', 'OFFNET+ONNET UBR', 'ONNET+UBR', 'ONNET COLO', 'ONNET COLO+UBR']
        backhaul_type_list = ['SDH', 'Ethernet', 'E1', 'EoSDH', 'Dark Fibre', 'UBR']
        pmp_list = [1, 2]
        azimuth_angles_list = range(0, 361)
        yes_or_no = ['Yes', 'No', 'Y', 'N']
        dr_site_list = ['Yes', 'No', 'Y', 'N']

        # regex for checking whether string contains only numbers and .(dot)
        regex_numbers_and_single_dot = '^[0-9]*\\.?[0-9]*$'
        # regex_upto_two_dec_places = '^\d{1,9}($|\.\d{1,2}$)'
        regex_upto_two_dec_places = '^\d+($|\.\d{1,2}$)'
        regex_ip_address = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
        regex_alnum_comma_hyphen_fslash_underscore_space = '^[a-zA-Z0-9\s,_/-]+$'
        regex_alnum_comma_underscore_space = '^[a-zA-Z0-9,\s_]+$'
        regex_alpha_underscore = '^[a-zA-Z_]+$'
        regex_alpha_space = '^[a-zA-Z\s]+$'
        regex_alnum_comma_underscore_space = '^[a-zA-Z0-9\s,_]+$'
        regex_alnum_comma_underscore_space_asterisk = '^[a-zA-Z0-9\s,\*_]+$'
        regex_alnum_hyphen = '^[a-zA-Z0-9-]+$'
        regex_alnum_space = '^[a-zA-Z0-9\s]+$'
        regex_mac = '^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$'
        regex_lat_long = '^-?([1-8]?[1-9]|[1-9]0)\.{1}\d+'
        # regex_lat_long = '^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'

        # wimax bs fields validations but common with pmp bs
        # 'city' validation (must be alphabetical and can contain space)
        try:
            if city:
                if not re.match(regex_alpha_space, str(city).strip()):
                    errors += 'City must be alpha and can contain space.\n'
            else:
                errors += 'City must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'state' validation (must be alphabetical and can contain space)
        try:
            if state:
                if not re.match(regex_alpha_space, str(state).strip()):
                    errors += 'State must be alpha and can contain space.\n'
            else:
                errors += 'State must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'type of bs' validation (must be from provided list)
        try:
            if type_of_bs:
                if str(type_of_bs).strip().lower() not in [x.lower() for x in types_of_bs_list]:
                    errors += '{} is not valid option for bs type.\n'.format(type_of_bs)
            else:
                errors += 'Type of BS must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'site type' validation (must be from provided list)
        try:
            if site_type:
                if str(site_type).strip().lower() not in [x.lower() for x in site_types_list]:
                    errors += '{} is not a valid option for site type.\n'.format(site_type)
            else:
                errors += 'Site type must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'infra provider' validation (must be from provided list)
        try:
            if infra_provider:
                if str(infra_provider).strip().lower() not in [x.lower() for x in infra_provider_list]:
                    errors += '{} is not a valid option for infra provider.\n'.format(infra_provider)
            else:
                errors += 'Infra provider must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        #  'site id' validation (must be alphanumeric)
        try:
            if site_id:
                if not re.match(regex_alnum_comma_underscore_space, str(site_id).strip()):
                    errors += 'Site ID {} must be alphanumeric.\n'.format(site_id)
            else:
                errors += 'Site ID must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'building height' validation (must be upto 2 decimal places)
        try:
            if isinstance(building_height, int) or isinstance(building_height, float):
                if not re.match(regex_upto_two_dec_places, str(building_height).strip()):
                    errors += 'Building Height must be a number.\n'
            elif isinstance(building_height, str):
                errors += 'Building Height must be a number.\n'
            else:
                errors += 'Building Height must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'tower height' validation (must be upto 2 decimal places)
        try:
            if isinstance(tower_height, int) or isinstance(tower_height, float):
                if not re.match(regex_upto_two_dec_places, str(tower_height).strip()):
                    errors += 'Tower Height must be a number.\n'
            elif isinstance(tower_height, str):
                errors += 'Tower Height must be a number.\n'
            else:
                errors += 'Tower Height must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'idu ip' validation (must be an ip address)
        try:
            if idu_ip:
                if not re.match(regex_ip_address, idu_ip.strip()):
                    errors += 'IDU IP must be an ip address.'
            else:
                errors += 'IDU IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'sector name' validation (matches pattern for V1, V2, V3, V4 etc.)
        try:
            if sector_name:
                if not sector_name.lower().startswith('v'):
                    errors += 'Sector name must be like V1, V2, V3, V4 etc.'
            else:
                errors += 'Sector name must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'pmp' validation (must be from provided list)
        try:
            if pmp:
                if pmp not in pmp_list:
                    errors += '{} is not a valid option for pmp.\n'.format(pmp)
            else:
                errors += 'PMP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'make of antenna' validation (must be form provided list)
        try:
            if make_of_antenna:
                if make_of_antenna not in ['#N/A', 'na', 'NA']:
                    if str(make_of_antenna).strip().lower() not in [x.lower() for x in make_of_antenna_list]:
                        errors += '{} is not a valid option for make of antenna.\n'.format(make_of_antenna)
        except Exception as e:
            logger.info(e.message)

        # 'antenna polarisation' validation (must be from provided list)
        try:
            if antenna_polarization:
                if str(antenna_polarization).strip().lower() not in [x.lower() for x in antenna_polarisation_list]:
                    errors += '{} is not a valid option for antenna polarization.\n'.format(antenna_polarization)
            else:
                errors += 'Antenna polarization must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'antenna tilt' validation (must be upto 2 decimal places)
        try:
            if isinstance(antenna_tilt, int) or isinstance(antenna_tilt, float):
                if not re.match(regex_upto_two_dec_places, str(antenna_tilt).strip()):
                    errors += 'Antenna Tilt must be a number.\n'
            elif isinstance(antenna_tilt, str):
                errors += 'Antenna Tilt must be a number.\n'
            else:
                errors += 'Antenna Tilt must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'antenna height' validation (must be upto 2 decimal places)
        try:
            if isinstance(antenna_height, int) or isinstance(antenna_height, float):
                if not re.match(regex_upto_two_dec_places, str(antenna_height).strip()):
                    errors += 'Antenna Height must be a number.\n'
            elif isinstance(antenna_height, str):
                errors += 'Antenna Height must be a number.\n'
            else:
                errors += 'Antenna Height must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

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
            logger.info(e.message)

        # 'azimuth' validation (must be in range 0-360)
        try:
            if int(azimuth) not in azimuth_angles_list:
                errors += 'Azimuth must be in range 0-360.\n'
            elif int(azimuth) in azimuth_angles_list:
                pass
            else:
                errors += 'Azimuth must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'installation of splitter' validation (must be 'Yes' or 'No')
        try:
            if installation_of_splitter:
                if str(installation_of_splitter).strip().lower() not in [x.lower() for x in yes_or_no]:
                    errors += 'Installation of splitter must be from \'Yes\' or \'No\'.\n'
            else:
                errors += 'Installation of splitter must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'type of gps' validation (must be alphanumeric)
        try:
            if type_of_gps:
                if not (isinstance(type_of_gps, unicode) and type_of_gps.strip().isalnum()):
                    errors += 'Type Of GPS must be alphanumeric.\n'
            else:
                errors += 'Type Of GPS must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'bs switch ip' validation (must be an ip address)
        try:
            if bs_switch_ip:
                if bs_switch_ip != 'NA':
                    if not re.match(regex_ip_address, bs_switch_ip.strip()):
                        errors += 'BS Switch IP {} must be an ip address.\n'.format(bs_switch_ip)
            else:
                errors += 'BS switch IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'aggregation switch' validation (must be an ip address)
        try:
            if aggregation_switch:
                if aggregation_switch != 'NA':
                    if not re.match(regex_ip_address, aggregation_switch.strip()):
                        errors += 'Aggregation Switch must be an ip address.\n'
        except Exception as e:
            logger.info(e.message)

        # 'aggregation switch port' validation
        # (can only contains alphanumeric, underscore, hyphen, space, comma, forward slash)
        try:
            if aggregation_switch_port:
                if aggregation_switch_port != 'NA':
                    if not re.match(regex_alnum_comma_hyphen_fslash_underscore_space, aggregation_switch_port.strip()):
                        errors += 'Aggregation Switch Port can only contains alphanumeric, underscore, hyphen, space, comma, forward slash.\n'
        except Exception as e:
            logger.info(e.message)

        # 'bs converter ip' validation (must be an ip address)
        try:
            if bs_converter_ip:
                if bs_converter_ip != 'NA':
                    if not re.match(regex_ip_address, bs_converter_ip.strip()):
                        errors += 'BS Converter IP must be an ip address.\n'
            else:
                errors += 'BS Converter IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'pop conveter ip' validation (must be an ip address)
        try:
            if pop_converter_ip:
                if pop_converter_ip != 'NA':
                    if not re.match(regex_ip_address, pop_converter_ip.strip()):
                        errors += 'POP Converter IP must be an ip address.\n'
            else:
                errors += 'POP Converter must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'converter type' validation (can only contains alphabets or underscore)
        try:
            if converter_type:
                if converter_type != 'NA':
                    if not re.match(regex_alpha_underscore, converter_type.strip()):
                        errors += 'Converter type can only contains alphabets or underscore.\n'
            else:
                errors += 'Converter type must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'bh configured on' validation (must be an ip address)
        try:
            if bh_configured_on:
                if not re.match(regex_ip_address, bh_configured_on.strip()):
                    errors += 'BH Configured On must be an ip address.\n'
            else:
                errors += 'BH Configured On must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'switch or converter port' validation
        # (can only contains alphanumeric, underscore, hyphen, space, comma, forward slash)
        try:
            if switch_or_converter_port:
                if not re.match(regex_alnum_comma_hyphen_fslash_underscore_space, switch_or_converter_port.strip()):
                    errors += 'Switch/Converter Port {} can only contains alphanumeric, underscore, hyphen, space, comma, forward slash.\n'.format(switch_or_converter_port)
            else:
                errors += 'Switch/Converter Port must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'bh capacity' validation (must be numeric)
        try:
            if isinstance(bh_capacity, int) or isinstance(bh_capacity, float):
                if not re.match(regex_upto_two_dec_places, str(bh_capacity).strip()):
                    errors += 'BH Capacity must be a number.\n'
            elif isinstance(bh_capacity, str):
                errors += 'BH Capactiy must be a number.\n'
            else:
                errors += 'BH Capactiy must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'bh off or onnet' validation (must be from provided list)
        try:
            if bh_off_or_onnet:
                if str(bh_off_or_onnet).strip().lower() not in [x.lower() for x in bh_off_or_onnet_list]:
                    errors += '{} is not a valid option for bh off or onnet.\n'.format(bh_off_or_onnet)
            else:
                errors += 'BH Offnet/Onnet must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'backhaul type' validation (must be from provided list)
        try:
            if backhaul_type:
                if str(backhaul_type).strip().lower() not in [x.lower() for x in backhaul_type_list]:
                    errors += '{} is not a valid option for backhaul type.\n'.format(backhaul_type)
        except Exception as e:
            logger.info(e.message)

        # # 'bh circuit id' validation
        # # (can only contains alphanumeric, underscore, space, comma)
        # if bh_circuit_id:
        #     if not re.match(regex_alnum_comma_underscore_space_asterisk, bh_circuit_id.strip()):
        #         errors += 'BH Circuit ID - {} can only contains alphanumeric, underscore, space, comma.\n'.format(bh_circuit_id)

        # 'pe hostname' validation
        # (can only contains alphanumerics and hyphen)
        try:
            if pe_hostname:
                if not re.match(regex_alnum_hyphen, pe_hostname.strip()):
                    errors += 'PE Hostname can only contains alphanumerics and hyphen.\n'
            else:
                errors += 'PE Hostname must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'pe ip' validation (must be an ip address)
        try:
            if pe_ip:
                if not re.match(regex_ip_address, pe_ip.strip()):
                    errors += 'PE IP must be an ip address.\n'
            else:
                errors += 'PE IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'dr site' validation (must be 'Yes' or 'No')
        try:
            if dr_site:
                if str(dr_site).strip().lower() not in [x.lower() for x in dr_site_list]:
                    errors += 'DR Site {} must be from \'Yes\' or \'No\'.\n'.format(dr_site)
        except Exception as e:
            logger.info(e.message)

        # pmp fields validations
        # 'sync splitter used' validation (must be 'Yes' or 'No')
        try:
            if sync_splitter_used:
                if str(sync_splitter_used).strip().lower() not in [x.lower() for x in yes_or_no]:
                    errors += 'Sync splitter used must be from \'Yes\' or \'No\'.\n'
            else:
                errors += 'Installation of splitter must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'odu ip' validation (must be an ip address)
        try:
            if odu_ip:
                if not re.match(regex_ip_address, odu_ip.strip()):
                    errors += 'ODU IP must be an ip address.'
            else:
                errors += 'ODU IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'ss ip' validation (must be an ip address)
        try:
            if ss_ip:
                if not re.match(regex_ip_address, ss_ip.strip()):
                    errors += 'SS IP must be an ip address.'
            else:
                errors += 'SS IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'ip' validation (must be an ip address)
        try:
            if ip:
                if not re.match(regex_ip_address, ip.strip()):
                    errors += 'IP must be an ip address.'
            else:
                errors += 'IP must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'mac' validation
        try:
            if mac:
                if not re.match(regex_mac, str(mac).strip()):
                    errors += 'MAC must be a mac address.\n'
            else:
                errors += 'MAC must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'latitude' validation

        try:
            if latitude:
                if not re.match(regex_lat_long, str(latitude).strip()):
                    errors += 'Latitude value is wrong.\n'
            else:
                errors += 'Latitude must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'longitude' validation
        try:
            if longitude:
                if not re.match(regex_lat_long, str(longitude).strip()):
                    errors += 'Longitude value is wrong.\n'
            else:
                errors += 'Longitude must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'qos_bw' validation (must be numeric)
        try:
            if isinstance(qos_bw, int) or isinstance(qos_bw, float):
                if not re.match(regex_upto_two_dec_places, str(qos_bw).strip()):
                    errors += 'QOS (BW) must be a number.\n'
            elif qos_bw:
                if not re.match(regex_upto_two_dec_places, str(qos_bw).strip()):
                    errors += 'QOS (BW) must be a number.\n'
            else:
                errors += 'QOS (BW) must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'ss antenna height' validation (must be upto 2 decimal places)
        try:
            if isinstance(ss_antenna_height, int) or isinstance(ss_antenna_height, float):
                if not re.match(regex_upto_two_dec_places, str(ss_antenna_height).strip()):
                    errors += 'SS Antenna Height must be a number.\n'
            elif ss_antenna_height:
                if not re.match(regex_upto_two_dec_places, str(ss_antenna_height).strip()):
                    errors += 'SS Antenna Height must be a number.\n'
            else:
                errors += 'SS Antenna Height must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'ss tower height' validation (must be upto 2 decimal places)
        try:
            if isinstance(tower_pole_height, int) or isinstance(tower_pole_height, float):
                if not re.match(regex_upto_two_dec_places, str(tower_pole_height).strip()):
                    errors += 'SS Tower Height must be a number.\n'
            elif tower_pole_height:
                if not re.match(regex_upto_two_dec_places, str(tower_pole_height).strip()):
                    errors += 'SS Tower Height must be a number.\n'
            else:
                errors += 'SS Tower Height must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'antenna polarisation' validation (must be from provided list)
        try:
            if polarization:
                if str(polarization).strip().lower() not in [x.lower() for x in antenna_polarisation_list]:
                    errors += '{} is not a valid option for polarization.\n'.format(polarization)
            else:
                errors += 'Polarization must not be empty.\n'
        except Exception as e:
            logger.info(e.message)

        # 'antenna type' validation (must be from provided list)
        try:
            if antenna_type:
                if str(antenna_type).strip().lower() not in [x.lower() for x in antenna_type_list]:
                    errors += '{} is not a valid option for antenna type.\n'.format(antenna_type)
        except Exception as e:
            logger.info(e.message)

        # 'ss_mount_type' validation (must be from provided list)
        try:
            if ss_mount_type:
                if str(ss_mount_type).strip().lower() not in [x.lower() for x in ss_mount_type_list]:
                    errors += '{} is not a valid option for ss mount type.\n'.format(ss_mount_type)
        except Exception as e:
            logger.info(e.message)

        # 'ethernet extender' validation (must be 'Yes' or 'No')
        try:
            if ethernet_extender:
                if str(ethernet_extender).strip().lower() not in [x.lower() for x in yes_or_no]:
                    errors += 'Ethernet extender must be from \'Yes\' or \'No\'.\n'
        except Exception as e:
            logger.info(e.message)

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
            logger.info(e.message)

        # 'lens or reflector' validation (must be from provided list)
        try:
            if lens_or_reflector:
                if str(lens_or_reflector).strip().lower() not in [x.lower() for x in yes_or_no]:
                    errors += '{} is not a valid option for lens/reflector.\n'.format(lens_or_reflector)
        except Exception as e:
            logger.info(e.message)

        # 'rssi during acceptance' validation (must be -ve number)
        try:
            if rssi_during_acceptance:
                if rssi_during_acceptance > 0:
                    errors += 'RSSi During Acceptance must be negative number.\n'.format(rssi_during_acceptance)
        except Exception as e:
            logger.info(e.message)

        # # 'ttsl circuit id' validation
        # # (can only contains alphanumeric, underscore, space, comma)
        # if ttsl_circuit_id:
        #     if ttsl_circuit_id != "NA":
        #         if not re.match(regex_alnum_comma_underscore_space, ttsl_circuit_id.strip()):
        #             errors += 'TTSL Circuit ID can only contains alphanumeric, underscore, space, comma.\n'

        # insert key 'errors' in dict 'd'
        d['Errors'] = errors

        # check whether there are errors exist or not
        try:
            if not errors:
                valid_rows_dicts.append(d)
            else:
                invalid_rows_dicts.append(d)
        except Exception as e:
            logger.info(e.message)

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
                ws_valid.write(0, i, col, style)
            else:
                ws_valid.write(0, i, col, style_errors)
    except Exception as e:
        logger.info(e.message)

    try:
        for i, l in enumerate(valid_rows_lists):
            i += 1
            for j, col in enumerate(l):
                ws_valid.write(i, j, col)
    except Exception as e:
        logger.info(e.message)

    try:
        for i, col in enumerate(headers):
            if col != 'Errors':
                ws_invalid.write(0, i, col, style)
            else:
                ws_invalid.write(0, i, col, style_errors)
    except Exception as e:
        logger.info(e.message)

    try:
        for i, l in enumerate(invalid_rows_lists):
            i += 1
            for j, col in enumerate(l):
                ws_invalid.write(i, j, col)
    except Exception as e:
        logger.info(e.message)

    wb_valid.save('media/uploaded/inventory_files/valid.xls')
    wb_invalid.save('media/uploaded/inventory_files/invalid.xls')

    gis_bulk_obj = GISInventoryBulkImport.objects.get(pk=gis_obj_id)
    gis_bulk_obj.valid_filename = 'media/uploaded/inventory_files/valid.xls'
    gis_bulk_obj.invalid_filename = 'media/uploaded/inventory_files/invalid.xls'
    gis_bulk_obj.status = 1
    gis_bulk_obj.save()

    return gis_bulk_obj.original_filename

