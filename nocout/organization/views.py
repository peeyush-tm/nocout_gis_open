import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .forms import OrganizationForm
from .models import Organization
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.utils.util import date_handler


class OrganizationList(ListView):
    model = Organization
    template_name = 'organization/organization_list.html'

    def get_queryset(self):
        queryset = self.model._default_manager.values('name', 'description', 'user_group__name', 'device_group__name')
        return queryset[:10]

    def get_context_data(self, **kwargs):

        context=super( OrganizationList, self ).get_context_data(**kwargs)
        object_list = context['object_list']
        object_list, object_list_headers = Datatable_Generation( object_list ).main()
        context['object_list'] = json.dumps( object_list, default=date_handler )
        context.update({
            'object_list_headers' : json.dumps(object_list_headers, default=date_handler )
        })
        return context



class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'organization/organization_detail.html'


class OrganizationCreate(CreateView):
    template_name = 'organization/organization_new.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')


class OrganizationUpdate(UpdateView):
    template_name = 'organization/organization_update.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')


class OrganizationDelete(DeleteView):
    model = Organization
    template_name = 'organization/organization_delete.html'
    success_url = reverse_lazy('organization_list')
