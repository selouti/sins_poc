from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsServiceProvider(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, "role", None) == "service_provider"


class IsServiceAgent(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, "role", None) == "service_agent"


class ReadOnlyOrAgent(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return getattr(request, "role", None) in {"service_agent", "service_provider"}
