import logging
from device.models import State, StateGeoInfo
from geo_data import lat_log_data

logger = logging.getLogger(__name__)
# ******************************* STATE LAT LONG MODIFIER ********************************


def update_lat_long():
    counter = 0
    # id's of states we already have in lat_log_data
    current_states_ids = list()

    # loop for getting states id's
    for state_dict in lat_log_data:
        state_id = None
        try:
            state_id = State.objects.get(state_name=state_dict['name']).id
        except Exception as e:
            pass
        if state_id:
            current_states_ids.append(state_id)

    print "********************************** current_states_ids - ", current_states_ids

    # delete only records from 'device_stategeoinfo' table for which we have states in 'lat_long_data'
    try:
        StateGeoInfo.objects.filter(state_id__in=current_states_ids).delete()
    except Exception as e:
        pass

    # insert records in 'device_stategeoinfo' table
    for state_dict in lat_log_data:
        counter += 1

        print "********************************** name - ", state_dict["name"]

        state = State.objects.filter(state_name=state_dict["name"])[0]

        print "********************************** id - ", state.id
        print "********************************** counter - {}", counter

        for boundary in state_dict["boundries"]:
            StateGeoInfo.objects.create(state_id=state.id, latitude=boundary['lat'], longitude=boundary['lon'])