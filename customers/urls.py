from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, FieldDefinitionViewSet

router = DefaultRouter()
router.register(r"items", CustomerViewSet, basename="customer")
router.register(r"fields", FieldDefinitionViewSet, basename="field")

urlpatterns = router.urls
