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

        if sSearch:
            qs = qs.filter(Q(**{"%s__icontains" % self.obj_alias: sSearch}))
        qs = qs.values('id', self.obj_alias)
        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        if 'obj_id' in self.request.GET:
            response = [qs.get(id=self.request.GET['obj_id'])[self.obj_alias]]
        else:
            qs = qs[:50] # Limit result upto 50
            response = {
                "total_count": qs.count(), "incomplete_results": False,
                "items": list(qs)
            }

        return HttpResponse(json.dumps(response))
