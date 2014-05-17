import json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from device_group.models import DeviceGroup
from forms import DeviceGroupForm
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.utils.util import date_handler


class DeviceGroupList(ListView):
    model = DeviceGroup
    template_name = 'device_group/dg_list.html'

    def get_queryset(self):
        queryset = self.model._default_manager.values('name', 'alias', 'parent__name', 'location','address')
        return queryset[:10]

    def get_context_data(self, **kwargs):

        context=super( DeviceGroupList, self ).get_context_data(**kwargs)
        object_list = context['object_list']
        object_list, object_list_headers = Datatable_Generation( object_list ).main()
        context['object_list'] = json.dumps( object_list, default=date_handler )
        context.update({
            'object_list_headers' : json.dumps(object_list_headers, default=date_handler )
        })
        return context




class DeviceGroupDetail(DetailView):
    model = DeviceGroup
    template_name = 'device_group/dg_detail.html'


class DeviceGroupCreate(CreateView):
    template_name = 'device_group/dg_new.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')


class DeviceGroupUpdate(UpdateView):
    template_name = 'device_group/dg_update.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')


class DeviceGroupDelete(DeleteView):
    model = DeviceGroup
    template_name = 'device_group/dg_delete.html'
    success_url = reverse_lazy('dg_list')