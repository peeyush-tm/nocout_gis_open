from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from device.models import Device
from forms import DeviceForm

class DeviceList(ListView):
    model = Device
    template_name = 'devices_list.html'

class DeviceDetail(DetailView):
    model = Device
    template_name = 'device_detail.html'
    
class DeviceCreate(CreateView):
    template_name = 'device_new.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')

class DeviceUpdate(UpdateView):
    template_name = 'device_update.html'
    model = Device
    form_class = DeviceForm
    success_url = reverse_lazy('device_list')

class DeviceDelete(DeleteView):
    model = Device
    template_name = 'device_delete.html'
    success_url = reverse_lazy('device_list')