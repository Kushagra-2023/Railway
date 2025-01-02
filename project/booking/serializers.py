from rest_framework import serializers
from .models import *

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'  # Automatically include all fields from the Schedule model

class TrainSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)  # Include related schedules in detail

    class Meta:
        model = Train
        fields = '__all__'

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class TrainRequestSerializer(serializers.Serializer):
    source = serializers.CharField(required=True)
    destination = serializers.CharField(required=True)
    date = serializers.DateField(required=True, input_formats=['%d/%m/%Y'])

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["user", "name", "train", "schedule", "class_type"]

# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = ["user", "name", "train", "schedule", "class_type", "source_station", "destination_station"]


class ViewHistorySerializer(serializers.ModelSerializer):
    train = TrainSerializer()
    schedule = ScheduleSerializer()
    class Meta:
        model = Booking
        fields = ["user", "name", "train", "schedule", "class_type", "booking_status"]

    

