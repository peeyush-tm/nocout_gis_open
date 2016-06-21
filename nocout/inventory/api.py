from inventory.tasks import validate_file_for_bulk_upload
import os
from device.models import DeviceTechnology, VendorModel, ModelType, DeviceType
from nocout.settings import MEDIA_ROOT
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import (AntennaSerializer, BackhaulSerializer, SectorSerializer, SubStationSerializer,
                         BaseStationSerializer, CustomerSerializer, CircuitSerializer)
from inventory.models import Antenna, Backhaul, Sector, BaseStation, SubStation, Customer, Circuit
from nocout import permissions

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
from service.models import Service

nocout_utils = NocoutUtilsGateway()
import logging

logger = logging.getLogger(__name__)


class AntennaViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Antenna.
    """
    model = Antenna
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = AntennaSerializer

    def get_queryset(self):
        return Antenna.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class BackhaulViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Backhaul.
    """
    model = Backhaul
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = BackhaulSerializer

    def get_queryset(self):
        return Backhaul.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class SectorViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Sector.
    """
    model = Sector
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = SectorSerializer

    def get_queryset(self):
        return Sector.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class SubStationViewSet(viewsets.ModelViewSet):
    """
    Class Based view for SubStation.
    """
    model = SubStation
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = SubStationSerializer

    def get_queryset(self):
        return SubStation.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class BaseStationViewSet(viewsets.ModelViewSet):
    """
    Class Based view for BaseStation.
    """
    model = BaseStation
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = BaseStationSerializer

    def get_queryset(self):
        return BaseStation.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Customer.
    """
    model = Customer
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class CircuitViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Circuit.
    """
    model = Circuit
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = CircuitSerializer

    def get_queryset(self):
        return Circuit.objects.filter(organization__in=nocout_utils.logged_in_user_organizations(self))


class GetServicesForTechnology(APIView):
    """
    Fetch services corresponding to the selected technology.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_tech_services/2/"
    """
    def get(self, request, pk=""):
        """
        Processing API request.

        Args:
            pk (int): Selected technology ID.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g.,
                                {
                                    "message": "Successfully fetched services data.",
                                    "data": {
                                        "meta": {},
                                        "objects": {
                                            "services": [
                                                {
                                                    "alias": "Radwin UAS",
                                                    "id": 5
                                                },
                                                {
                                                    "alias": "Estimated Throughput",
                                                    "id": 6
                                                },
                                                {
                                                    "alias": "Total Downlink Utilization",
                                                    "id": 7
                                                }
                                            ]
                                        }
                                    },
                                    "success": 0
                                }
        """
        result = list()

        if pk:
            try:
                # Get vendors for selected technology.
                vendors = DeviceTechnology.objects.get(pk=pk).device_vendors
                device_models = list()
                for vendor in vendors.all():
                    models = VendorModel.objects.filter(vendor=vendor)
                    device_models.append(models)
                services = list()
                for model in device_models:
                    # Get all device types associated with all models.
                    types = ModelType.objects.filter(model=model)
                    for dt in types:
                        # Get all services associated with 'types'.
                        for svc in dt.type.service.all():
                            services.append(svc)
                # Some devices have same services, so here we are making list of distinct services.
                distinct_service = set(services)
                for svc in distinct_service:
                    svc_dict = dict()
                    svc_dict['id'] = svc.id
                    svc_dict['alias'] = svc.alias
                    result.append(svc_dict)
            except Exception as e:
                logger.info(e)

        return Response(result)


class GetDSForService(APIView):
    """
    Fetch data sources corresponding to the selected service.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_service_data_sources/5/"
    """
    def get(self, request, pk=""):
        """
        Processing API request.

        Args:
            pk (int): Selected service ID.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g.,
                                {
                                    "message": "Successfully fetched data sources.",
                                    "data": {
                                        "meta": {},
                                        "objects": {
                                            "data_sources": [
                                                {
                                                    "alias": "Radwin UAS",
                                                    "id": 3
                                                }
                                            ]
                                        }
                                    },
                                    "success": 0
                                }
        """
        result = list()

        if pk:
            try:
                # Fetting data sources associated with the selected service.
                data_sources = Service.objects.get(id=pk).service_data_sources.all()
                for data_source in data_sources:
                    ds_dict = dict()
                    ds_dict['id'] = data_source.id
                    ds_dict['alias'] = data_source.alias
                    result.append(ds_dict)
            except Exception as e:
                logger.info(e)

        return Response(result)


class GetServiceForDeviceType(APIView):
    """
    Fetch services corresponding to the selected device type.

    Allow: GET, HEAD, OPTIONS

    URL: "http://127.0.0.1:8000/api/get_device_type_services/4/"
    """
    def get(self, request, pk):
        """
        Processing API request.

        Args:
            pk (int): Selected service ID.

        Returns:
            result (str): Result which needs to be returned.
                          For e.g.,
                                {
                                    "services": [
                                        {
                                            "alias": "ss params from bs",
                                            "id": 145
                                        },
                                        {
                                            "alias": "aggregagte params from bs",
                                            "id": 146
                                        },
                                        {
                                            "alias": "ss vlantag from bs ",
                                            "id": 147
                                        }
                                    ]
                                }
        """
        result = list()

        services = list()
        # Process if type_id is not empty.
        if pk:
            try:
                dt = DeviceType.objects.get(id=pk)
                for svc in dt.service.all():
                    services.append(svc)
                # Some devices have same services, so here we are making list of distinct services.
                distinct_service = set(services)
                
                for svc in distinct_service:
                    svc_dict = dict()
                    svc_dict['id'] = svc.id
                    svc_dict['alias'] = svc.alias
                    result.append(svc_dict)
            except Exception as e:
                logger.info(e)

        return Response(result)


class GetBulkUploadFilesInfo(APIView):
    def get(self, request):
        result = {
            'create': [],
            'delete': []
        }
        # Create/Update inventory files location.
        create_dir = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/create'

        # Delete inventory files location.
        delete_dir = MEDIA_ROOT + 'inventory_files/auto_upload_inventory/delete'

        if os.path.exists(create_dir) and os.listdir(create_dir):
            for inventory in os.listdir(create_dir):
                result['create'].append(inventory)

        if os.path.exists(delete_dir) and os.listdir(delete_dir):
            for inventory in os.listdir(delete_dir):
                result['delete'].append(inventory)

        return Response(result)


class ValidateAutoUploadInventories(APIView):
    def get(self, request, op_type):
        # Result.
        result = {
            'success': 0,
            'message': "Inventory validation request failed."
        }

        if op_type in ['c', 'd']:
            # Validate files for bulk upload.
            validate_file_for_bulk_upload.delay(op_type)
            result['success'] = 1
            result['message'] = "Inventory validation request send."

        return Response(result)
