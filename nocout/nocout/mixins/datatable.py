from django.db.models import Q

from nocout.utils import logged_in_user_organizations


class ValuesQuerySetMixin(object):
    """
    class ExampleDatatableListing(ValuesQuerySetMixin, BaseDatatableView):
        tab_search = {
            "tab_kwarg": 'technology',
            "tab_attr": "live_polling_template__technology__name",
        }
        extra_qs_kwargs = {
            "is_deleted": 0,
            "is_added_to_nms": 1,
        }
    """

    tab_search = None
    extra_qs_kwargs = None

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        qs = self.model.objects.values(*self.columns + ['id'])
        if self.tab_search:
            tab_kwarg = self.tab_search['tab_kwarg']
            qs = qs.filter(**{self.tab_search['tab_attr']: self.kwargs[tab_kwarg]})

        if self.extra_qs_kwargs:
            qs = qs.filter(**self.extra_qs_kwargs)
        return qs


class DatatableOrganizationFilterMixin(object):
    """
    Limit data as per organization level access.

    Admin has access to his organization and sub-organizations.
    """
    organization_field = 'organization'
    values_queryset = True
    extra_qs_kwargs = None

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

        if self.extra_qs_kwargs:
            qs = qs.filter(**self.extra_qs_kwargs)

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
