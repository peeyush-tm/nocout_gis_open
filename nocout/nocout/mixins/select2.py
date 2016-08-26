"""
"""
import json

from django.db.models import Q
from django.http import HttpResponse
from device.models import DeviceTechnology
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway


class Select2Mixin(object):
    """
    Mixin used for getting data for select2 field using ajax call.
    """
    obj_alias = 'alias'

    def get_queryset(self):
        """
        Method which returns queryset after filter.
        :param self:
        :return qs:
        """
        required_values = ['id', self.obj_alias]
        qs = super(Select2Mixin, self).get_queryset()
        org_id = self.request.GET.get('org', '0')
        sSearch = self.request.GET.get('sSearch', None)
        tech_name = self.request.GET.get('tech_name', None)
        if str(org_id) == "0":
            # Create instance of 'NocoutUtilsGateway' class
            nocout_utils = NocoutUtilsGateway()
            organizations = nocout_utils.logged_in_user_organizations(self)
            qs = qs.filter(organization__id__in=organizations)
        else:
            qs = qs.filter(organization_id=org_id)

        if str(qs.model.__name__).strip().lower() == 'sector':
            sector_required_list = ['id', self.obj_alias, 'name', 'sector_configured_on__ip_address', 'sector_id']
            required_values = sector_required_list
        elif str(qs.model.__name__).strip().lower() == 'device':
            required_values = required_values = ['id', self.obj_alias, 'ip_address']

        if sSearch:
            #specific cases to handle
            #ask Anoop how to make it more generic
            if str(qs.model.__name__).strip().lower() == 'sector':
                #we have a search for sector
                #search for sector can happen on
                #sector id, sector configured on
                qs = qs.filter(
                    Q(**{
                        "%s__icontains" % self.obj_alias: sSearch
                    })
                    |
                    Q(**{
                        "sector_configured_on__ip_address__icontains" : sSearch
                    })
                    |
                    Q(**{
                        "sector_id__icontains" : sSearch
                    })
                )

            else:
                qs = qs.filter(Q(**{"%s__icontains" % self.obj_alias: sSearch}))

        if tech_name:
            try:
                tech_id = DeviceTechnology.objects.get(name__iexact=tech_name).id
                qs = qs.filter(device_technology=tech_id)
            except Exception, e:
                pass

        qs = qs.values(*required_values)
        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if str(qs.model.__name__).strip().lower() == 'sector':
            if int(self.request.GET.get('obj_id', 0)):
                sector_object = qs.get(id=self.request.GET['obj_id'])
                response = [
                    "{0} ({1}) {2}".format(sector_object[self.obj_alias],
                        sector_object['sector_configured_on__ip_address'],
                        sector_object['sector_id'] if sector_object['sector_id'] else ""
                    )
                ]


            else:
                qs = qs[:50] # Limit result upto 50
                response_list = list()
                for resp in qs:
                    resp['alias'] += " ({0}) ".format(resp['sector_configured_on__ip_address'])
                    if resp['sector_id']:
                        resp['alias'] += "{0}".format(resp['sector_id'])

                response = {
                    "total_count": qs.count(), "incomplete_results": False,
                    "items": list(qs)
                }
        else:
            if int(self.request.GET.get('obj_id', 0)):
                if str(qs.model.__name__).strip().lower() == 'device':
                    response = [qs.get(id=self.request.GET['obj_id'])[self.obj_alias], qs.get(id=self.request.GET['obj_id'])['ip_address']]
                else:
                    response = [qs.get(id=self.request.GET['obj_id'])[self.obj_alias]]
            else:
                qs = qs[:50] # Limit result upto 50
                response = {
                    "total_count": qs.count(), "incomplete_results": False,
                    "items": list(qs)
                }

        return HttpResponse(json.dumps(response))
