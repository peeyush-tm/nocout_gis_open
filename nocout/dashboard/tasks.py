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

