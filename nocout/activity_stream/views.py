import json
from actstream.models import Action
from django.db.models.query import ValuesQuerySet
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from user_profile.models import UserProfile


class ActionList(ListView):
    model = Action
    template_name = 'activity_stream/actions_logs.html'

    def get_context_data(self, **kwargs):
        context=super(ActionList, self).get_context_data(**kwargs)
        context['datatable_headers'] = json.dumps([ {'mData':'actor', 'sTitle' : 'User','sWidth':'15%','bSortable': False},
                                                    {'mData':'__unicode__', 'sTitle' : 'Actions','bSortable': False},
                                                    {'mData':'timestamp', 'sTitle': 'Timestamp','sWidth':'17%','bSortable': False} ])
        return context


class ActionListingTable(BaseDatatableView):
    model = Action
    columns = [ 'timestamp']
    order_columns = ['-timestamp']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            actor_objects_ids_list = UserProfile.objects.filter(username__icontains=sSearch).values_list('id', flat=True)
            qs =Action.objects.filter( actor_object_id__in=actor_objects_ids_list ).values('id','timestamp')
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Action.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):

        if qs:
            for dct in qs:
                for key, val in dct.items():
                    dct['timestamp']= dct['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    if key=='id':
                        dct['__unicode__'] = Action.objects.get(pk= val).__unicode__()
                        dct['actor'] = Action.objects.get(pk= val).actor.username
                    else:
                        dct[key] = val
            return list(qs)
        return []

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)
        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret
