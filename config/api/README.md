# Eventify API

Event management and secure ticket purchase system built with Django REST Framework.

## Features

- **Transaction-Safe Purchases**: `select_for_update()` prevents race conditions and overselling
- **JWT Authentication**: Token-based security
- **User Isolation**: Users only see their own purchases
- **Immutable Purchases**: No updates/deletes on completed purchases

## Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/POST/PUT/DELETE | `/api/events/` | Event CRUD | Yes (Owner) |
| GET/POST/PUT/DELETE | `/api/ticket-types/` | Ticket type management | Yes |
| GET/POST | `/api/ticket-purchases/` | Purchase tickets (immutable) | Yes |

## Transaction Safety

```python
def perform_create(self, serializer):
    with transaction.atomic():
        # Lock row to prevent concurrent access
        ticket_type = TicketType.objects.select_for_update().get(...)
        
        # Validate capacity
        if quantity > ticket_type.capacity:
            raise ValidationError(...)  # Auto rollback
        
        # Update atomically
        ticket_type.capacity -= quantity
        ticket_type.save()
        serializer.save(user=self.request.user)
```

**Result**: Multiple simultaneous purchase requests are serialized. No overselling possible.

## Quick Start

```bash
# Create event
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "Concert", "description": "...", "start_time": "...", "end_time": "..."}'

# Create ticket type
curl -X POST http://localhost:8000/api/ticket-types/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"event": 1, "name": "VIP", "price": "100.00", "capacity": 50}'

# Purchase tickets (safe from race conditions)
curl -X POST http://localhost:8000/api/ticket-purchases/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"ticket_type": 1, "quantity": 2}'
```

## Testing

```bash
# Run tests
python manage.py test api

# Key tests covered:
# - Successful purchase + capacity reduction
# - Capacity validation (exceeds/zero capacity)
# - Concurrent purchase safety
# - Authentication requirements
# - User purchase isolation
# - Immutability (no update/delete)
```

## Models

**Event**: title, description, start_time, end_time, owner  
**TicketType**: event, name, price, capacity  
**TicketPurchase**: user, ticket_type, quantity, total_price, created_at

## Configuration

```python
# settings.py
INSTALLED_APPS = ['rest_framework', 'rest_framework_simplejwt', 'api', 'login']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
AUTH_USER_MODEL = 'login.CustomUser'
```

## Error Responses

- `400`: Validation error (e.g., "Not enough tickets available")
- `401`: Authentication required
- `404`: Resource not found
- `405`: Method not allowed (e.g., trying to update purchase)

---

**Status**: Production Ready ✅  
**Version**: 1.0.0
