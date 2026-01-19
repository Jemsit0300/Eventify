from rest_framework import serializers
from .models import Event, TicketPurchase, TicketType

class EventSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'owner', 'created_at']


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'event', 'name', 'price', 'capacity']

class TicketPurchaseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = TicketPurchase
        fields = ['id', 'user', 'ticket_type', 'quantity', 'total_price', 'created_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value