from actstream import action
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device_group.models import DeviceGroup
from nocout.utils.util import DictDiffer
from user_group.models import UserGroup, Organization
from forms import UserGroupForm
from user_profile.models import UserProfile


class UserGroupList(ListView):
    model = UserGroup
    template_name = 'user_group/ug_list.html'

    def get_context_data(self, **kwargs):
        context=super(UserGroupList, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'name',                   'sTitle' : 'Name',                  'sWidth':'null',},
            {'mData':'alias',                  'sTitle' : 'Alias',                 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'address',                'sTitle' : 'Addres',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'location',               'sTitle' : 'Location',              'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'parent__name',           'sTitle' : 'Parent Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'organization__name',     'sTitle' : 'Organization',          'sWidth':'null','sClass':'hidden-xs'},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%' ,})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class UserGroupListingTable(BaseDatatableView):
    model = UserGroup
    columns = ['name', 'alias', 'address', 'location', 'parent__name','organization__name']
    order_columns = ['name', 'alias', 'address', 'location', 'parent__name', 'organization__name']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= self.request.user.userprofile.organization.get_descendants(include_self=True).values_list('id', flat=True)
        return UserGroup.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/user_group/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="#" onclick="Dajaxice.user_group.user_group_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret

class UserGroupDetail(DetailView):
    model = UserGroup
    template_name = 'user_group/ug_detail.html'

class UserGroupCreate(CreateView):
    template_name = 'user_group/ug_new.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    @method_decorator(permission_required('user_group.add_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserGroupCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb=u'created', action_object=self.object)
        return super(ModelFormMixin, self).form_valid(form)

class UserGroupUpdate(UpdateView):
    template_name = 'user_group/ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')


    @method_decorator(permission_required('user_group.change_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserGroupUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #IntegrityError: (1062, "Duplicate entry 'test_group4' for key 'name'")
        #TODO:Disable the edit of name from the UI (name should be unique)
        self.object = form.save()

        #User Activity log
        initial_field_dict=form.initial

        cleaned_data_field_dict={}
        for field in form.cleaned_data.keys():
            if field =='users':
                cleaned_data_field_dict[field]= map(lambda query_set: query_set.id, form.cleaned_data[field])
            elif field in ('organization','parent'):
                cleaned_data_field_dict[field]= form.cleaned_data[field].id
            else:
                cleaned_data_field_dict[field]=form.cleaned_data[field]

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            initial_field_dict['parent'] = UserGroup.objects.get(pk=initial_field_dict['parent']).name \
                if initial_field_dict['parent'] else str(None)
            initial_field_dict['organization'] = Organization.objects.get(pk=initial_field_dict['organization']).name \
                if initial_field_dict['organization'] else str(None)
            initial_field_dict['users'] = ', '.join(UserProfile.objects.filter(pk__in=initial_field_dict['users']).values_list('username', flat=True)) \
                if initial_field_dict['users'] else str(None)

            cleaned_data_field_dict['parent'] = UserGroup.objects.get(pk=cleaned_data_field_dict['parent']).name \
                if cleaned_data_field_dict['parent'] else str(None)
            cleaned_data_field_dict['organization'] = Organization.objects.get(pk=cleaned_data_field_dict['organization']).name \
                if cleaned_data_field_dict['organization'] else str(None)
            cleaned_data_field_dict['users'] = ', '.join(UserProfile.objects.filter(pk__in= cleaned_data_field_dict['users']).values_list('username', flat=True)) \
                                                             if cleaned_data_field_dict['users'] else str(None)

            verb_string = 'Changed values of User Group %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            action.send(self.request.user, verb=verb_string)

        return super(ModelFormMixin, self).form_valid(form)



class UserGroupDelete(DeleteView):
    model = UserGroup
    template_name = 'user_group/ug_delete.html'
    success_url = reverse_lazy('ug_list')

    @method_decorator(permission_required('user_group.delete_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UserGroupDelete, self).dispatch(*args, **kwargs)


    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting user group: %s'%(self.object.name))
        super(UserGroupDelete, self).delete(self, request, *args, **kwargs)

def user_group_users_render_wrt_organization(request):
    organization_id= request.GET['organization']
    organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
    user_profile=UserProfile.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values_list('id','username')
    response_string=''
    for index in range(len(user_profile)):
        response_string+='<option value={0}>{1}</option>'.format(*map(str, user_profile[index]))

    return HttpResponse(json.dumps({'response':response_string}), mimetype='application/json')
