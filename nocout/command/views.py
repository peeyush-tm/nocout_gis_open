from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from models import Command
from .forms import CommandForm


class CommandList(ListView):
    model = Command
    template_name = 'commands_list.html'


class CommandDetail(DetailView):
    model = Command
    template_name = 'command_detail.html'


class CommandCreate(CreateView):
    template_name = 'command_new.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')


class CommandUpdate(UpdateView):
    template_name = 'command_update.html'
    model = Command
    form_class = CommandForm
    success_url = reverse_lazy('commands_list')


class CommandDelete(DeleteView):
    model = Command
    template_name = 'command_delete.html'
    success_url = reverse_lazy('commands_list')
    
    