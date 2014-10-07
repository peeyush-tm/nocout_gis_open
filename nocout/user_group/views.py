from operator import itemgetter
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
    """
    Class Based View to list User Group
    """
    model = UserGroup
    template_name = 'user_group/ug_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(UserGroupList, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'name',                   'sTitle' : 'Name',                  'sWidth':'auto',},
            {'mData':'alias',                  'sTitle' : 'Alias',                 'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'organization__name',     'sTitle' : 'Organization',          'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'users__first_name',      'sTitle' : 'Users',                 'sWidth':'auto','sClass':'hidden-xs','bSortable': False},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%' ,'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class UserGroupListingTable(BaseDatatableView):
    """
    Class Based View for the User Group data table rendering.
    """
    model = UserGroup
    columns = ['name', 'alias', 'users__first_name','organization__name']
    order_columns = ['name', 'alias','organization__name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        break
            return result_list

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= list(self.request.user.userprofile.organization.get_descendants(include_self=True)
                                      .values_list('id', flat=True))
        qs_query= UserGroup.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).prefetch_related()
        qs=list()
        for ug in qs_query:
            qs.append( {'id':ug.id,
                        'name': ug.name,
                        'alias': ug.alias,
                        'organization__name':ug.organization.name,
                        'users__first_name': ', '.join( ug.users.values_list('first_name', flat=True)) },
                       )
        return qs

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/user_group/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="#" onclick="Dajaxice.user_group.user_group_soft_delete_form(get_soft_delete_form, {{\'value\': \
                {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def ordering(self, qs):
        """
        Sort the qs with respect to the columns required in the queryset,
        If Nothing is specified then by default the ordering will be done on the basis of first column
        in the data table.
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except ValueError:
            i_sorting_cols = 0

        order = []
        order_columns = self.get_order_columns()
        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except ValueError:
                i_sort_col = 0
            # sorting order
            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

            sdir = '-' if s_sort_dir == 'desc' else ' '
            try:
                sortcol = order_columns[i_sort_col]
            except IndexError:
                return qs
            #for the mutiple sorting of the columns at a time
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key=itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

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
    """
    Class Based View to render the User Group Detail Information.
    """
    model = UserGroup
    template_name = 'user_group/ug_detail.html'

class UserGroupCreate(CreateView):
    """
    Class Based View to Create the User Group.
    """
    template_name = 'user_group/ug_new.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')

    @method_decorator(permission_required('user_group.add_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(UserGroupCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        to log the user activity after submitting the form.
        """
        self.object = form.save()
        try:
            action.send(self.request.user, verb=u'created', action_object=self.object)
        except Exception as activity:
            pass
        return super(ModelFormMixin, self).form_valid(form)

class UserGroupUpdate(UpdateView):
    """
    Class Based View to Update the User Group.
    """
    template_name = 'user_group/ug_update.html'
    model = UserGroup
    form_class = UserGroupForm
    success_url = reverse_lazy('ug_list')


    @method_decorator(permission_required('user_group.change_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch function restricted with the permissions.
        """
        return super(UserGroupUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        To log the user activity after submitting.
        """
        #IntegrityError: (1062, "Duplicate entry 'test_group4' for key 'name'")
        #TODO:Disable the edit of name from the UI (name should be unique)
        self.object = form.save()

        #User Activity log
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of User group : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            self.object=form.save()
            try:
                action.send( self.request.user, verb=verb_string )
            except Exception as activity:
                pass

        return super(ModelFormMixin, self).form_valid(form)



class UserGroupDelete(DeleteView):
    """
    Class based View to delete the User Group
    """
    model = UserGroup
    template_name = 'user_group/ug_delete.html'
    success_url = reverse_lazy('ug_list')

    @method_decorator(permission_required('user_group.delete_usergroup', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(UserGroupDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        The delete function to overriding to log the user activity.
        """
        try:
            action.send(request.user, verb='deleting user group: %s'%(self.get_object().name))
        except Exception as activity:
            pass
        return super(UserGroupDelete, self).delete(request, *args, **kwargs)

def user_group_users_render_wrt_organization(request):
    """
    To fetch the User w.r.t to the organization required to save in the m2m field in the UserGroup.
    """
    organization_id= request.GET['organization']
    organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
    user_profile= UserProfile.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values_list('id','username')
    response_string=''
    for index in range(len(user_profile)):
        response_string+= '<option value={0}>{1}</option>'.format(*map(str, user_profile[index]))

    return HttpResponse(json.dumps({'response':response_string}), mimetype='application/json')
