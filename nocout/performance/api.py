"""
===============================================
Module contains api's specific to 'performance' app.
===============================================

Location:
* /nocout_gis/nocout/performance/api.py

List of constructs:
=======
Classes
=======
=======
Methods
=======

"""
import urllib
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.db.models import Q, Count
from rest_framework.response import Response
from django.http.response import  HttpResponse
from rest_framework import status
from django.core import serializers
from performance.models import CustomDashboard, UsersCustomDashboard, DSCustomDashboard, PingStabilityTest
from device.models import DeviceTechnology
from machine.models import Machine
from site_instance.models import SiteInstance
from service.models import ServiceDataSource
from user_profile.models import UserProfile
from nocout.settings import MAX_PARALLEL_STABILITY_TESTS
import json
from IPy import IP
import logging

import ast
from copy import deepcopy
import requests

logger = logging.getLogger(__name__)


class CustomDashboardCreate(APIView):
    """
    List all dashboards, or create a new dashboard.
    """ 
    
    def post(self, request, format=None):
            
        result = {
            'success': 0,
            'message': 'Custom dashboard not saved',
            'data': []
        }

        name = self.request.POST.get('custom_name', '')
        title = self.request.POST.get('custom_alias', '')
        display_type =   self.request.POST.get('selected_type', '')
        ds_srv_list =   self.request.POST.getlist('ds_name[]', '')
        is_public =  json.loads(self.request.POST.get('is_public_dashboard', ''))    

        # Save custom dashboard master
        dashboard_name_count = CustomDashboard.objects.filter(name=name)
        dashboard_title_count = CustomDashboard.objects.filter(title=title)

        if dashboard_name_count.exists():
            result.update(
                message='Dashboard name already exists. Please try another.'
            )
            return HttpResponse(json.dumps(result))
        elif dashboard_title_count.exists():
            result.update(
                message='Dashboard title already exists. Please try another.'
            )
            return HttpResponse(json.dumps(result))


        custom_ds_instance = CustomDashboard()
        custom_ds_instance.name = name
        custom_ds_instance.title = title
        custom_ds_instance.display_type = display_type
        custom_ds_instance.is_public = is_public
        custom_ds_instance.save()

        # Save user entry for the created custom dashboard
        current_user = UserProfile.objects.get(id=self.request.user.id)
        user_custom_ds_instance = UsersCustomDashboard()
        user_custom_ds_instance.user_profile =current_user
        user_custom_ds_instance.custom_dashboard_id = custom_ds_instance.id
        user_custom_ds_instance.save()
        
        #  Save data_source entry for the created custom dashboard
       
        for ds_srv in ds_srv_list:
            if '_' not in ds_srv:
                continue
            ds_srv_splitted = ds_srv.split('_')
            data_source = ds_srv_splitted[0]
            service = ds_srv_splitted[1]            
            data_source_custom_instance = ''
            data_source_custom_instance = DSCustomDashboard()            
            data_source_custom_instance.custom_dashboard_id = custom_ds_instance.id
            data_source_custom_instance.data_source_id = data_source
            data_source_custom_instance.service_id = service
            data_source_custom_instance.save()

        data = serializers.serialize('json', custom_ds_instance.__class__.objects.filter(id=custom_ds_instance.id))

        result.update(
            success=1,
            message='Custom dashboard saved successfully.',
            data=data
        )

        return HttpResponse(json.dumps(result))


class CustomDashboardList(APIView):
    """
    List all custom dashboards associated with user
    """
    def get(self, request, format=None):

         # Response of api.
        result = {
            'success': 0,
            'message': 'No Data.',
            'data': {
                'meta': {},
                'objects': {                 
                }
            }
        }

        result_data=list()
        search_txt  = self.request.GET.get('search_txt', None)
        # Save user entry for the created custom dashboard
        user_profile_id = self.request.user.pk
        if search_txt:
            custom_dashboards = CustomDashboard.objects.filter(user_profile=user_profile_id,title__icontains=search_txt)
        else:
            custom_dashboards = CustomDashboard.objects.filter(user_profile=user_profile_id)
        # print custom_dashboards
        result_data = [{'id': value.id,
                    'title': value.title,
                    'name':value.name,
                    }for value in custom_dashboards]
                                                                                

        if custom_dashboards:
            result['message'] = "Successfully fetched Dashboards"
            result['success'] = 1                 
            result['data']['objects']=result_data                
        else:
            result['message'] = "No Custom Dashboards Exist"


        return Response(result)


class CustomDashboardDelete(APIView):
    """
    Delete all dashboards selected by user.
    """
    def post(self, request, format=None):
        result = {
            "success": 0,
            "message": "",
            "data": {
            }
        }
        # Save user entry for the created custom dashboard
        user_profile_id = self.request.user.id
        dashboard_id = self.request.POST.getlist('selected_db[]','')

        if dashboard_id:                        
            user_custom_dashboards_del = UsersCustomDashboard.objects.filter(
                user_profile = user_profile_id,
                custom_dashboard__in=dashboard_id
            )
            custom_dashboards_del = CustomDashboard.objects.filter(               
                id__in=dashboard_id
            )
            ds_custom_dashboards_del = DSCustomDashboard.objects.filter(                
                custom_dashboard__in=dashboard_id
            )
            if custom_dashboards_del.exists():
                custom_dashboards_del.delete()
                ds_custom_dashboards_del.delete()
                user_custom_dashboards_del.delete()
                result['success'] = 1
                result['message'] = "Successfully deleted."
            else:
                result['message'] = "Please enter valid custom Dashboard to be deleted"
        else:
            result['message'] = "Please enter the custom Dashboard to be deleted"
       

        return Response(result)
       
       
