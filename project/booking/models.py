from django.db import models
from django.utils import timezone  # For using timezone.now()
from datetime import datetime
from users.models import User
# Station model
class Station(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)

    def __str__(self):
        return self.station_name
    
# Route model
class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    source_id = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name='source_routes'
    )
    destination_id = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name='destination_routes'
    )
    via_stations = models.ManyToManyField(Station, related_name="via_routes", blank=True)  # Intermediate stations

    def __str__(self):
        return f"{self.source_id.station_name} to {self.destination_id.station_name}"
    

class RouteStop(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="route_stops"  # Reverse relation
    )
    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="route_stops"
    )
    departure_time = models.TimeField(default=timezone.now)
    arrival_time = models.TimeField()  # Arrival time for each station
    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.station.station_name} at {self.arrival_time} with priority {self.priority}"

# Schedule model
class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    # train = models.ForeignKey(
    #     Train, on_delete=models.CASCADE, related_name="schedules"
    # )
    departure = models.DateTimeField(default=timezone.now)
    arrival = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Departure: {self.departure} Arrival: {self.arrival}"

    # def __str__(self):
    #     return f"{self.train.train_name} schedule"

    # @property
    # def train_no(self):
    #     return self.train.train_no

    # @property
    # def train_name(self):
    #     return self.train.train_name

# Train model
class Train(models.Model):
    train_id = models.AutoField(primary_key=True)
    train_no = models.IntegerField()
    train_name = models.CharField(max_length=100)
    route_id = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="trains"
    )
    schedule_id = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="trains"
    )

    def __str__(self):
        return self.train_name



# Seat model
class Seat(models.Model):
    seat_id = models.AutoField(primary_key=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat_no = models.CharField(max_length=10)
    class_type = models.IntegerField(default=3)  # e.g., Sleeper, AC First Class
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.seat_no} ({self.class_type}) - Train: {self.train.train_name} - Schedule: {self.schedule.departure}"

    def book_seat(self):
        """Marks the seat as booked."""
        self.is_available = False
        self.save()


