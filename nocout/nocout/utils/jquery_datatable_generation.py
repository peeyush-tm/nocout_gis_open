"""
============================================
Module contains datatable objects sanitizer.
============================================

Location:
* /nocout_gis/nocout/activity_stream/views.py

List of constructs:
=======
Classes
=======
* Datatable_Generation
"""


class Datatable_Generation:
    """
    Sanitize datatable raw data before generating datatables. Here datatable raw data in form of list of
    dictionaries 'object_list' and another list of dictionaries 'sanity_dicts_list' passed as parameters,
    based on which 'object_list' is sanitized to get final data (datatable headers and data) which needs
    to be returned to datatable.

    Workflow:
    1. Get 'object_list' which contains raw data as a list of dictionaries for e.g.
                                                                        [
                                                                            {
                                                                                'username': u'user1',
                                                                                'phone_number': '',
                                                                                'first_name': u'User1',
                                                                                'last_name': '',
                                                                                'email': u'user1@gmail.com',
                                                                                'last_login': datetime.datetime(2015,
                                                                                5,
                                                                                7,
                                                                                14,
                                                                                2,
                                                                                27),
                                                                                'parent__last_name': '',
                                                                                'role__role_name': u'admin',
                                                                                'organization__name': u'TCL',
                                                                                'parent__first_name': '',
                                                                                'id': 62L
                                                                            }
                                                                        ]
    2. Get 'sanity_dicts_list' based on which 'object_list' needs to be sanitized. Example of 'sanity_dicts_list'
                                                                            [
                                                                                OrderedDict([
                                                                                    ('dict_final_key',
                                                                                    'full_name'),
                                                                                    ('dict_key1',
                                                                                    'first_name'),
                                                                                    ('dict_key2',
                                                                                    'last_name')
                                                                                ]),
                                                                                OrderedDict([
                                                                                    ('dict_final_key',
                                                                                    'manager_name'),
                                                                                    ('dict_key1',
                                                                                    'parent__first_name'),
                                                                                    ('dict_key2',
                                                                                    'parent__last_name')
                                                                                ])
                                                                            ]
    3. Loop on 'sanity_dicts_list' then loop on 'object_list' as an inner loop. Now manipulate all dictionaries
       in 'object_list' by following process below:
       * Consider 'dict_final_key' value in 'sanity_dicts_list' as key of the field which needs to be modified in 
         dictionaries in 'object_list', and values of keys other than 'dict_final_key' in 'sanity_dicts_list'
         as keys of fields which needs to be concatinated to get the value of field which needs to be modified 
         above, i.e. 
         dict1['full_name'] = dict1['first_name'] + dict1['last_name'],
         dict1['manager_name'] = dict1['parent__first_name'] + dict1['parent__last_name']

    """
    def __init__(self, object_list, sanity_dicts_list=None, delimiter=' ', **kwargs):
        """
        Sanitize data before showing it in the datatable.

        Args:
            object_list (list): Raw data fetched from database for datatable. For e.g.,
                                [
                                    {
                                        'username': u'user1',
                                        'phone_number': '',
                                        'first_name': u'User1',
                                        'last_name': '',
                                        'email': u'user1@gmail.com',
                                        'last_login': datetime.datetime(2015,
                                        5,
                                        7,
                                        14,
                                        2,
                                        27),
                                        'parent__last_name': '',
                                        'role__role_name': u'admin',
                                        'organization__name': u'TCL',
                                        'parent__first_name': '',
                                        'id': 62L
                                    }
                                ]
            sanity_dicts_list (list): List of dictionary containing data based on which sanitization is performed.
                                      For e.g.,
                                            [
                                                OrderedDict([
                                                    ('dict_final_key',
                                                    'full_name'),
                                                    ('dict_key1',
                                                    'first_name'),
                                                    ('dict_key2',
                                                    'last_name')
                                                ]),
                                                OrderedDict([
                                                    ('dict_final_key',
                                                    'manager_name'),
                                                    ('dict_key1',
                                                    'parent__first_name'),
                                                    ('dict_key2',
                                                    'parent__last_name')
                                                ])
                                            ]
            delimiter (str): Seperator used when concatinating values.
            kwargs (dict): Key word/dictionary arguments.

        Returns:
            self.object_list, object_list_headers (tuple): Result which needs to be returned.
                                                           For e.g.
                                                            ([
                                                                {
                                                                    'username': u'user1',
                                                                    'phone_number': '',
                                                                    'manager_name': '',
                                                                    'id': 62L,
                                                                    'last_login': datetime.datetime(2015,
                                                                    5,
                                                                    7,
                                                                    14,
                                                                    2,
                                                                    27),
                                                                    'full_name': u'User1',
                                                                    'role__role_name': u'admin',
                                                                    'organization__name': u'TCL',
                                                                    'email': u'user1@gmail.com'
                                                                }
                                                            ],
                                                            [
                                                                {
                                                                    'mData': 'username',
                                                                    'sTitle': 'Username'
                                                                },
                                                                {
                                                                    'mData': 'phone_number',
                                                                    'sTitle': 'PhoneNumber'
                                                                },
                                                                {
                                                                    'mData': 'manager_name',
                                                                    'sTitle': 'ManagerName'
                                                                },
                                                                {
                                                                    'mData': 'id',
                                                                    'sTitle': 'Id'
                                                                },
                                                                {
                                                                    'mData': 'last_login',
                                                                    'sTitle': 'LastLogin'
                                                                },
                                                                {
                                                                    'mData': 'full_name',
                                                                    'sTitle': 'FullName'
                                                                },
                                                                {
                                                                    'mData': 'role__role_name',
                                                                    'sTitle': 'RoleRoleName'
                                                                },
                                                                {
                                                                    'mData': 'organization__name',
                                                                    'sTitle': 'OrganizationName'
                                                                },
                                                                {
                                                                    'mData': 'email',
                                                                    'sTitle': 'Email'
                                                                }
                                                            ])
        """
        self.object_list = object_list
        self.sanity_dicts_list = sanity_dicts_list
        self.delimiter = delimiter

    def sanity_of_object_dict_list(self):
        for dct in self.sanity_dicts_list:
            dict_final_key = dct.pop('dict_final_key')
            # Creating a key in 'object_list' by taking value of 'dict_final_key' as key name,
            # and concatination of specified fields in 'sanity_dicts_list' as value.
            for object_dict in self.object_list:
                object_dict[dict_final_key] = self.delimiter.join(
                    [object_dict.pop(dict_values) for dict_values in dct.values()])

    def main(self):
        # self.object_list = [{key: "" if val is None else val for key, val in dct.items()} for dct in self.object_list]

        if self.sanity_dicts_list:
            self.sanity_of_object_dict_list()

        # Creating final datatable headers.
        object_list_headers = [dict(mData=key, sTitle=key.replace('_', ' ').title()) for key in
                               self.object_list[0].keys()]

        return self.object_list, object_list_headers



