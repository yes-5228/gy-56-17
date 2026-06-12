from rest_framework import viewsets

from .models import Booking, Traveler
from .serializers import BookingSerializer, TravelerSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.select_related("route").prefetch_related("travelers").all()
        route_id = self.request.query_params.get("route")
        status = self.request.query_params.get("status")
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class TravelerViewSet(viewsets.ModelViewSet):
    serializer_class = TravelerSerializer

    def get_queryset(self):
        queryset = Traveler.objects.select_related("booking").all()
        booking_id = self.request.query_params.get("booking")
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset
