from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from models import SiteInstance
from forms import SiteInstanceForm


class SiteInstanceList(ListView):
    model = SiteInstance
    form_class = SiteInstanceForm
    template_name = 'site_instance/site_create.html'
    success_url = reverse_lazy('site_list')


class SiteInstanceDetail(DetailView):
    model = SiteInstance
    template_name = 'site_instance_detail.html'

class SiteInstanceCreate(CreateView):
    template_name = 'site_instance_new.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')

class SiteInstanceUpdate(UpdateView):
    template_name = 'site_instance_update.html'
    model = SiteInstance
    form_class = SiteInstanceForm
    success_url = reverse_lazy('site_instance_list')


class SiteInstanceDelete(DeleteView):
    model = SiteInstance
    template_name = 'site_instance_delete.html'
    success_url = reverse_lazy('site_instance_list')

