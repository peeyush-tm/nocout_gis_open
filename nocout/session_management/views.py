"""
=====================================================================================
Module contains views and related functionality specific to 'session_management' app.
=====================================================================================

Location:
* /nocout_gis/nocout/session_management/views.py

List of constructs:
=======
Classes
=======
* UserStatusList
* UserStatusTable

=======
Methods
=======
* dialog_action
* change_user_status
* dialog_for_page_refresh
* dialog_expired_logout_user
* logout_user
"""

import json
from collections import OrderedDict
from operator import itemgetter
from django.contrib import auth
from django.contrib.auth import logout
from django.db.models.query import ValuesQuerySet
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.utils.jquery_datatable_generation import Datatable_Generation
from nocout.mixins.permissions import PermissionsRequiredMixin
from session_management.models import Visitor
from user_profile.models import UserProfile
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway


class UserStatusList(PermissionsRequiredMixin, ListView):
    """
    View to show headers of logged in user status datatable.
        URL - 'http://127.0.0.1:8000/sm/'
    """
    model = UserProfile
    template_name = 'session_management/users_status_list.html'
    required_permissions = ('user_profile.view_userprofile',)

    def get_context_data(self, **kwargs):
        """
        Preparing the context variables required in the template rendering.
        """
        context = super(UserStatusList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'username', 'sTitle': 'Username', 'sWidth': 'auto', },
            {'mData': 'full_name', 'sTitle': 'Full Name', 'sWidth': 'auto'},
            {'mData': 'role__role_name', 'sTitle': 'Role', 'sWidth': 'auto'},
            {'mData': 'logged_in_status', 'sTitle': 'Logged in', 'sWidth': 'auto', 'bSortable': False}
        ]

        # If the user role is Admin then the action column will appear on the datatable
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({
                'mData': 'actions',
                'sTitle': 'Actions',
                'sWidth': '8%',
                'bSortable': False
            })

        context['datatable_headers'] = json.dumps(datatable_headers)

        return context


class UserStatusTable(BaseDatatableView):
    """
    View to show list of logged in user status in datatable.
        URL - 'http://127.0.0.1:8000/sm/'
    """
    model = UserProfile
    columns = ['username', 'first_name', 'last_name', 'role__role_name']
    order_columns = ['username', 'first_name', 'role__role_name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.
        """
        # sSearch = self.request.GET.get('sSearch', None)
        sSearch = self.request.GET.get('search[value]', None)

        if sSearch:
            result_list = list()
            logged_in_users_ids = [visitor.user_id for visitor in Visitor.objects.all()]
            for dictionary in qs:
                # Adding the 'logged_in_status' key to search in the dictionary.
                dictionary['logged_in_status'] = 'YES' if dictionary['id'] in logged_in_users_ids else 'NO'
                for key in dictionary.keys():
                    if key == 'is_active':
                        continue
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        dictionary.pop('logged_in_status')
                        break
                if 'logged_in_status' in dictionary:
                    dictionary.pop('logged_in_status')
            return result_list

        return qs

    def get_initial_queryset(self):
        """
        Preparing  initial queryset for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] == 'admin':
            organization_descendants_ids = list(
                self.request.user.userprofile.organization.get_descendants(include_self=True)
                .values_list('id', flat=True))
        else:
            organization_descendants_ids = list(str(self.request.user.userprofile.organization.id))

        return UserProfile.objects.exclude(id=self.request.user.userprofile.id).filter(
            organization__in=organization_descendants_ids,
            is_deleted=0
        ).values(
            *self.columns + ['id', 'is_active']
        )

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.
        :param qs:
        :return qs
        """
        if qs:
            # Init qs data list
            resultant_data = list()
            # make Visitor ids list
            logged_in_users_ids = [visitor.user_id for visitor in Visitor.objects.all()]

            for dct in qs:
                dct.update(
                    actions='<h3 class="fa fa-lock text-danger" title="Lock User" \
                            onclick="change_user_status(this);"> &nbsp;</h3>'
                            if dct.get('is_active') else '<h3 class="fa fa-unlock text-success" \
                            title="Unlock User" onclick="change_user_status(this);"> &nbsp;</h3>',
                    logged_in_status='NO',
                    full_name=str(dct['first_name']) + " " + str(dct['last_name'])
                )

                if dct['id'] in logged_in_users_ids:
                    dct['actions'] += '<h3 class="fa fa-sign-out text-danger" title="Log-Off User" \
                                      onclick="logout_user(this);"> &nbsp;</h3>'
                    dct['logged_in_status'] = 'YES'

                resultant_data.append(dct)
            return resultant_data
        return qs

    def ordering(self, qs):
        """
        Sort the qs with respect to the columns required in the queryset.
        If nothing is specified then by default the ordering will be done
        on the basis of first column in the data table.
        """
        order_columns = self.get_order_columns()
        
        # Create instance of 'NocoutUtilsGateway' class
        nocout_utils = NocoutUtilsGateway()

        return nocout_utils.nocout_datatable_ordering(self, qs, order_columns)

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request

        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()


        # Number of records before filtering.
        if type(qs) == type(list()):
            total_records = len(qs)
        else:
            total_records = qs.count()

        qs = self.filter_queryset(qs)
        
        # Number of records after filtering.
        if type(qs) == type(list()):
            total_display_records = len(qs)
        else:
            total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # If the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.
        # Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # Prepare output data.
        aaData = self.prepare_results(qs)

        ret = {
            'sEcho': int(request.REQUEST.get('sEcho', 0)),
            'iTotalRecords': total_records,
            'iTotalDisplayRecords': total_display_records,
            'aaData': aaData
        }

        return ret


@csrf_exempt
def dialog_action(request):
    """
    The action of the dialog box appears on the screen.
    If the action is continue then the user will get logged off from the current logged in session
    and the same session key will be used to login the user.
    """
    url = request.POST.get('url', '/home/')
    user = auth.authenticate(token=request.POST.get('auth_token', None))

    if request.POST.get('action') == 'continue' and user:
        # session_key = request.session.session_key
        if hasattr(user, 'visitor'):
            Session.objects.filter(session_key=user.visitor.session_key).delete()
            # If Session object is modified as session key is changed.
            # Above doesn't remove existing visitor object.
            # So removing it below.
            Visitor.objects.filter(user=user).delete()
        auth.login(request, user)
        # Create an entry for user's session in visitor model.
        Visitor.objects.create(session_key=request.session.session_key, user=request.user)
        # Empty the user invalid attempts on successful login.
        UserProfile.objects.filter(id=user.id).update(user_invalid_attempt=0)
        object_values = dict(url=url)
    else:
        object_values = dict(url='/login/')

    result = {
        "success": 1,  # 0 - fail, 1 - success, 2 - exception
        "message": "Success/Fail message.",
        "data": {
            "meta": {},
            "objects": object_values,
        }
    }

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def change_user_status(request):
    """
    Modify the status of user by modifying it's 'is_active' bit.
    The response for user lock down, with success 1 as successful.
    """
    user_name = request.POST.get('user_name')
    user = UserProfile.objects.filter(username=user_name)

    if user[0].is_active:
        status = False
    else:
        status = True
        user.update(user_invalid_attempt=0, user_invalid_attempt_at=None)

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

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def dialog_for_page_refresh(request):
    """
    The ajax request to refresh the page is user status is changed to not active.
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

    return HttpResponse(json.dumps(result), content_type='application/json')


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

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def logout_user(request):
    """
    To logout the user from the system.
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

    return HttpResponse(json.dumps(result), content_type='application/json')