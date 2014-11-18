from rest_framework import viewsets, generics
from inventory.models import Antenna, Backhaul, Sector, BaseStation, SubStation, Customer, Circuit
#from inventory.serializers import AntennaSerializer, BackhaulSerializer, SectorSerializer, CircuitSerializer, BaseStationSerializer, SubStationSerializer, CustomerSerializer
from nocout.utils import logged_in_user_organizations
from nocout import permissions

class AntennaViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Antenna.
    """
    model = Antenna
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Antenna.objects.filter(organization__in=logged_in_user_organizations(self))


class BackhaulViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Backhaul.
    """
    model = Backhaul
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Backhaul.objects.filter(organization__in=logged_in_user_organizations(self))


class SectorViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Sector.
    """
    model = Sector
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Sector.objects.filter(organization__in=logged_in_user_organizations(self))


class SubStationViewSet(viewsets.ModelViewSet):
    """
    Class Based view for SubStation.
    """
    model = SubStation
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return SubStation.objects.filter(organization__in=logged_in_user_organizations(self))


class BaseStationViewSet(viewsets.ModelViewSet):
    """
    Class Based view for BaseStation.
    """
    model = BaseStation
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return BaseStation.objects.filter(organization__in=logged_in_user_organizations(self))


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Customer.
    """
    model = Customer
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Customer.objects.filter(organization__in=logged_in_user_organizations(self))


class CircuitViewSet(viewsets.ModelViewSet):
    """
    Class Based view for Circuit.
    """
    model = Circuit
    permission_classes = (permissions.DjangoModelPermissions,)

    def get_queryset(self):
        return Circuit.objects.filter(organization__in=logged_in_user_organizations(self))
