from rest_framework.routers import DefaultRouter
from .views import EventViewSet, TicketPurchaseViewSet, TicketTypeViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'ticket-types', TicketTypeViewSet, basename='tickettype')
router.register(r'ticket-purchases', TicketPurchaseViewSet, basename='ticketpurchase')

urlpatterns = router.urls