import json
from django.db.models.query import ValuesQuerySet
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device_group.models import DeviceGroup
from .forms import OrganizationForm
from .models import Organization
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.utils.util import date_handler, DictDiffer
from user_group.models import UserGroup
from nocout.utils import logged_in_user_organizations
from activity_stream.models import UserAction
from nocout.mixins.permissions import PermissionsRequiredMixin


class OrganizationList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render Organization List page.
    """

    model = Organization
    template_name = 'organization/organization_list.html'
    required_permissions = ('organization.view_organization',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(OrganizationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                'sTitle' : 'Name',          'sWidth':'auto'},
            {'mData':'alias',               'sTitle' : 'Alias',         'sWidth':'auto'},
            {'mData':'parent__name',        'sTitle' : 'Parent',        'sWidth':'auto'},
            {'mData':'city',                'sTitle' : 'City',          'sWidth':'auto'},
            {'mData':'state',               'sTitle' : 'State',         'sWidth':'auto'},
            {'mData':'country',             'sTitle' : 'Country',       'sWidth':'auto'},
            {'mData':'description',         'sTitle' : 'Description',   'sWidth':'auto','bSortable': False}]

        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%','bSortable': False })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class OrganizationListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class based View to render Organization Data table.
    """
    model = Organization
    required_permissions = ('organization.view_organization',)
    columns = ['name', 'alias', 'parent__name','city','state','country', 'description']
    order_columns = ['name',  'alias', 'parent__name', 'city', 'state', 'country']

    def logged_in_user_organization_ids(self):
        """
        return the logged in user descendants organization ids.
        """
        if self.request.user.userprofile.role.values_list( 'role_name', flat=True )[0] =='admin':
            return list(self.request.user.userprofile.organization.get_descendants(include_self=True).values_list('id', flat=True))
        else:
            return list(str(self.request.user.userprofile.organization.id))

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            sSearch = sSearch.replace("\\", "")
            query=[]
            organization_descendants_ids= self.logged_in_user_organization_ids()
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query) + ", id__in = %s"%organization_descendants_ids + \
                          ").values(*"+str(self.columns+['id'])+")"
            exec exec_query
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        organization_descendants_ids= self.logged_in_user_organization_ids()
        return Organization.objects.filter(pk__in=organization_descendants_ids).values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/organization/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/organization/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
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


class OrganizationDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the organization detail.
    """
    model = Organization
    required_permissions = ('organization.view_organization',)
    template_name = 'organization/organization_detail.html'


class OrganizationCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new organization.
    """
    template_name = 'organization/organization_new.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')
    required_permissions = ('organization.add_organization',)


    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        self.object=form.save()
        self.model.objects.rebuild()
        return super(ModelFormMixin, self).form_valid(form)


class OrganizationUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update organization.
    """
    template_name = 'organization/organization_update.html'
    model = Organization
    form_class = OrganizationForm
    success_url = reverse_lazy('organization_list')
    required_permissions = ('organization.change_organization',)

    def get_queryset(self):
        return logged_in_user_organizations(self)

    def form_valid(self, form):
        """
        Submit the form and to log the user activity.
        """
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }
        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Organization : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string)>=255:
                verb_string=verb_string[:250] + '...'

            self.object=form.save()
            self.model.objects.rebuild()
        return HttpResponseRedirect( OrganizationUpdate.success_url )


class OrganizationDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class based View to Delete the Organization.
    """
    model = Organization
    template_name = 'organization/organization_delete.html'
    success_url = reverse_lazy('organization_list')
    required_permissions = ('organization.delete_organization',)

    def get_queryset(self):
        return logged_in_user_organizations(self)

    def delete(self, *args, **kwargs):
        """
        Log the user action as the organisation is deleted.
        """
        try:
            organization_obj = self.get_object()
            action ='A organization is deleted - {}(country- {}, State- {}, City- {})'.format(organization_obj.alias,
                    organization_obj.country, organization_obj.state, organization_obj.city)
            UserAction.objects.create(user_id=self.request.user.id, module='Organization', action=action )
        except:
            pass
        return super(OrganizationDelete, self).delete(*args, **kwargs)
