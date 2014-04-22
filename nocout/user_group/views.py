from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from user_group.models import UserGroup,Organization
from django.views.generic.edit import ModelFormMixin

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
    def form_valid(self, form):
        self.object = form.save(commit=False)
        usergroup_obj = UserGroup()
        usergroup_obj.name = form.cleaned_data['name']
        usergroup_obj.alias = form.cleaned_data['alias']
        usergroup_obj.address = form.cleaned_data['address']
        usergroup_obj.location = form.cleaned_data['location']
        usergroup_obj.save()
        try:
            usergroup_obj.parent = usergroup_obj
            usergroup_obj.save()
        except:
            pass
        
        for dg in form.cleaned_data['device_group']:
            organization = Organization()
            organization.user_group = usergroup_obj
            organization.device_group = dg
            organization.save()
        return super(ModelFormMixin, self).form_valid(form)
    
class UserGroupUpdate(UpdateView):
    template_name = 'ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')
    def form_valid(self, form):
        self.object = form.save(commit=False)
        usergroup_obj = UserGroup()
        usergroup_obj.name = form.cleaned_data['name']
        usergroup_obj.alias =form.cleaned_data['alias']
        usergroup_obj.address = form.cleaned_data['address']
        usergroup_obj.location = form.cleaned_data['location']
        usergroup_obj.save()
        #print "usergroup"
        try:
                usergroup_obj.parent = usergroup_obj
                usergroup_obj.save()
        except:
            pass  
        #print "rahul"      
        p =Organization.objects.filter(usergroup_obj =self.object).delete()
        p.save()
        
        for dg in form.cleaned_data['device_group']:
            
            organization= Organization()
            organization.p = p
            organization.device_group = dg
            organization.save()
        return super(ModelFormMixin, self).form_valid(form)

class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'ug_delete.html'
    success_url = reverse_lazy('ug_list')