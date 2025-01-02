from django.shortcuts import render
from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from . serializers import *
from django.http import JsonResponse
from datetime import datetime
from rest_framework import status



class TrainView(APIView):
    serializer_class = TrainSerializer

    def get(self, request):
        trains = Train.objects.all()  # Query all trains
        serializer = self.serializer_class(trains, many=True)  # Serialize the queryset
        return Response(serializer.data)  # Return serialized data


class ScheduleView(APIView):
    serializer_class = ScheduleSerializer

    def get(self, request):
        schedules = Schedule.objects.all()
        serializer = self.serializer_class(schedules, many=True)
        return Response(serializer.data)
    
class StationView(APIView):
    serializer_class = StationSerializer

    def get(self, request):
        stations = Station.objects.all()
        serializer = self.serializer_class(stations, many=True)
        return Response(serializer.data)

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Train  # Import your Train model
from .serializers import TrainRequestSerializer  # Import the serializer
from django.db.models import Q

def getRoute(source, destination):
    try:
        source_station_id = Station.objects.get(station_name=source).station_id
        destination_station_id = Station.objects.get(station_name=destination).station_id
    except Station.DoesNotExist:
        return []

    source_stops = RouteStop.objects.filter(station_id=source_station_id).select_related('route')
    destination_stops = RouteStop.objects.filter(station_id=destination_station_id).select_related('route')

    valid_routes = []
    for r1 in source_stops:
        for r2 in destination_stops:
            if r1.priority < r2.priority and r1.route == r2.route:
                valid_routes.append({
                    'route': r1.route,
                    'departure': r1.departure_time  # Assuming departure_time exists in RouteStop
                })

    return valid_routes

def getRouteWithDeparture(source, destination):
    try:
        source_station_id = Station.objects.get(station_name=source).station_id
        destination_station_id = Station.objects.get(station_name=destination).station_id
    except Station.DoesNotExist:
        return []

    # Get RouteStops for source and destination
    source_stops = RouteStop.objects.filter(station_id=source_station_id).select_related('route')
    destination_stops = RouteStop.objects.filter(station_id=destination_station_id).select_related('route')

    # Map routes with departure times
    valid_routes = []
    for r1 in source_stops:
        for r2 in destination_stops:
            if r1.priority < r2.priority and r1.route == r2.route:
                valid_routes.append({
                    'route': r1.route,
                    'departure': r1.departure_time  # Assuming departure_time exists in RouteStop
                })

    return list(valid_routes)


