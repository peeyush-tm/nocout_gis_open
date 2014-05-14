from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .forms import OrganizationForm
from .models import Organization


class OrganizationList(ListView):
    model = Organization
    template_name = 'organization/organization_list.html'


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
