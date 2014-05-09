from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from user_group.models import UserGroup,Organization
from django.views.generic.edit import ModelFormMixin

from forms import UserGroupForm

class UserGroupList(ListView):
    model = UserGroup
    template_name = 'user_group/ug_list.html'

class UserGroupDetail(DetailView):
    model = UserGroup
    template_name = 'user_group/ug_detail.html'
    
class UserGroupCreate(CreateView):
    template_name = 'user_group/ug_new.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #Add the default group if the parent field is None
        # if not self.object.parent:
        #     self.object.parent=Default_group
        self.object.save()

        for dg in form.cleaned_data['device_group']:
            Organization.objects.create(user_group=self.object, device_group=dg)

        return super(ModelFormMixin, self).form_valid(form)
    
class UserGroupUpdate(UpdateView):
    template_name = 'user_group/ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     usergroup_obj = UserGroup()
    #
    #
    #     usergroup_obj.name = form.cleaned_data['name']
    #     usergroup_obj.alias =form.cleaned_data['alias']
    #     usergroup_obj.address = form.cleaned_data['address']
    #     usergroup_obj.location = form.cleaned_data['location']
    #     usergroup_obj.save()
    #     #print "usergroup"
    #     try:
    #             usergroup_obj.parent = usergroup_obj
    #             usergroup_obj.save()
    #     except:
    #         pass
    #     #print "rahul"
    #     p =Organization.objects.filter(usergroup_obj =self.object).delete()
    #     p.save()
    #
    #     for dg in form.cleaned_data['device_group']:
    #
    #         organization= Organization()
    #         organization.p = p
    #         organization.device_group = dg
    #         organization.save()
    #     return super(ModelFormMixin, self).form_valid(form)


    def form_valid(self, form):
        #IntegrityError: (1062, "Duplicate entry 'test_group4' for key 'name'")
        #TODO:Disable the edit of name from the UI (name should be unique)
        self.object = form.save(commit=False)
        if form.cleaned_data['device_group']:
            Organization.objects.filter( user_group = self.object ).delete()

            for dg in form.cleaned_data['device_group']:
                Organization.objects.create(user_group=self.object, device_group=dg)

        UserGroup.objects.filter(name=self.object.name).update( alias=self.object.alias, address=self.object.address,
                                                      location=self.object.location, parent=self.object.parent )
        return super(ModelFormMixin, self).form_valid(form)



class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'user_group/ug_delete.html'
    success_url = reverse_lazy('ug_list')

