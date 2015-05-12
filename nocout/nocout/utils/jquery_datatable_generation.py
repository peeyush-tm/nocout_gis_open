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
    Sanitize datatables objects before generating datatables.

    Workflow:
    1. Get 'object_list' which contains raw data generated.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): GET request
        value (int): Selected user ID.
        datatable_headers (unicode): Datatable headers.

    Returns:
        result (str): Result which needs to be returned.
                       for e.g. {
                                    "result": {
                                        "message": "Successfully render form.",
                                        "data": {
                                            "meta": "",
                                            "objects": {
                                                "name": "user11",
                                                "eligible": [],
                                                "datatable_headers": "",
                                                "form_title": "user",
                                                "form_type": "user",
                                                "id": 61
                                            }
                                        },
                                        "success": 1
                                    }
                                }

    """
    def __init__(self, object_list, sanity_dicts_list=None, delimiter=' ', **kwargs):
        self.object_list = object_list
        self.sanity_dicts_list = sanity_dicts_list
        self.delimiter = delimiter
        print "****************************** object_list - ", object_list, type(object_list)
        print "****************************** sanity_dicts_list - ", sanity_dicts_list, type(sanity_dicts_list)
        print "****************************** delimiter - ", delimiter, type(delimiter)
        print "****************************** kwargs - ", kwargs, type(kwargs)

    def sanity_of_object_dict_list(self):
        for dct in self.sanity_dicts_list:
            dict_final_key = dct.pop('dict_final_key')
            for object_dict in self.object_list:
                object_dict[dict_final_key] = self.delimiter.join(
                    [object_dict.pop(dict_values) for dict_values in dct.values()])

    def main(self):
        print "**************************** self - ", self, type(self)
        self.object_list = [{key: "" if val is None else val for key, val in dct.items()} for dct in self.object_list]
        if self.sanity_dicts_list:
            self.sanity_of_object_dict_list()
        object_list_headers = [dict(mData=key, sTitle=key.replace('_', ' ').title()) for key in
                               self.object_list[0].keys()]
        print "************************* object_list_headers - ", object_list_headers, type(object_list_headers)
        return self.object_list, object_list_headers



