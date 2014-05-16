from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from user_profile.models import UserProfile, Department, Roles
from forms import UserForm
from django.http.response import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
import json, datetime

date_handler = lambda obj: obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(obj, datetime.datetime) else None


class UserList(ListView):
    model = UserProfile
    template_name = 'user_profile/users_list.html'

    def get_queryset(self):

        queryset = self.model._default_manager.values('username','first_name','last_name','email','role',
                                           'user_group__name','parent__first_name','parent__last_name','phone_number','last_login')
        return queryset[:10]

    def get_context_data(self, **kwargs):
        context=super(UserList, self).get_context_data(**kwargs)
        ############################REQUIRED TO DEBUG IF REQUIRED(Code is yet not freezed )######################
        # object_list=context['object_list']
        # object_list_headers = [{"mData": "applicationName", "sTitle" : "Application Name" },
        #                 { "mData" :"ipAddress", "sTitle" : "Application Name"},
        #                 { "mData" :"url", "sTitle" : "URL"},
        #                 { "mData" :"noOfCustomer", "sTitle" : "No. of Customers"},
        #                 { "mData" :"roamingDrop", "sTitle" : "Roaming Drop"},]
        #
        # object_list=[{'applicationName': "ATM Monitoring",
        #                 'roamingDrop': "",
        #                 'noOfCustomer': 50,
        #                 'ipAddress': "192.168.1.1",
        #                  'url': "www.google.co.in",}]
        # object_list = context['object_list']
        # object_list = [ dict([ (key,value) if value else ( key,'') for object in object_list for key, value in object.iteritems() ])]
        #######################################################################################################
        object_list = [{ key: val if val else "" for key, val in dct.items() } for dct in context['object_list']]

        object_list_sanity = lambda dict_final_key, dict_first_key, dict_last_key :[  dct.__setitem__(dict_final_key,
                                dct.pop(dict_first_key) + ' ' + dct.pop(dict_last_key)) for dct in object_list ]

        object_list_sanity('full_name','first_name','last_name')
        object_list_sanity('manager_name','parent__first_name','parent__last_name')

        object_list_headers = [ dict(mData=key, sTitle=key.replace('_',' ').title()) for key in object_list[0].keys() ]

        context['object_list'] = json.dumps(object_list,default=date_handler)
        context.update({
            'object_list_headers' : json.dumps(object_list_headers, default=date_handler)
        })

        return context

class UserDetail(DetailView):
    model = UserProfile
    template_name = 'user_profile/user_detail.html'


class UserCreate(CreateView):
    template_name = 'user_profile/user_new.html'
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

        # creating roles  --> M2M Relation (Model: Roles)
        for role in form.cleaned_data['role']:
            user_role = Roles.objects.get(role_name=role)
            user_profile.role.add(user_role)
            user_profile.save()

        # saving user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = user_profile
            department.user_group = ug
            department.save()
        return HttpResponseRedirect(UserCreate.success_url)


class UserUpdate(UpdateView):
    template_name = 'user_profile/user_update.html'
    model = UserProfile
    form_class = UserForm
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        self.object.username = form.cleaned_data['username']
        self.object.first_name = form.cleaned_data['first_name']
        self.object.last_name = form.cleaned_data['last_name']
        self.object.email = form.cleaned_data['email']
        self.object.password = make_password(form.cleaned_data['password1'])
        self.object.phone_number = form.cleaned_data['phone_number']
        self.object.company = form.cleaned_data['company']
        self.object.designation = form.cleaned_data['designation']
        self.object.address = form.cleaned_data['address']
        self.object.comment = form.cleaned_data['comment']
        self.object.save()

        # updating parent --> FK Relation
        try:
            parent_user = UserProfile.objects.get(username=form.cleaned_data['parent'])
            self.object.parent = parent_user
            self.object.save()
        except:
            print "User has no parent."

        # deleting old roles of user
        self.object.role.clear()

        # updating roles  --> M2M Relation (Model: Roles)
        for role in form.cleaned_data['role']:
            user_role = Roles.objects.get(role_name=role)
            self.object.role.add(user_role)
            self.object.save()

        # delete old relationship exist in department
        Department.objects.filter(user_profile=self.object).delete()

        # updating user_group --> M2M Relation (Model: Department)
        for ug in form.cleaned_data['user_group']:
            department = Department()
            department.user_profile = self.object
            department.user_group = ug
            department.save()
        return HttpResponseRedirect(UserCreate.success_url)


class UserDelete(DeleteView):
    model = UserProfile
    template_name = 'user_profile/user_delete.html'
    success_url = reverse_lazy('user_list')

