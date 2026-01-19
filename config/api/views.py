from rest_framework import viewsets, mixins

from .models import Event, TicketPurchase, TicketType
from .serializers import EventSerializer, TicketPurchaseSerializer, TicketTypeSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TicketTypeViewSet(viewsets.ModelViewSet):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer

    def get_queryset(self):
        return TicketType.objects.all()


class TicketPurchaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Ticket purchase endpoint.
    - User must be authenticated
    - Users can only see their own purchases
    - Purchase is immutable (no update / delete)
    """
    seerializer_class = TicketPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TicketPurchase.objects.filter(user=self.request.user)
    
    @transaction.atomic
    def perform_create(self, serializer):
        ticket_type = serializer.validated_data['ticket_type']
        quantity = serializer.validated_data['quantity']

        if ticket_type.capacity < quantity:
            raise serializers.ValidationError("Not enough tickets available")
        
        total_price = ticket_type.price * quantity

        ticket_type.capacity -= quantity
        ticket_type.save()

        serializer.save(
            user=self.request.user,
            total_price=total_price
        )