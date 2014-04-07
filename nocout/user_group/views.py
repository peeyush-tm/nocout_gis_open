from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from user_group.models import UserGroup
from forms import UserGroupForm

class UserGroupList(ListView):
    model = UserGroup
    template_name = 'ug_list.html'

class UserGroupDetail(DetailView):
    model = UserGroup
    template_name = 'ug_detail.html'
    
class UserGroupCreate(CreateView):
    template_name = 'ug_new.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

class UserGroupUpdate(UpdateView):
    template_name = 'ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'ug_delete.html'
    success_url = reverse_lazy('ug_list')