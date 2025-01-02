from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('train', TrainView.as_view(), name="train"),
    path('schedule', ScheduleView.as_view(), name="schedule"),
    path('station', StationView.as_view(), name="station"),
    path('trainlist', GetTrainsView.as_view(), name="trainlist"),
    path('seatbooking', SeatBookingView.as_view(), name="seatbooking"),
    path('viewhistory', HistoryView.as_view(), name="viewhistory"),
    path('cancelticket', CancelTicketView.as_view(), name="cancelticket"),
]