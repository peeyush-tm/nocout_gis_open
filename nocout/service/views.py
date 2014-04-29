from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from models import Service, ServiceParameters
from .forms import ServiceForm, ServiceParametersForm


class ServiceList(ListView):
    model = Service
    template_name = 'services_list.html'


class ServiceDetail(DetailView):
    model = Service
    template_name = 'service_detail.html'


class ServiceCreate(CreateView):
    template_name = 'service_new.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')


class ServiceUpdate(UpdateView):
    template_name = 'service_update.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')


class ServiceDelete(DeleteView):
    model = Service
    template_name = 'service_delete.html'
    success_url = reverse_lazy('services_list')


class ServiceParametersList(ListView):
    model = ServiceParameters
    template_name = 'services_parameter_list.html'


class ServiceParametersDetail(DetailView):
    model = ServiceParameters
    template_name = 'service_parameter_detail.html'


class ServiceParametersCreate(CreateView):
    template_name = 'service_parameter_new.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')


class ServiceParametersUpdate(UpdateView):
    template_name = 'service_parameter_update.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')


class ServiceParametersDelete(DeleteView):
    model = ServiceParameters
    template_name = 'service_parameter_delete.html'
    success_url = reverse_lazy('services_parameter_list')
    