# Booking model
from django.db import models
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'CONFIRMED'),
        ('WAITLISTED', 'WAITLISTED'),
        ('CANCELLED', 'CANCELLED'),
    ]

    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True, blank=True)  # Seat assignment
    name = models.CharField(max_length=100, null=True, blank=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    class_type = models.IntegerField()  # e.g., Sleeper, AC First Class
    booking_date = models.DateTimeField(default=timezone.now)
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITLISTED')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        """
        Automatically handle seat assignment and price mapping.
        """
        # If no seat is assigned, try to find one
        if not self.seat:
            available_seat = Seat.objects.filter(
                train=self.train,
                schedule=self.schedule,
                class_type=self.class_type,
                is_available=True
            ).first()

            if available_seat:
                self.seat = available_seat
                self.booking_status = 'CONFIRMED'
                self.amount = available_seat.price

                # Mark the seat as booked
                available_seat.is_available = False
                available_seat.save()

        super().save(*args, **kwargs)

    @staticmethod
    def assign_waitlist_seat(train, schedule, class_type):
        """
        Assigns an available seat to the earliest waitlisted booking.
        """
        # Fetch the earliest waitlisted booking
        print(f"Assigning waitlist seat for Train: {train.train_no}, Schedule: {schedule.schedule_id}, Class Type: {class_type}")
        print(f"Waitlisted Booking Count: {Booking.objects.filter(train=train, schedule=schedule, class_type=class_type, booking_status='WAITLISTED').count()}")
        waitlisted_booking = Booking.objects.filter(
            train=train,
            schedule=schedule,
            class_type=class_type,
            booking_status='WAITLISTED'
        ).order_by('booking_date').first()

        if waitlisted_booking:
            # Find an available seat
            available_seat = Seat.objects.filter(
                train=train,
                schedule=schedule,
                class_type=class_type,
                is_available=True
            ).first()

            if available_seat:
                # Assign the seat to the waitlisted booking
                waitlisted_booking.seat = available_seat
                waitlisted_booking.booking_status = 'CONFIRMED'
                waitlisted_booking.amount = available_seat.price
                waitlisted_booking.save()

                # Mark the seat as no longer available
                available_seat.is_available = False
                available_seat.save()

                print(f"Assigned seat {available_seat.seat_id} to booking {waitlisted_booking.booking_id}")
            else:
                print("No available seats to assign")
        else:
            print("No waitlisted bookings to process")
# from django.db import models
# from django.utils import timezone
# from datetime import datetime
# from users.models import User

# def is_seat_available(seat, schedule, source_station, destination_station):
#     # Fetch existing confirmed bookings for the seat
#     bookings = Booking.objects.filter(
#         seat=seat,
#         schedule=schedule,
#         booking_status='CONFIRMED'
#     )

#     # Fetch station orders for comparison
#     stops = RouteStop.objects.filter(
#         route=seat.train.route_id, station__in=[source_station, destination_station]
#     ).order_by('order')
#     source_order, destination_order = stops[0].order, stops[1].order

#     for booking in bookings:
#         booking_stops = RouteStop.objects.filter(
#             route=seat.train.route_id,
#             station__in=[booking.source_station, booking.destination_station]
#         ).order_by('order')
#         booking_source_order, booking_dest_order = booking_stops[0].order, booking_stops[1].order

#         # Check for overlap
#         if not (destination_order <= booking_source_order or source_order >= booking_dest_order):
#             return False  # Overlapping booking found

#     return True  # No overlap

# def get_available_seats(train, schedule, source_station, destination_station, class_type):
#     seats = Seat.objects.filter(train=train, schedule=schedule, class_type=class_type)
#     available_seats = []

#     for seat in seats:
#         if is_seat_available(seat, schedule, source_station, destination_station):
#             available_seats.append(seat)

#     return available_seats


# # Station model
# class Station(models.Model):
#     station_id = models.AutoField(primary_key=True)
#     station_name = models.CharField(max_length=100)
#     district = models.CharField(max_length=100)

#     def __str__(self):
#         return self.station_name


# # Route model
# class Route(models.Model):
#     route_id = models.AutoField(primary_key=True)
#     source_id = models.ForeignKey(
#         Station, on_delete=models.CASCADE, related_name='source_routes'
#     )
#     destination_id = models.ForeignKey(
#         Station, on_delete=models.CASCADE, related_name='destination_routes'
#     )
#     via_stations = models.ManyToManyField(Station, related_name="via_routes", blank=True)

#     def __str__(self):
#         return f"{self.source_id.station_name} to {self.destination_id.station_name}"


# # RouteStop model with `order`
# class RouteStop(models.Model):
#     id = models.AutoField(primary_key=True)
#     route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="route_stops")
#     station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_stops")
#     arrival_time = models.TimeField()
#     order = models.PositiveIntegerField(default=1)  # Position in the route

#     def __str__(self):
#         return f"{self.station.station_name} at {self.arrival_time}"


# # Train model
# class Train(models.Model):
#     train_id = models.AutoField(primary_key=True)
#     train_no = models.IntegerField()
#     train_name = models.CharField(max_length=100)
#     route_id = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trains")
#     schedule_id = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name="train_schedules")

#     def __str__(self):
#         return self.train_name


# # Schedule model
# class Schedule(models.Model):
#     schedule_id = models.AutoField(primary_key=True)
#     departure = models.DateTimeField(default=timezone.now)
#     arrival = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Departure: {self.departure} Arrival: {self.arrival}"


# # Seat model
# class Seat(models.Model):
#     seat_id = models.AutoField(primary_key=True)
#     train = models.ForeignKey(Train, on_delete=models.CASCADE)
#     schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
#     seat_no = models.CharField(max_length=10)
#     class_type = models.IntegerField(default=3)  # Sleeper, AC First Class
#     is_available = models.BooleanField(default=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         return f"{self.seat_no} ({self.class_type}) - Train: {self.train.train_name}"


# # Booking model with new fields
# class Booking(models.Model):
#     STATUS_CHOICES = [
#         ('CONFIRMED', 'Confirmed'),
#         ('WAITLISTED', 'Waitlisted'),
#         ('CANCELLED', 'Cancelled'),
#     ]

#     booking_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     train = models.ForeignKey(Train, on_delete=models.CASCADE)
#     schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
#     source_station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, related_name='source_bookings')
#     destination_station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, related_name='destination_bookings')
#     class_type = models.IntegerField()  # Sleeper, AC First Class
#     booking_date = models.DateTimeField(default=timezone.now)
#     booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITLISTED')
#     amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

#     def save(self, *args, **kwargs):
#         # Check seat availability before assigning
#         if not self.seat:  # If no seat is assigned
#             available_seat = Seat.objects.filter(
#                 train=self.train,
#                 schedule=self.schedule,
#                 class_type=self.class_type,
#                 is_available=True
#             ).first()

#             if available_seat and is_seat_available(
#                 available_seat, self.schedule, self.source_station, self.destination_station
#             ):
#                 self.seat = available_seat
#                 self.booking_status = 'CONFIRMED'
#                 self.amount = available_seat.price

#                 # Mark the seat as booked
#                 available_seat.is_available = False
#                 available_seat.save()

#         super().save(*args, **kwargs)


