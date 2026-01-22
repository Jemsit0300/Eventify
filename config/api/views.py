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
    serializer_class = TicketPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return TicketPurchase.objects.all()
        
        return TicketPurchase.objects.filter(user=user)

    def perform_create(self, serializer):
        with transaction.atomic():
            ticket_type = (
                TicketType.objects

                .select_for_update()
                .get(id=serializer.validated_data['ticket_type'].id)
            )

            quantity = serializer.validated_data['quantity']

            if quantity > ticket_type.capacity:
                raise ValidationError({'quantity': 'Not enough tickets available'})
            
            ticket_type.capacity -= quantity
            ticket_type.save()

            serializer.save(user=self.request.user)