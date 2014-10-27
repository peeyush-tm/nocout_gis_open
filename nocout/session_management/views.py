from collections import OrderedDict
import json
from operator import itemgetter
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.views.generic import ListView
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from session_management.models import Visitor
from django.contrib import auth
from user_profile.models import UserProfile
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

class UserStatusList(ListView):
    """
    Class Based View to list the User Status of logged in.
    """
    model = UserProfile
    template_name = 'session_management/users_status_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(UserStatusList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'username', 'sTitle': 'Username', 'sWidth': 'auto', },
            {'mData': 'full_name', 'sTitle': 'Full Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'role__role_name', 'sTitle': 'Role', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'logged_in_status', 'sTitle': 'Logged in', 'sWidth': 'auto','bSortable': False },]

        #if the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'8%' ,'bSortable': False })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class UserStatusTable(BaseDatatableView):
    """
    Class based View to render User Status Data table.
    """
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'role__role_name']
    order_columns = ['username', 'first_name', 'role__role_name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            logged_in_users_ids = [visitor.user_id for visitor in Visitor.objects.all()]
            for dictionary in qs:
                #Adding the logged_in_status key to search in the dictionary.
                dictionary['logged_in_status']= 'YES' if dictionary['id'] in logged_in_users_ids else 'NO'
                for key in dictionary.keys():
                    if key=='is_active': continue
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        dictionary.pop('logged_in_status')
                        break

                if 'logged_in_status' in dictionary: dictionary.pop('logged_in_status')
            return result_list

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        logged_in_user= self.request.user.userprofile
        organization_descendants_ids= list(logged_in_user.organization.get_descendants(include_self=True)
                                    .values_list('id', flat=True))

        return UserProfile.objects.exclude(id= logged_in_user.id).filter(organization__in = \
               organization_descendants_ids, is_deleted=0).values(*self.columns+['id', 'is_active'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            sanity_dicts_list = [
                OrderedDict({'dict_final_key': 'full_name', 'dict_key1': 'first_name', 'dict_key2': 'last_name'})]
            qs, qs_headers = Datatable_Generation(qs, sanity_dicts_list).main()
            logged_in_users_ids = [visitor.user_id for visitor in Visitor.objects.all()]
            for dct in qs:
                dct.update(actions='<h3 class="fa fa-lock text-danger" onclick="change_user_status(this);"> &nbsp;</h3>'
                           if dct.get('is_active') else '<h3 class="fa fa-unlock text-success" \
                           onclick="change_user_status(this);"> &nbsp;</h3>', logged_in_status='NO')
                if dct.pop('id') in logged_in_users_ids:
                    dct['actions'] += '<h3 class="fa fa-sign-out text-danger" onclick="logout_user(this);"> &nbsp;</h3>'
                    dct['logged_in_status'] = 'YES'

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
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret

@csrf_exempt
def dialog_action(request):
    """
    The Action of the Dialog box appears on the screen.
    If the action is continue then the user will get logged off from the current logged in session
    and the same session key will be used to login the user.

    """
    url = request.POST.get('url', '/home/')
    if request.POST.get('action') == 'continue':
        session_key = request.session.session_key
        if hasattr(request.user, 'visitor'):
            Session.objects.filter(session_key=request.user.visitor.session_key).delete()
        Visitor.objects.create(session_key=session_key, user=request.user)
        result = {
            "success": 1,  # 0 - fail, 1 - success, 2 - exception
            "message": "Success/Fail message.",
            "data": {
                "meta": {},
                "objects": {
                    'url': url
                }
            }
        }
        return HttpResponse(json.dumps(result), mimetype='application/json')

    elif request.POST.get('action') == 'logout':
        #since we are having auto-logoff functionality with us as well
        #we need to check for session parameter _session_security
        #_session_security is used by session security to judge the
        #auto logoff of the user
        if '_session_security' in request.session:
            del request.session["_session_security"]

        auth.logout(request)
        result = {
            "success": 1,  # 0 - fail, 1 - success, 2 - exception
            "message": "Success/Fail message.",
            "data": {
                "meta": {},
                "objects": {
                    'url': '/login/'
                }
            }
        }
        return HttpResponse(json.dumps(result), mimetype='application/json')

@csrf_exempt
def change_user_status(request):
    """

    :param request:the django request
    :return: the response for user lock down, with success 1 as successful
    """
    user_name = request.POST.get('user_name')
    user = UserProfile.objects.filter(username=user_name)
    if user[0].is_active:
        status = False
    else:
        status = True

    user.update(is_active=status)

    result = {
        "success": 1,  # 0 - fail, 1 - success, 2 - exception
        "message": "Success/Fail message.",
        "data": {
            "meta": {},
            "objects": {
                'status': status,
            }
        }
    }

    return HttpResponse(json.dumps(result), mimetype='application/json')

@csrf_exempt
def dialog_for_page_refresh(request):
    """
        The Ajax request to refresh the page is user status is changed to not active.
        or the user session key does not exist any more in the Visitor table.
    """
    dialog_confirmation = False
    if not request.user.is_active or request.user.is_anonymous():
        dialog_confirmation = True

    result = {
        "success": 1,  # 0 - fail, 1 - success, 2 - exception
        "message": "Success/Fail message.",
        "data": {
            "meta": {},
            "objects": {
                'dialog': dialog_confirmation
            }
        }
    }

    return HttpResponse(json.dumps(result), mimetype='application/json')

@csrf_exempt
def dialog_expired_logout_user(request):
    """
    To logout the user if the dialog appearing with the timestamp expires.
    """
    if not request.user.is_anonymous():
        logout(request)
    result = {
        "success": 1,  # 0 - fail, 1 - success, 2 - exception
        "message": "Success/Fail message.",
        "data": {
            "meta": {},
            "objects": {
                'refresh': True
            }
        }
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')

@csrf_exempt
def logout_user(request):
    """
    request to logout the user from the system.
    """
    user_name = request.POST.get('user_name')
    user = UserProfile.objects.get(username=user_name)
    Session.objects.filter(session_key=user.visitor.session_key).delete()
    result = {
        "success": 1,  # 0 - fail, 1 - success, 2 - exception
        "message": "Success/Fail message.",
        "data": {
            "meta": {},
            "objects": {}
        }
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')




