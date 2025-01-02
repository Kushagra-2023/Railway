from django.db.models import Q
from .models import *

# Define source and destination stations
source_station_id = 2  # Example source station id
destination_station_id = 3  # Example destination station id

# Query to filter route stops for source and destination stations
route_stops = RouteStop.objects.filter(
    Q(station_id=source_station_id) | Q(station_id=destination_station_id)
)

# Initialize a list to hold route_ids where source priority < destination priority
valid_route_ids = []

# Iterate through the filtered route stops and compare priorities
for route_stop in route_stops:
    # Get the related route for the current route stop
    route_id = route_stop.route_id
    if(route_stop.station_id == 3):
        continue

    # Get the priority of source and destination from the same route
    for r in route_stops:
        if(r.route_id == route_id & r.station_id == 3 & r.priority > route_stop.priority):
            valid_route_ids.append(route_id)

# Print or return the valid route_ids
print(valid_route_ids)
