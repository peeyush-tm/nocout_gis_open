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

from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from django.http.response import  HttpResponse
from rest_framework import status
from django.core import serializers
from performance.models import CustomDashboard,UsersCustomDashboard,DSCustomDashboard
from service.models import ServiceDataSource
from user_profile.models import UserProfile
import json


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
            custom_dashboards_del = UsersCustomDashboard.objects.filter(
                user_profile = user_profile_id,
                custom_dashboard__in=dashboard_id
            )
            if custom_dashboards_del.exists():
                custom_dashboards_del.delete()
                result['success'] = 1
                result['message'] = "Successfully deleted."
            else:
                result['message'] = "Please enter valid custom Dashboard to be deleted"
        else:
            result['message'] = "Please enter the custom Dashboard to be deleted"
       

        return Response(result)
       
       


