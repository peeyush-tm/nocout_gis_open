from django.db.models import Q

from nocout.utils import logged_in_user_organizations


class DatatableOrganizationFilterMixin(object):
    """
    Limit data as per organization level access.

    Admin has access to his organization and sub-organizations.
    """
    organization_field = 'organization'
    values_queryset = True

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model.")
        qs = self.model.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(**{self.organization_field + "__in": logged_in_user_organizations(self)})

        if self.values_queryset:
            qs = qs.values(*self.columns + ['id'])
        return qs


class DatatableSearchMixin(object):
    """
    Search datatable based on provided serach columns if provided otherwise based on datatable's columns.
    """
    search_columns = []

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            search_columns = self.search_columns if self.search_columns else self.columns

            query_object = Q()
            for column in search_columns:
                query_object = query_object | Q(**{"%s__icontains" % column: sSearch})
            qs = qs.filter(query_object).distinct()
        return qs
