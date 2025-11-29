from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class RoleHeaderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        header = settings.ROLE_HEADER
        role = request.headers.get(header, "")
        request.role = role.lower().strip()


def has_role(request, *roles):
    return getattr(request, "role", None) in {r.lower() for r in roles}
