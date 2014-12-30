"""
"""
import json

from django.db.models import Q
from django.http import HttpResponse

from nocout.utils import logged_in_user_organizations


class Select2Mixin(object):
    """
    """
    obj_alias = 'alias'
    required_values = ['id', obj_alias]

    def get_queryset(self):
        """
        """
        qs = super(Select2Mixin, self).get_queryset()
        org_id = self.request.GET.get('org', '0')
        sSearch = self.request.GET.get('sSearch', None)
        if str(org_id) == "0":
            organizations = logged_in_user_organizations(self)
            qs = qs.filter(organization__id__in=organizations)
        else:
            qs = qs.filter(organization_id=org_id)

        if str(qs.model.__name__).strip().lower() == 'sector':
            sector_required_list = ['id', self.obj_alias, 'name', 'sector_configured_on__ip_address', 'sector_id']
            self.required_values = sector_required_list

        if sSearch:
            #specific cases to handle
            #ask Anoop how to make it more generic
            if str(qs.model.__name__).strip().lower() == 'sector':
                #we have a search for sector
                #search for sector can happen on
                #sector id, sector configured on
                qs = qs.filter(Q(**{"%s__icontains" % self.obj_alias: sSearch})
                               |
                               Q(**{"sector_configured_on__ip_address__icontains" : sSearch})
                               |
                               Q(**{"sector_id__icontains" : sSearch})
                )

            else:
                qs = qs.filter(Q(**{"%s__icontains" % self.obj_alias: sSearch}))

        qs = qs.values(*self.required_values)
        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if str(qs.model.__name__).strip().lower() == 'sector':
            if 'obj_id' in self.request.GET:
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
            if 'obj_id' in self.request.GET:
                response = [qs.get(id=self.request.GET['obj_id'])[self.obj_alias]]
            else:
                qs = qs[:50] # Limit result upto 50
                response = {
                    "total_count": qs.count(), "incomplete_results": False,
                    "items": list(qs)
                }

        return HttpResponse(json.dumps(response))