class GetTrainsView(APIView):
    def post(self, request):
        # Deserialize and validate input data
        serializer = TrainRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        source = serializer.validated_data['source']
        destination = serializer.validated_data['destination']
        date = serializer.validated_data['date']

        routes_with_departures = getRouteWithDeparture(source, destination)
        if not routes_with_departures:
            return Response({'error': 'No valid routes found for the given source and destination.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Extract route IDs
            route_ids = [route['route'].route_id for route in routes_with_departures]

            # Query Train model
            trains = Train.objects.filter(
                route_id__in=route_ids,
                schedule_id__departure__date=date
            )

            if not trains.exists():
                return Response({'error': 'No trains found for the given parameters.'}, status=status.HTTP_404_NOT_FOUND)

            # Map train details along with departure times
            train_list = []
            for train in trains:
                departure_time = next(
                    (r['departure'] for r in routes_with_departures if r['route'] == train.route_id), None
                )
                
                # Add a check for None to avoid calling .strftime() on None
                if departure_time is None:
                    departure_str = 'N/A'  # Fallback if departure time is None
                else:
                    departure_str = departure_time.strftime('%H:%M')

                train_list.append({
                    'train_number': train.train_no,
                    'train_name': train.train_name,
                    'source': train.route_id.source_id.station_name,
                    'destination': train.route_id.destination_id.station_name,
                    'departure': departure_str,
                    'schedule_id': train.schedule_id.schedule_id
                })

            return Response({'trains': train_list}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(str(e))  # Or use logging
            return Response({'error': 'An error occurred while processing your request.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# class GetTrainsView(APIView):
#     def post(self, request):
#         # Deserialize and validate input data
#         serializer = TrainRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         # Extract validated data
#         source = serializer.validated_data['source']
#         destination = serializer.validated_data['destination']
#         date = serializer.validated_data['date']

#         routes = getRoute(source, destination)
#         if not routes:
#             return Response({'error': 'No valid routes found for the given source and destination.'}, status=status.HTTP_404_NOT_FOUND)
#         try:
#             # Query the Train model
#             trains = Train.objects.filter(
#                 route_id__source_id__station_name=source,
#                 route_id__destination_id__station_name=destination,
#                 schedule_id__departure__date=date
#             )

#             trains1 = Train.objects.filter(
#                 route_id__in = routes,
#                 schedule_id__departure__date=date
#             )

#             if not trains1.exists():
#                 return Response({'error': 'No trains found for the given parameters.'}, status=status.HTTP_404_NOT_FOUND)

            # Format train data for response
            # train_list = [
            #     {
            #         'train_number': train.train_no,
            #         'train_name': train.train_name,
            #         'source': train.route_id.source_id.station_name,
            #         'destination': train.route_id.destination_id.station_name,
            #         'departure': train.schedule_id.departure.strftime('%d/%m/%Y %H:%M:%S'),
            #         'schedule_id': train.schedule_id.schedule_id
            #     }
            #     for train in trains
            # ]

        #     train_list = [
        #         {
        #             'train_number': train.train_no,
        #             'train_name': train.train_name,
        #             'source': train.route_id.source_id.station_name,
        #             'destination': train.route_id.destination_id.station_name,
        #             'departure': train.schedule_id.departure.strftime('%d/%m/%Y %H:%M:%S'),
        #             'schedule_id': train.schedule_id.schedule_id
        #         }
        #         for train in trains1
        #     ]            
        #     return Response({'trains': train_list}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     # Handle unexpected server-side errors
        #     return Response({'error': 'An error occurred while processing your request.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class SeatBookingView(APIView):
#     def post(self, request):
#         serializer = BookingSerializer(data=request.data)
#         if serializer.is_valid():
#             # Create the booking instance from validated data
#             booking = Booking(
#                 user=serializer.validated_data['user'],
#                 name=serializer.validated_data['name'],
#                 train=Train.objects.get(train_no=serializer.validated_data['train']) ,
#                 schedule=serializer.validated_data['schedule'],
#                 class_type=serializer.validated_data['class_type']
#             )
#             booking.save()  # Automatically assigns a seat if available
            
#             if booking.booking_status == 'CONFIRMED':
#                 return Response(
#                     {"message": "Booking confirmed", "booking": BookingSerializer(booking).data},
#                     status=status.HTTP_201_CREATED
#                 )
#             else:
#                 return Response(
#                     {"message": "No seats available. Added to waitlist", "booking": BookingSerializer(booking).data},
#                     status=status.HTTP_201_CREATED
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Train, Schedule, Booking
from .serializers import BookingSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Train, Schedule, Booking

class SeatBookingView(APIView):
    def post(self, request):
        # Extract the train_no and schedule_id from request data
        train_no = request.data.get('train')
        schedule_id = request.data.get('schedule')

        try:
            # Look up the train and schedule based on the provided train_no and schedule_id
            train = Train.objects.get(train_no=train_no)
            schedule = Schedule.objects.get(schedule_id=schedule_id)
        except Train.DoesNotExist:
            return Response({"error": "Train not found"}, status=status.HTTP_404_NOT_FOUND)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract other required fields from the request
        user = request.data.get("user")
        name = request.data.get("name")
        class_type = request.data.get("class_type")

        if not user or not name or not class_type:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the booking instance manually
            booking = Booking(
                user_id=user,
                name=name,
                train=train,
                schedule=schedule,
                class_type=class_type
            )

            # Save the booking
            booking.save()  # Automatically assigns a seat if available (or adds to waitlist)

            # Logic to determine booking status
            if booking.booking_status == 'CONFIRMED':
                return Response(
                    {"message": "Booking confirmed", "booking": {
                        "user": booking.user_id,
                        "name": booking.name,
                        "train": booking.train.train_no,
                        "schedule": booking.schedule.schedule_id,
                        "class_type": booking.class_type,
                        "booking_status": booking.booking_status
                    }},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"message": "No seats available. Added to waitlist", "booking": {
                        "user": booking.user_id,
                        "name": booking.name,
                        "train": booking.train.train_no,
                        "schedule": booking.schedule.schedule_id,
                        "class_type": booking.class_type,
                        "booking_status": booking.booking_status
                    }},
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# class GetTrainsView(APIView):
#     def post(self, request):
#         # Deserialize and validate input data
#         serializer = TrainRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         # Extract validated data
#         source = serializer.validated_data['source']
#         destination = serializer.validated_data['destination']
#         date = serializer.validated_data['date']

#         try:
#             # Query the Train model
#             trains = Train.objects.filter(
#                 route_id__source_id__station_name=source,
#                 route_id__destination_id__station_name=destination,
#                 schedule_id__departure__date=date
#             )

#             if not trains.exists():
#                 return Response({'error': 'No trains found for the given parameters.'}, status=status.HTTP_404_NOT_FOUND)

#             # Format train data for response
#             train_list = [
#                 {
#                     'train_number': train.train_no,
#                     'train_name': train.train_name,
#                     'source': train.route_id.source_id.station_name,
#                     'destination': train.route_id.destination_id.station_name,
#                     'departure': train.schedule_id.departure.strftime('%d/%m/%Y %H:%M:%S'),
#                     'schedule_id': train.schedule_id.schedule_id
#                 }
#                 for train in trains
#             ]

#             return Response({'trains': train_list}, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Handle unexpected server-side errors
#             return Response({'error': 'An error occurred while processing your request.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class SeatBookingView(APIView):
#     def post(self, request):
#         serializer = BookingSerializer(data=request.data)

#         if serializer.is_valid():
#             # Create the booking instance from validated data
#             booking = Booking(
#                 user=serializer.validated_data['user'],
#                 name=serializer.validated_data['name'],
#                 train=serializer.validated_data['train'],
#                 schedule=serializer.validated_data['schedule'],
#                 class_type=serializer.validated_data['class_type']
#             )
#             booking.save()  # Automatically assigns a seat if available
            
#             if booking.booking_status == 'CONFIRMED':
#                 return Response(
#                     {"message": "Booking confirmed", "booking": BookingSerializer(booking).data},
#                     status=status.HTTP_201_CREATED
#                 )
#             else:
#                 return Response(
#                     {"message": "No seats available. Added to waitlist", "booking": BookingSerializer(booking).data},
#                     status=status.HTTP_201_CREATED
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class GetTrainsView(APIView):
#     def post(self, request):
#         # Deserialize and validate input data
#         serializer = TrainRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         # Extract validated data
#         source = serializer.validated_data['source']
#         destination = serializer.validated_data['destination']
#         date = serializer.validated_data['date']

#         try:
#             # Query trains with source and destination stations in the route
#             trains = Train.objects.filter(
#                 route_id__route_stops__station__station_name=source,
#                 route_id__route_stops__station__station_name=destination,
#                 schedule_id__departure__date=date
#             ).distinct()

#             if not trains.exists():
#                 return Response({'error': 'No trains found for the given parameters.'}, status=status.HTTP_404_NOT_FOUND)

#             # Format train data for response
#             train_list = []
#             for train in trains:
#                 # Check station order along the route
#                 stops = train.route_id.route_stops.filter(
#                     station__station_name__in=[source, destination]
#                 ).order_by('order')

#                 if len(stops) == 2 and stops[0].station.station_name == source:
#                     train_list.append({
#                         'train_number': train.train_no,
#                         'train_name': train.train_name,
#                         'source': source,
#                         'destination': destination,
#                         'departure': train.schedule_id.departure.strftime('%d/%m/%Y %H:%M:%S'),
#                         'schedule_id': train.schedule_id.schedule_id
#                     })

#             if not train_list:
#                 return Response({'error': 'No valid trains found for the given route order.'}, status=status.HTTP_404_NOT_FOUND)

#             return Response({'trains': train_list}, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Handle unexpected server-side errors
#             return Response({'error': 'An error occurred while processing your request.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class HistoryView(APIView):
    def get(self, request):
        # Fetch the bookings for the logged-in user
        user_id = request.query_params["user_id"]
        history = Booking.objects.filter(user__id = user_id)  # Filter bookings by user
        
        # Serialize the data
        serializer = ViewHistorySerializer(history, many=True)  # Assuming you have a BookingSerializer
        
        # Return the serialized data as a response
        return Response(serializer.data)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# class CancelTicketView(APIView):
#     def post(self, request):
#         try:
#             # Extract row_id from the JSON body
#             row_id = request.data.get("row_id")
#             if not row_id:
#                 return Response({"error": "row_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Fetch the booking record
#             booking = Booking.objects.get(booking_id=row_id)

#             # Update the booking status
#             booking.booking_status = "CANCELLED"
#             if booking.seat:
#                 # Use ORM's update method to directly update the seat availability
#                 Seat.objects.filter(seat_id=booking.seat.seat_id).update(is_available=True)
#             booking.save()

#             # Assign waitlist seat
#             if booking.seat:
#                 Booking.assign_waitlist_seat(
#                     train=booking.train,
#                     schedule=booking.schedule,
#                     class_type=booking.class_type,
#                 )

#             return Response({"message": "Booking cancelled and waitlist updated"}, status=status.HTTP_200_OK)

#         except Booking.DoesNotExist:
#             return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CancelTicketView(APIView):
    def post(self, request):
        try:
            # Extract row_id from the JSON body
            user_id = int(request.data.get("user_id"))
            name = request.data.get("name")
            train_no = int(request.data.get("train_no"))
            schedule_id = int(request.data.get("schedule_id"))
            class_type = int(request.data.get("class_type"))

            
            # Fetch the booking record
            booking = Booking.objects.get(user__id=user_id, schedule__schedule_id=schedule_id, name=name, train__train_no=train_no, class_type=class_type)

            # Update the booking status
            booking.booking_status = "CANCELLED"
            if booking.seat:
                # Use ORM's update method to directly update the seat availability
                Seat.objects.filter(seat_id=booking.seat.seat_id).update(is_available=True)
            booking.save()

            # Assign waitlist seat
            if(booking.seat):
                Booking.assign_waitlist_seat(
                    train=booking.train,
                    schedule=booking.schedule,
                    class_type=booking.class_type,
                )

            return Response({"message": "Booking cancelled and waitlist updated"}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)











    

 



