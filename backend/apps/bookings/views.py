from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Booking, Traveler
from .serializers import BookingSerializer, TravelerSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.select_related("route").prefetch_related("travelers").all()
        route_id = self.request.query_params.get("route")
        status_param = self.request.query_params.get("status")
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class TravelerViewSet(viewsets.ModelViewSet):
    serializer_class = TravelerSerializer

    def get_queryset(self):
        queryset = Traveler.objects.select_related("booking").all()
        booking_id = self.request.query_params.get("booking")
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get("booking")
        if booking_id:
            booking = Booking.objects.filter(id=booking_id).first()
            if booking:
                traveler_count = booking.travelers.count()
                if traveler_count >= booking.party_size:
                    raise ValidationError(
                        {"detail": f"游客人数已达报名人数上限（{booking.party_size}人），无法继续添加"}
                    )
        return super().create(request, *args, **kwargs)
