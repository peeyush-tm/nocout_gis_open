from django.shortcuts import render
import json
from actstream import action
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.utils.util import DictDiffer
from models import Antenna, BaseStation, Backhaul, Sector, Customer
from forms import AntennaForm, BaseStationForm, BackhaulForm, SectorForm, CustomerForm


def inventory(request):
    return render(request,'inventory/inventory.html')

class AntennaList(ListView):
    model = Antenna
    template_name = 'antenna/antenna_list.html'

    def get_context_data(self, **kwargs):
        context=super(AntennaList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',              'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'height',            'sTitle' : 'Height',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'polarization',      'sTitle' : 'Polarization',     'sWidth':'null',},
            {'mData':'tilt',              'sTitle' : 'Tilt',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',           'sTitle' : 'Actions',          'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class AntennaListingTable(BaseDatatableView):
    model = AntennaList
    columns = ['name', 'height', 'polarization', 'tilt', 'beam_width']
    order_columns = ['name', 'height', 'polarization', 'tilt', 'beam_width']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
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
        return Antenna.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/antenna/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/antenna/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class AntennaDetail(DetailView):
    model = Antenna
    template_name = 'antenna/antenna_detail.html'


class AntennaCreate(CreateView):
    template_name = 'antenna/antenna_new.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(AntennaCreate.success_url)


class AntennaUpdate(UpdateView):
    template_name = 'antenna/antenna_update.html'
    model = Antenna
    form_class = AntennaForm
    success_url = reverse_lazy('antennas_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        print "************************************************************"
        print 'initial_field_dict', initial_field_dict
        print 'cleaned_data_field_dict', cleaned_data_field_dict

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Antenna : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( AntennaUpdate.success_url )

class AntennaDelete(DeleteView):
    model = Antenna
    template_name = 'antenna/antenna_delete.html'
    success_url = reverse_lazy('antennas_list')


class BaseStationList(ListView):
    model = BaseStation
    template_name = 'base_station/base_stations_list.html'

    def get_context_data(self, **kwargs):
        context=super(BaseStationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'bs_site_name',              'sTitle' : 'Base Site Name',                'sWidth':'null',},
            {'mData':'bs_switch',                 'sTitle' : 'Base Switch Name',    'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'backhaul',                  'sTitle' : 'Backhaul',            'sWidth':'null',},
            {'mData':'bs_type',                   'sTitle' : 'Base Station Type',   'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'building_height',           'sTitle' : 'Building Height',     'sWidth':'null',},
            {'mData':'description',               'sTitle' : 'Description',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',                   'sTitle' : 'Actions',             'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class BaseStationListingTable(BaseDatatableView):
    model = BaseStationList
    columns = ['bs_site_name', 'bs_switch', 'backhaul', 'bs_type', 'building_height', 'description']
    order_columns = ['bs_site_name', 'bs_switch', 'backhaul', 'bs_type', 'building_height', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
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
        return BaseStation.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/base_station/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/base_station/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class BaseStationDetail(DetailView):
    model = BaseStation
    template_name = 'base_station/base_station_detail.html'


class BaseStationCreate(CreateView):
    template_name = 'base_station/base_station_new.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(BaseStationCreate.success_url)


class BaseStationUpdate(UpdateView):
    template_name = 'base_station/base_station_update.html'
    model = BaseStation
    form_class = BaseStationForm
    success_url = reverse_lazy('base_stations_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        print "************************************************************"
        print 'initial_field_dict', initial_field_dict
        print 'cleaned_data_field_dict', cleaned_data_field_dict

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Base Station : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( BaseStationUpdate.success_url )

class BaseStationDelete(DeleteView):
    model = BaseStation
    template_name = 'base_station/base_station_delete.html'
    success_url = reverse_lazy('base_stations_list')
    
    
class BackhaulList(ListView):
    model = Backhaul
    template_name = 'backhaul/backhauls_list.html'

    def get_context_data(self, **kwargs):
        context=super(BackhaulList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'bh_configured_on',        'sTitle' : 'Backhaul Configured On',       'sWidth':'null',},
            {'mData':'bh_port',                 'sTitle' : 'Backhaul Port',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'bh_type',                 'sTitle' : 'Backhaul Type',                'sWidth':'null',},
            {'mData':'pop',                     'sTitle' : 'POP',                          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'pop_port',                'sTitle' : 'POP Port',                     'sWidth':'null',},
            {'mData':'bh_connectivity',         'sTitle' : 'Connectivity',                 'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'bh_circuit_id',           'sTitle' : 'Circuit ID',                   'sWidth':'null',},
            {'mData':'bh_capacity',             'sTitle' : 'Capacity',                     'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',                 'sTitle' : 'Actions',                      'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class BackhaulListingTable(BaseDatatableView):
    model = BackhaulList
    columns = ['bh_configured_on', 'bh_port', 'bh_type', 'pop', 'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']
    order_columns = ['bh_configured_on', 'bh_port', 'bh_type', 'pop', 'pop_port', 'bh_connectivity', 'bh_circuit_id', 'bh_capacity']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
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
        return Backhaul.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/backhaul/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/backhaul/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class BackhaulDetail(DetailView):
    model = Backhaul
    template_name = 'backhaul/backhaul_detail.html'


class BackhaulCreate(CreateView):
    template_name = 'backhaul/backhaul_new.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(BackhaulCreate.success_url)


class BackhaulUpdate(UpdateView):
    template_name = 'backhaul/backhaul_update.html'
    model = Backhaul
    form_class = BackhaulForm
    success_url = reverse_lazy('backhauls_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        print "************************************************************"
        print 'initial_field_dict', initial_field_dict
        print 'cleaned_data_field_dict', cleaned_data_field_dict

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Backhaul : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( BackhaulUpdate.success_url )

class BackhaulDelete(DeleteView):
    model = Backhaul
    template_name = 'backhaul/backhaul_delete.html'
    success_url = reverse_lazy('backhauls_list')
    
    
class SectorList(ListView):
    model = Sector
    template_name = 'sector/sectors_list.html'

    def get_context_data(self, **kwargs):
        context=super(SectorList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',          'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'sector_id',     'sTitle' : 'ID',               'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'base_station',  'sTitle' : 'Base Station',     'sWidth':'null',},
            {'mData':'idu',           'sTitle' : 'IDU',              'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'odu',           'sTitle' : 'ODU',              'sWidth':'null',},
            {'mData':'antenna',       'sTitle' : 'Antenna',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'mrc',           'sTitle' : 'MRC',              'sWidth':'null',},
            {'mData':'description',   'sTitle' : 'Description',      'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'actions',       'sTitle' : 'Actions',          'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class SectorListingTable(BaseDatatableView):
    model = SectorList
    columns = ['name', 'sector_id', 'base_station', 'idu', 'odu', 'antenna', 'mrc', 'description']
    order_columns = ['name', 'sector_id', 'base_station', 'idu', 'odu', 'antenna', 'mrc', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
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
        return Sector.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/sector/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/sector/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class SectorDetail(DetailView):
    model = Sector
    template_name = 'sector/sector_detail.html'


class SectorCreate(CreateView):
    template_name = 'sector/sector_new.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(SectorCreate.success_url)


class SectorUpdate(UpdateView):
    template_name = 'sector/sector_update.html'
    model = Sector
    form_class = SectorForm
    success_url = reverse_lazy('sectors_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        print "************************************************************"
        print 'initial_field_dict', initial_field_dict
        print 'cleaned_data_field_dict', cleaned_data_field_dict

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Sector : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( SectorUpdate.success_url )

class SectorDelete(DeleteView):
    model = Sector
    template_name = 'sector/sector_delete.html'
    success_url = reverse_lazy('sectors_list')
    
    
class CustomerList(ListView):
    model = Customer
    template_name = 'customer/customers_list.html'

    def get_context_data(self, **kwargs):
        context=super(CustomerList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'name',              'sTitle' : 'Name',             'sWidth':'null',},
            {'mData':'city',              'sTitle' : 'City',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'state',             'sTitle' : 'State',            'sWidth':'null',},
            {'mData':'address',           'sTitle' : 'Address',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'description',       'sTitle' : 'Description',      'sWidth':'null',},
            {'mData':'actions',           'sTitle' : 'Actions',          'sWidth':'10%' ,}
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class CustomerListingTable(BaseDatatableView):
    model = CustomerList
    columns = ['name', 'city', 'state', 'address', 'description']
    order_columns = ['name', 'city', 'state', 'address', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
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
        return Customer.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/customer/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/customer/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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

class CustomerDetail(DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'


class CustomerCreate(CreateView):
    template_name = 'customer/customer_new.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')

    def form_valid(self, form):
        self.object=form.save()
        action.send(self.request.user, verb='Created', action_object = self.object)
        return HttpResponseRedirect(CustomerCreate.success_url)


class CustomerUpdate(UpdateView):
    template_name = 'customer/customer_update.html'
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('customers_list')


    def form_valid(self, form):
        initial_field_dict = { field : form.initial[field] for field in form.initial.keys() }

        cleaned_data_field_dict = { field : form.cleaned_data[field]  for field in form.cleaned_data.keys() }

        print "************************************************************"
        print 'initial_field_dict', initial_field_dict
        print 'cleaned_data_field_dict', cleaned_data_field_dict

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Customer : %s from initial values '%(self.object.name) + ', '.join(['%s: %s' %(k, initial_field_dict[k]) \
                               for k in changed_fields_dict])+\
                               ' to '+\
                               ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object=form.save()
            action.send( self.request.user, verb=verb_string )
        return HttpResponseRedirect( CustomerUpdate.success_url )

class CustomerDelete(DeleteView):
    model = Customer
    template_name = 'customer/customer_delete.html'
    success_url = reverse_lazy('customers_list')