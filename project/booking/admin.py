from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Schedule)
admin.site.register(Train)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Booking)
admin.site.register(Seat)
admin.site.register(RouteStop)