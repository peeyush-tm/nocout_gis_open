import datetime

#Used for JsonDatetime Encoding #example# ::json.dumps( json_object, default=date_handler )
date_handler = lambda obj: obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(obj, datetime.datetime) else None
