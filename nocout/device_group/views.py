from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from device_group.models import DeviceGroup
from forms import DeviceGroupForm


class DeviceGroupList(ListView):
    model = DeviceGroup
    template_name = 'dg_list.html'


class DeviceGroupDetail(DetailView):
    model = DeviceGroup
    template_name = 'dg_detail.html'


class DeviceGroupCreate(CreateView):
    template_name = 'dg_new.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')


class DeviceGroupUpdate(UpdateView):
    template_name = 'dg_update.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')


class DeviceGroupDelete(DeleteView):
    model = DeviceGroup
    template_name = 'dg_delete.html'
    success_url = reverse_lazy('dg_list')