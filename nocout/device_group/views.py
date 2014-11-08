import json
from operator import itemgetter
from django.db.models.query import ValuesQuerySet
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device
from device_group.models import DeviceGroup
from forms import DeviceGroupForm
from django.db.models import Q
from nocout.utils.util import DictDiffer
from organization.models import Organization
from nocout.mixins.permissions import PermissionsRequiredMixin


class DeviceGroupList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render DeviceGroup List Page.
    """
    model = DeviceGroup
    template_name = 'device_group/dg_list.html'
    required_permissions = ('device_group.view_devicegroup',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(DeviceGroupList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',                   'sTitle' : 'Name',              'sWidth':'auto',},
            {'mData':'alias',                  'sTitle' : 'Alias',             'sWidth':'auto','sClass':'hidden-xs'},
            {'mData':'parent__name',           'sTitle' : 'Parent ',           'sWidth':'auto',},
            {'mData':'organization__name',     'sTitle' : 'Organization',      'sWidth':'auto',},]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DeviceGroupListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class based View to render Device Group Data table.
    """
    model = DeviceGroup
    required_permissions = ('device_group.view_devicegroup',)
    columns = ['name', 'alias', 'parent__name','organization__name']
    order_columns = ['name', 'alias', 'parent__name','organization__name']

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
        return DeviceGroup.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values(*self.columns+['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/device_group/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="#" onclick="Dajaxice.device_group.device_group_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
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

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return sorted(qs, key= itemgetter(order[0][1:]), reverse= True if '-' in order[0] else False)
        return qs


    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
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


class DeviceGroupDetail(PermissionsRequiredMixin, DetailView):
    """
    Class based view to render the Device group detail.
    """
    model = DeviceGroup
    required_permissions = ('device_group.view_devicegroup',)
    template_name = 'device_group/dg_detail.html'


class DeviceGroupCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based view to create new Device group.
    """
    template_name = 'device_group/dg_new.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')
    required_permissions = ('device_group.add_devicegroup',)

    def form_valid( self, form ):
        """
        Submit the form and to log the user activity.
        """
        self.object=form.save()
        return HttpResponseRedirect( DeviceGroupCreate.success_url )


class DeviceGroupUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based view to update machine.
    """
    template_name = 'device_group/dg_update.html'
    model = DeviceGroup
    form_class = DeviceGroupForm
    success_url = reverse_lazy('dg_list')
    required_permissions = ('device_group.change_devicegroup',)

    def form_valid( self, form ):
        """
        Submit the form and to log the user activity.
        """
        try:
            initial_field_dict = form.initial

            cleaned_data_field_dict={}
            for field in form.cleaned_data.keys():
                if field =='devices':
                    cleaned_data_field_dict[field]=map(lambda obj: obj.pk, form.cleaned_data[field])
                elif field in ('parent','organization'):
                    cleaned_data_field_dict[field]= form.cleaned_data[field].pk if form.cleaned_data[field] else None
                else:
                    cleaned_data_field_dict[field]= form.cleaned_data[field]

            changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()

            if changed_fields_dict:
                initial_field_dict['parent'] = DeviceGroup.objects.get(pk=initial_field_dict['parent']).name \
                    if initial_field_dict['parent'] else str(None)
                initial_field_dict['organization'] = Organization.objects.get(pk=initial_field_dict['organization']).name \
                    if initial_field_dict['organization'] else str(None)
                initial_field_dict['devices'] = ', '.join([Device.objects.get(pk=device).device_name for device in initial_field_dict['devices']])\
                    if initial_field_dict['devices'] else str(None)

                cleaned_data_field_dict['parent']= DeviceGroup.objects.get(pk=cleaned_data_field_dict['parent']).name \
                    if cleaned_data_field_dict['parent'] else str(None)
                cleaned_data_field_dict['organization']= Organization.objects.get(pk=cleaned_data_field_dict['organization']).name \
                    if cleaned_data_field_dict['organization'] else str(None)
                cleaned_data_field_dict['devices'] = ', '.join([Device.objects.get(pk=device).device_name for device in cleaned_data_field_dict['devices']])\
                    if cleaned_data_field_dict['devices'] else str(None)

                verb_string = 'Changed values of Device Group: %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                                   for k in changed_fields_dict])+\
                                   ' to '+\
                                   ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
                if len(verb_string)>=255:
                    verb_string=verb_string[:250] + '...'


        except Exception as activity:
            pass

        self.object=form.save()

        return HttpResponseRedirect( DeviceGroupCreate.success_url )


class DeviceGroupDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class based View to delete the Device Group
    """
    model = DeviceGroup
    template_name = 'device_group/dg_delete.html'
    success_url = reverse_lazy('dg_list')
    required_permissions = ('device_group.delete_devicegroup',)

    def delete(self, request, *args, **kwargs):
        """
        overriding the delete method to log the user activity.
        """
        return super(DeviceGroupDelete, self).delete(request, *args, **kwargs)


def device_group_devices_wrt_organization(request):
    """
    Fetches Device Group w.r.t to the organization and its descendants.
    """
    organization_id= request.GET['organization']
    organization_descendants_ids= Organization.objects.get(id= organization_id).get_descendants(include_self=True).values_list('id', flat=True)
    devices=Device.objects.filter(organization__in = organization_descendants_ids, is_deleted=0).values_list('id','device_name')
    response_string=''
    for index in range(len(devices)):
        response_string+='<option value={0}>{1}</option>'.format(*map(str, devices[index]))

    return HttpResponse(json.dumps({'response': response_string }), mimetype='application/json')
