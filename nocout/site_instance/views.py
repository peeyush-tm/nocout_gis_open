from django.db.models.query import ValuesQuerySet
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
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin


class SiteInstanceList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Site Instance List page.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_list.html'
    required_permissions = ('site_instance.view_siteinstance',)

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

class SiteInstanceListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Site Instance Data table.
    """
    model = SiteInstance
    required_permissions = ('site_instance.view_siteinstance',)
    columns = ['name', 'alias','machine__name', 'live_status_tcp_port', 'web_service_port', 'username']
    order_columns = ['name', 'alias','machine__name', 'live_status_tcp_port', 'web_service_port', 'username']
    search_columns = ['name', 'alias','machine__name', 'live_status_tcp_port', 'web_service_port', 'username']

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

        json_data = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in json_data:
            dct.update(actions='<a href="/site/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/site/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class SiteInstanceDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render Site Instance Detail.
    """
    model = SiteInstance
    required_permissions = ('site_instance.view_siteinstance',)
    template_name = 'site_instance/site_instance_detail.html'


class SiteInstanceCreate(PermissionsRequiredMixin, CreateView):
    """
    Class Based View to Create a Site Instance.
    """
    template_name = 'site_instance/site_instance_new.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.add_siteinstance',)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        self.object=form.save()
        return HttpResponseRedirect(SiteInstanceCreate.success_url)

class SiteInstanceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to Update the Site Instance.
    """
    template_name = 'site_instance/site_instance_update.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.change_siteinstance',)

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


class SiteInstanceDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to Delete the Site Instance.
    """
    model = SiteInstance
    template_name = 'site_instance/site_instance_delete.html'
    success_url = reverse_lazy('site_instance_list')
    required_permissions = ('site_instance.delete_siteinstance',)