class StartPingStabilityTest(APIView):
    """
    This class starts ping stability testing for given ip address
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(StartPingStabilityTest, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """

        """
        result = {
            'success': 0,
            'message': 'Some error occured. Please try again later.'
        }

        total_pending_count = PingStabilityTest.objects.filter(
            status=False
        ).count()

        # Not start parallel stability tests more than MAX_PARALLEL_STABILITY_TESTS
        if total_pending_count >= MAX_PARALLEL_STABILITY_TESTS:
            result.update(
                message='Currently {} stability tests are running. Please try after some time.'.format(total_pending_count)
            )
            return Response(result)

        ip_address = request.POST.get('ip_address')
        duration = request.POST.get('duration', 1)
        tech_id = request.POST.get('tech_id')
        tech_name = request.POST.get('tech_name')
        email_ids = request.POST.get('email_ids', '')

        if not tech_name:
            try:
                tech_name = DeviceTechnology.objects.get(pk=tech_id).name
            except Exception, e:
                result.update(
                    message='Invalid Data.'
                )
                return Response(result)

        machine_site_info = get_machine_site(ip_address, tech_name, duration)

        machine = machine_site_info.get('machine')
        site = machine_site_info.get('site')

        if machine and site:
            ping_stability_instance = PingStabilityTest(
                user_profile_id=self.request.user.id,
                ip_address=ip_address,
                time_duration=duration,
                machine=machine,
                site_instance=site,
                technology=DeviceTechnology.objects.get(id=tech_id),
                email_ids=email_ids
            )
            ping_stability_instance.save()

            post_data = {
                'username': site.username,
                'password': site.password,
                'port': site.web_service_port,
                'machine': machine.machine_ip,
                'site_name': site.name,
                'params': {
                    'data': [{
                        'ip_address': ip_address,
                        'time_interval': duration,
                        'id': ping_stability_instance.id
                    }],
                    'mode': 'ping_test'
                }
            }

            url = "http://{}:{}@{}:{}/{}/check_mk/nocout_live.py".format(
                post_data.get('username'),
                post_data.get('password'),
                post_data.get('machine'),
                post_data.get('port'),
                post_data.get('site_name')
            )

            # Encoding data.
            encoded_data = urllib.urlencode(post_data.get('params'))

            # Sending post request to nocout device app to start given IP ping stability testing
            try:
                result.update(
                    success=1,
                    message='Ping stability testing started.'
                )
                r = requests.post(url, data=encoded_data)
                response_dict = ast.literal_eval(r.text)
                if len(response_dict):
                    temp_dict = deepcopy(response_dict)
                    q.put(temp_dict)
            except Exception as e:
                logger.error('Stability Test Request Exception')
                logger.error(e)
                pass

        return Response(result)


def get_machine_site(ip_address, tech_name, duration):
    '''

    '''
    info_obj = {
        'machine': '',
        'site': ''
    }

    OSPF_MACHINES = ['ospf1', 'ospf3', 'ospf4', 'ospf5']

    if tech_name in ['P2P', 'PTP-BH']:
        try:
            # check whether IP is public or private
            test_ip = IP(ip_address)
            if test_ip.iptype() == 'PRIVATE':
                info_obj['machine'] = Machine.objects.get(name='vrfprv')
                info_obj['site'] = SiteInstance.objects.get(name='vrfprv_slave_1')
            elif test_ip.iptype() == 'PUBLIC':
                info_obj['machine'] = Machine.objects.get(name='pub')
                info_obj['site'] = SiteInstance.objects.get(name='pub_slave_1')
            else:
                pass
        except Exception as e:
            logger.error('PTP machine site selection')
            logger.error(e.message)
    else:
        used_ospf_machines = set(PingStabilityTest.objects.exclude(
            machine__name__in=['vrfprv', 'pub']
        ).filter(
            status=False
        ).values_list('machine__name', flat=True))

        # Get list of machines which are not used yet
        unused_machines = list(set(OSPF_MACHINES) - used_ospf_machines)

        # If any of the ospf machine is not used yet then please use first item from this list
        if len(unused_machines):
            machine_name = unused_machines[0]
            try:
                info_obj['machine'] = Machine.objects.get(name=machine_name)
                info_obj['site'] = SiteInstance.objects.get(name=str(machine_name)+'_slave_1')
            except Exception, e:
                logger.error('Machine Allotment Error 1')
                logger.error(unused_machines)
                logger.error(e)
                pass
        else:
            machine_wise_active_tests = list(PingStabilityTest.objects.exclude(
                machine__name__in=['vrfprv', 'pub']
            ).filter(
                status=False
            ).values('machine__name').annotate(
                mcount=Count('machine__name')
            ).order_by('machine__name'))

            least_ip_machine_name = machine_wise_active_tests[0]['machine__name']

            try:
                info_obj['machine'] = Machine.objects.get(name=least_ip_machine_name)
                info_obj['site'] = SiteInstance.objects.get(name=str(least_ip_machine_name)+'_slave_1')
            except Exception, e:
                logger.error('Machine Allotment Error 2')
                logger.error(machine_wise_active_tests)
                logger.error(e)
                pass

    return info_obj