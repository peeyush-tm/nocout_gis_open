from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from user_profile.models import UserProfile
from forms import UserForm

class UserList(ListView):
    model = UserProfile
    template_name = 'users_list.html'

class UserDetail(DetailView):
    model = UserProfile
    template_name = 'user_detail.html'
    
class UserCreate(CreateView):
    template_name = 'user_new.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

class UserUpdate(UpdateView):
    template_name = 'user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

class UserDelete(DeleteView):
    model = UserProfile
    template_name = 'user_delete.html'
    success_url = reverse_lazy('user_list')