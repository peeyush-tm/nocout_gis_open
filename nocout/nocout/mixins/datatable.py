from django.db.models import Q
import json

import logging

logger = logging.getLogger(__name__)

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway


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
            # Create instance of 'NocoutUtilsGateway' class
            nocout_utils = NocoutUtilsGateway()
            qs = qs.filter(**{self.organization_field + "__in": nocout_utils.logged_in_user_organizations(self)})

        if self.values_queryset:
            qs = qs.values(*self.columns + ['id'])

        if self.extra_qs_kwargs:
            qs = qs.filter(**self.extra_qs_kwargs)

        return qs


class DatatableSearchMixin(object):
    """
    Search datatable based on provided serach columns if provided otherwise based on datatable's columns.
    """

    # Fields based on which searching is done.
    search_columns = []

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        sSearch = self.request.GET.get('search[value]', None)
        
        if sSearch and not self.pre_camel_case_notation:
            search_columns = self.search_columns if self.search_columns else self.columns
            q = Q()
            for col in search_columns:
                q |= Q(**{'{0}__icontains'.format(col): sSearch})

            try:
                qs = qs.filter(q)
            except Exception, e:
                pass
        
        return self.advance_filter_queryset(qs)


class AdvanceFilteringMixin(object):
    """
    This class is responsible for advance filtering in BaseDatatableView
    """

    def advance_filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        advance_filters = self.request.GET.get('advance_filter', None)
        if advance_filters:
            filters_list = json.loads(advance_filters)
            if len(filters_list):
                if type(qs) == type(list()):
                    filtered_qs = list()
                    result = self.prepare_devices(qs)
                    condition_dict = dict()
                    for row in result:
                        for filters in filters_list:
                            condition = filters['condition']
                            column = filters['column']
                            values = filters['values']
                            column_val = unicode(row[column])
                            condition_dict[column] = False

                            if condition == 'equals':
                                is_matched = column_val.lower() in values
                                condition_dict[column] = str(is_matched)
                            elif condition == 'not_equals':
                                is_matched = column_val.lower() not in values
                                condition_dict[column] = str(is_matched)
                            else:
                                operator = False
                                is_any_matched = False
                                if condition == 'contains':
                                    operator = ' in '
                                elif condition == 'not_contains':
                                    operator = ' not in '
                                elif condition == 'gt':
                                    operator = ' > '
                                elif condition == 'gte':
                                    operator = ' >= '
                                elif condition == 'lt':
                                    operator = ' < '
                                elif condition == 'lte':
                                    operator = ' <= '
                                else:
                                    pass

                                for val in values:
                                    if is_any_matched:
                                        break

                                    if operator:
                                        if operator in [' > ', ' >= ', ' < ', ' <= ']:
                                            val = float(val)
                                            column_val = float(column_val)
                                            is_any_matched = eval('{0} {1} {2}'.format(column_val, operator, val))
                                        else:
                                            val = str(val)
                                            column_val = str(column_val).lower()
                                            is_any_matched = eval('"{0}" {1} "{2}"'.format(val, operator, column_val))
                                    else:
                                        if condition == 'starts_with':
                                            is_any_matched = column_val.lower().startswith(val)
                                        elif condition == 'ends_with':
                                            is_any_matched = column_val.lower().endswith(val)
                                        else:
                                            pass

                                condition_dict[column] = str(is_any_matched)

                        # Evaluate the Boolean string
                        if eval(' and '.join(condition_dict.values())):
                            filtered_qs.append(row)

                    return filtered_qs
                else:
                    filters_dict = {}
                    query = 'qs=qs.filter('
                    outer_counter = 0
                    for filters in filters_list:
                        condition = filters['condition']
                        column = filters['column']
                        values = filters['values']
                        q_object = ''
                        if condition == 'equals':
                            q_object = "Q({0}__in={1})".format(column, values)
                        elif condition == 'not_equals':
                            q_object = "~Q({0}__in={1})".format(column, values)
                        else:
                            negation = ''
                            operator = ''
                            if condition == 'contains':
                                operator = 'icontains'
                            elif condition == 'not_contains':
                                operator = 'icontains'
                                negation = '~'
                            elif condition == 'starts_with':
                                operator = 'istartswith'
                            elif condition == 'ends_with':
                                operator = 'iendswith'
                            else: 
                                operator = filters['condition']

                            q_object += '('
                            for val in values:
                                if q_object == '(':
                                    q_object += '{0}Q({1}__{2}="{3}")'.format(negation, column, operator, val.strip())
                                else:
                                    q_object += ' | {0}Q({1}__{2}="{3}")'.format(negation, column, operator, val.strip())

                            q_object += ')'
                        if outer_counter == len(filters_list) - 1:
                            query += q_object
                        else:
                            query += q_object + ','

                        outer_counter += 1
                    query += ')'
                    try:
                        exec query
                    except Exception, e:
                        pass
                        # logging.info(e.message)
        return qs