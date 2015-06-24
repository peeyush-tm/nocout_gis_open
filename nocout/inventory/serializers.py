from rest_framework import serializers
from inventory.models import Antenna, Backhaul, BaseStation, Sector, SubStation, Circuit, Customer


class AntennaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antenna


class BackhaulSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backhaul


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector


class SubStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStation


class BaseStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseStation


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer


class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
