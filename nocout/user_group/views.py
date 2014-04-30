from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from user_group.models import UserGroup, Organization
from forms import UserGroupForm
from django.http.response import HttpResponseRedirect


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
        user_group = UserGroup()
        user_group.name = form.cleaned_data['name']
        user_group.alias = form.cleaned_data['alias']
        user_group.location = form.cleaned_data['location']
        user_group.address = form.cleaned_data['address']

        # saving parent --> FK Relation
        try:
            parent_user_group = UserGroup.objects.get(name=form.cleaned_data['parent'])
            user_group.parent = parent_user_group
            user_group.save()
        except:
            print "UserGroup has no parent."

        # saving device_group --> M2M Relation (Model: Organization)
        for dg in form.cleaned_data['device_group']:
            organization = Organization()
            organization.user_group = user_group
            organization.device_group = dg
            organization.save()
            return HttpResponseRedirect(UserGroupCreate.success_url)
        return super(ModelFormMixin, self).form_valid(form)


class UserGroupUpdate(UpdateView):
    template_name = 'ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    def form_valid(self, form):

        # restrict form from updating
        self.object = form.save(commit=False)

        # updating parent --> FK Relation
        try:
            parent_user_group = UserGroup.objects.get(name=form.cleaned_data['parent'])
            self.object.parent = parent_user_group
            self.object.save()
        except:
            print "UserGroup has no parent."

        # delete old relationship exist in Organization Model
        Organization.objects.filter(user_group=self.object).delete()

        # updating device_group --> M2M Relation (Model: Organization)
        for dg in form.cleaned_data['device_group']:
            organization = Organization()
            organization.user_group = self.object
            organization.device_group = dg
            organization.save()
            return HttpResponseRedirect(UserGroupUpdate.success_url)
        return super(ModelFormMixin, self).form_valid(form)


class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'ug_delete.html'
    success_url = reverse_lazy('ug_list')

