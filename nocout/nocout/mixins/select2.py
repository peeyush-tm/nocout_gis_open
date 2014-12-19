"""
"""
import json

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
        org_id = self.request.GET['org']
        sSearch = self.request.GET['sSearch']
        if str(org_id) == "0":
            organizations = self.logged_in_user_organizations()
            qs = qs.filter(organization__id__in=organizations)
        else:
            qs = qs.filter(organization_id=org_id)

        qs = qs.filter(Q(**{"%s__icontains" % obj_alias: sSearch}))
        qs = qs.values('id', obj_alias)[:50]
        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        if obj_id in self.request.GET:
            response = [getattr(qs.get(id=self.request.GET['obj_id']), obj_alias)]
        else:
            response = {
                "total_count": qs.count(), "incomplete_results": False,
                "items": list(qs)
            }

        return HttpResponse(json.dumps(response))
