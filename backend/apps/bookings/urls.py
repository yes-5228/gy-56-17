from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, TravelerViewSet

router = DefaultRouter()
router.register("", BookingViewSet, basename="booking")
router.register("travelers", TravelerViewSet, basename="traveler")

urlpatterns = router.urls
