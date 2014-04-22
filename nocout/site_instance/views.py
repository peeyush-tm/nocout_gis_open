# Create your views here.
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from forms import SiteInstanceForm
from site_instance.models import SiteInstance

class SiteinstanceCreate(CreateView):
    model = SiteInstance
    form_class = SiteInstanceForm
    template_name = 'site_create.html'
    success_url = reverse_lazy('site_list')

class SiteinstanceList(ListView):
    model = SiteInstance
    template_name = 'site_list.html'

class SiteinstanceDetail(DetailView):
    model = SiteInstance
    template_name = 'site_detail.html'  

class SiteinstanceUpdate(UpdateView):
    model = SiteInstance
    form_class = SiteInstanceForm
    template_name = 'site_update.html'
    success_url = reverse_lazy('site_list')

class SiteInstanceDelete(DeleteView):
    model = SiteInstance
    template_name = 'site_delete.html'
    success_url = reverse_lazy('site_list')    