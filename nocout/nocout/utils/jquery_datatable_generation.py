

class Datatable_Generation:

    def __init__(self, object_list, sanity_dicts_list=None, delimiter=' ', **kwargs ):
        self.object_list = object_list
        self.sanity_dicts_list = sanity_dicts_list
        self.delimiter=delimiter


    def sanity_of_object_dict_list( self ):
        for dct in self.sanity_dicts_list:
            dict_final_key = dct.pop('dict_final_key')
            for object_dict in self.object_list:
                object_dict[ dict_final_key ] = self.delimiter.join( [ object_dict.pop(dict_values) for dict_values in dct.values() ] )


    def main(self):

        self.object_list = [ { key: val if val else "" for key, val in dct.items() } for dct in self.object_list ]
        if self.sanity_dicts_list:
            self.sanity_of_object_dict_list()
        object_list_headers = [ dict(mData=key, sTitle = key.replace('_',' ').title()) for key in self.object_list[0].keys() ]
        return self.object_list, object_list_headers



