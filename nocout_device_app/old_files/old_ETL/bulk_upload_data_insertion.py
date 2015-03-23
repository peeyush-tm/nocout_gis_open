from nocout_site_name import *
import imp

config_module = imp.load_source('configparser', '/omd/sites/%s/nocout/configparser.py' % nocout_site_name)

def main():
    mongo_conf = []
    configs = config_module.parse_config_obj()
    for section, options in configs.items():
        mongo_conf.append((options.get('site'),options.get('host'), options.get('port')))

    bulk_script = configs.get(mongo_conf[0][0]).get('bulk_upload').get('script')
    bulk_data_insertion_script = __import__(bulk_script)
    bulk_data_insertion_script.entry(
    user=configs.get(mongo_conf[0][0]).get('user'),
    sql_passwd=configs.get(mongo_conf[0][0]).get('sql_passwd'),
    sql_port=configs.get(mongo_conf[0][0]).get('mysql_port'),
    sql_db=configs.get(mongo_conf[0][0]).get('sql_db'),
    ip=configs.get(mongo_conf[0][0]).get('ip')
    )


if __name__ == '__main__':
	main()

