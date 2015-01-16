from celery import task, group
from dashboard.models import DashboardStatusTimely
from dashboard.views import get_gauge_chart_status_data
from organization.models import Organization
import datetime


@task()
def create_dashboard_status_timely():
    """
    """
    user_organizations = Organization.objects.all()
    pmp_latency_data = get_gauge_chart_status_data(user_organizations, False, False, '', 4)
    wimax_latency_data = get_gauge_chart_status_data(user_organizations, False, False, '', 3)
    all_latency_data = get_gauge_chart_status_data(user_organizations, False, False, '', None)
    pmp_packet_loss_data = get_gauge_chart_status_data(user_organizations, True, False, '', 4)
    wimax_packet_loss_data = get_gauge_chart_status_data(user_organizations, True, False, '', 3)
    all_packet_loss_data = get_gauge_chart_status_data(user_organizations, True, False, '', None)
    pmp_down_data = get_gauge_chart_status_data(user_organizations, False, True, '', 4)
    wimax_down_data = get_gauge_chart_status_data(user_organizations, False, True, '', 3)
    all_down_data = get_gauge_chart_status_data(user_organizations, False, True, '', None)
    idu_temperature_data = get_gauge_chart_status_data(user_organizations, False, False, 'IDU', 3)
    acb_temperature_data = get_gauge_chart_status_data(user_organizations, False, False, 'ACB', 3)
    fan_temperature_data = get_gauge_chart_status_data(user_organizations, False, False, 'FAN', 3)
    created_on = datetime.datetime.now()
    data_list = [pmp_latency_data,wimax_latency_data,all_latency_data,pmp_packet_loss_data,wimax_packet_loss_data,
        all_packet_loss_data, idu_temperature_data, acb_temperature_data, fan_temperature_data
    ]
    model_list = ['DashboardStatusTimely', 'DashboardStatusHourly', 'DashboardStatusDaily',
        'DashboardStatusWeekly', 'DashboardStatusMonthly', 'DashboardStatusYearly'
    ]
    for data in data_list:
        for model in model_list
            store_dashboard_data_timely(data, created_on, model)



def store_dashboard_data_timely(dashboard_data, created_on, model):
    """
    """
    data_dict = {}
    data_dict['dashboard_name'] =  dashboard_data['name']
    data_dict['created_on'] = created_on
    data_dict['range_type'] = 'INT'
    data_dict['start_range'] = 1
    data_dict['end_range'] = 10
    data_dict['range_color'] = dashboard_data['color']
    data_dict['range_count'] = dashboard_data['count']
    obj = model.objects.create(**data_dict)

