from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from user_profile.models import UserProfile, Department
from forms import UserForm
from django.http.response import HttpResponseRedirect
from django.contrib.auth.hashers import make_password


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
    
    def form_valid(self, form):
        user_profile = UserProfile()
        user_profile.username = form.cleaned_data['username']
        user_profile.first_name = form.cleaned_data['first_name']
        user_profile.last_name = form.cleaned_data['last_name']
        user_profile.email = form.cleaned_data['email']
        user_profile.password = make_password(form.cleaned_data['password1'])
        user_profile.role = form.cleaned_data['role']
        user_profile.phone_number = form.cleaned_data['phone_number']
        user_profile.company = form.cleaned_data['company']
        user_profile.designation = form.cleaned_data['designation']
        user_profile.address = form.cleaned_data['address']
        user_profile.comment = form.cleaned_data['comment']
        user_profile.save()
        
        # saving parent --> FK Relation
        try:
            parent_user = UserProfile.objects.get(username=form.cleaned_data['parent'])
            user_profile.parent = parent_user
            user_profile.save()
        except:
            print "User has no parent."
        
        # saving user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = user_profile
            department.user_group = ug
            department.save()
            return HttpResponseRedirect(UserCreate.success_url)
        return super(ModelFormMixin, self).form_valid(form)
        

class UserUpdate(UpdateView):
    template_name = 'user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        
        # saving form from updating
        self.object = form.save(commit=False)
        
        # delete old relationship exist in department
        Department.objects.filter(user_profile=self.object).delete()
        
        # updating user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = self.object
            department.user_group = ug
            department.save()
            return HttpResponseRedirect(UserUpdate.success_url)
        return super(ModelFormMixin, self).form_valid(form)


class UserDelete(DeleteView):
    model = UserProfile
    template_name = 'user_delete.html'
    success_url = reverse_lazy('user_list')
    
    