from rest_framework.routers import DefaultRouter
from .views import BrandProfileViewSet, ReviewViewSet

router = DefaultRouter()
router.register("brand", BrandProfileViewSet, basename="brand")
router.register("reviews", ReviewViewSet, basename="reviews")
urlpatterns = router.urls
