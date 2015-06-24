from rest_framework import viewsets
from serializers import (AntennaSerializer, BackhaulSerializer, SectorSerializer, SubStationSerializer,
                         BaseStationSerializer, CustomerSerializer, CircuitSerializer)
from inventory.models import Antenna, Backhaul, Sector, BaseStation, SubStation, Customer, Circuit
from nocout import permissions

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


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
