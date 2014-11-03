from django.contrib.auth.decorators import permission_required
from django.db.models.query import ValuesQuerySet
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import SiteInstance
from forms import SiteInstanceForm
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from nocout.utils.util import DictDiffer
import json
from activity_stream.models import UserAction

class SiteInstanceList(ListView):
    """
    Class Based View to render Site Instance List page.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_list.html'

    @method_decorator(permission_required('site_instance.view_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(SiteInstanceList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(SiteInstanceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                  'sTitle' : 'Name',                  'sWidth':'auto',},
            {'mData':'alias',                 'sTitle' : 'Alias',                 'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'machine__name',         'sTitle' : 'Machine',               'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'live_status_tcp_port',  'sTitle' : 'Live Status TCP Port',  'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'web_service_port',      'sTitle' : 'Web Service Port',      'sWidth':'auto',},
            {'mData':'username',              'sTitle' : 'Username',              'sWidth':'auto',},
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class SiteInstanceListingTable(BaseDatatableView):
    """
    Class based View to render Site Instance Data table.
    """
    model = SiteInstance
    columns = ['name', 'alias','machine__name', 'live_status_tcp_port', 'web_service_port', 'username']
    order_columns = ['name', 'alias','machine__name', 'live_status_tcp_port', 'web_service_port', 'username']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return SiteInstance.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/site/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/site/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

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

class SiteInstanceDetail(DetailView):
    """
    Class Based View to render Site Instance Detail.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_detail.html'


class SiteInstanceCreate(CreateView):
    """
    Class Based View to Create a Site Instance.
    """
    template_name = 'site_instance/site_instance_new.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.add_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(SiteInstanceCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        self.object=form.save()
        return HttpResponseRedirect(SiteInstanceCreate.success_url)

class SiteInstanceUpdate(UpdateView):
    """
    Class Based View to Update the Site Instance.
    """
    template_name = 'site_instance/site_instance_update.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.change_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(SiteInstanceUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer( initial_field_dict, cleaned_data_field_dict ).changed()

        if changed_fields_dict:

            verb_string = 'Changed values of Site Instance: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            self.object=form.save()
        return HttpResponseRedirect(SiteInstanceUpdate.success_url)


class SiteInstanceDelete(DeleteView):
    """
    Class Based View to Delete the Site Instance.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_delete.html'
    success_url = reverse_lazy('site_instance_list')

    @method_decorator(permission_required('site_instance.delete_siteinstance', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(SiteInstanceDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Log the user activity before deleting the Site Instance.
        """
        try:
            UserAction.objects.create(user_id=self.request.user.id, module='Site Instance',
                         action='A site instance is deleted - {}'.format(self.get_object().name) )
        except:
            pass
        return super(SiteInstanceDelete, self).delete(request, *args, **kwargs)