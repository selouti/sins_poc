from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rapidfuzz import fuzz

from .models import Customer, FieldDefinition
from .serializers import CustomerSerializer, FieldDefinitionSerializer
from .permissions import ReadOnlyOrAgent, IsServiceProvider
from django.conf import settings
from audit.models import AuditLog
from sins.kafka_utils import emit_event
import uuid


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(deleted_at__isnull=True)
    serializer_class = CustomerSerializer
    permission_classes = [ReadOnlyOrAgent]

    def perform_create(self, serializer):
        obj = serializer.save()
        AuditLog.objects.create(
            actor_role=getattr(self.request, "role", ""),
            action="create",
            entity="customer",
            entity_id=str(obj.id),
            location_id=settings.LOCATION_ID,
            payload=serializer.data,
        )
        emit_event(
            topic="customer.events",
            event_id=str(uuid.uuid4()),
            event_type="customer_created",
            entity_id=str(obj.id),
            location_id=settings.LOCATION_ID,
            payload=serializer.data,
        )

    def perform_update(self, serializer):
        obj = serializer.save()
        AuditLog.objects.create(
            actor_role=getattr(self.request, "role", ""),
            action="update",
            entity="customer",
            entity_id=str(obj.id),
            location_id=settings.LOCATION_ID,
            payload=serializer.data,
        )
        emit_event(
            topic="customer.events",
            event_id=str(uuid.uuid4()),
            event_type="customer_updated",
            entity_id=str(obj.id),
            location_id=settings.LOCATION_ID,
            payload=serializer.data,
        )

    def perform_destroy(self, instance):
        cid = str(instance.id)
        instance.deleted_at = __import__('datetime').datetime.utcnow()
        instance.save(update_fields=["deleted_at"])
        AuditLog.objects.create(
            actor_role=getattr(self.request, "role", ""),
            action="delete",
            entity="customer",
            entity_id=cid,
            location_id=settings.LOCATION_ID,
            payload={"id": cid},
        )
        emit_event(
            topic="customer.events",
            event_id=str(uuid.uuid4()),
            event_type="customer_deleted",
            entity_id=cid,
            location_id=settings.LOCATION_ID,
            payload={"id": cid},
        )

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        term = request.query_params.get("q", "").strip()
        mode = request.query_params.get("mode", "exact").lower()
        limit = int(request.query_params.get("limit", settings.FUZZY_HIT_LIMIT))
        if not term:
            return Response({"detail": "q required"}, status=400)

        qs = self.get_queryset()
        if mode == "exact":
            parts = term.split()
            for p in parts:
                qs = qs.filter(Q(surname__icontains=p) | Q(name__icontains=p) | Q(document_number__icontains=p))
            data = CustomerSerializer(qs[:limit], many=True).data
            return Response({"mode": mode, "results": data})

        # fuzzy
        candidates = list(qs.values("id", "surname", "name", "document_number"))
        scored = []
        for c in candidates:
            s = f"{c['surname']} {c['name']} {c.get('document_number') or ''}"
            score = max(
                fuzz.QRatio(term, s),
                fuzz.partial_ratio(term, s),
            )
            scored.append((score, c["id"]))
        scored.sort(reverse=True)
        ids = [cid for _, cid in scored[:limit]]
        ordered = {cid: i for i, cid in enumerate(ids)}
        res = sorted(Customer.objects.filter(id__in=ids), key=lambda x: ordered[x.id])
        data = CustomerSerializer(res, many=True).data
        return Response({"mode": "fuzzy", "results": data})


class FieldDefinitionViewSet(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    queryset = FieldDefinition.objects.all()
    serializer_class = FieldDefinitionSerializer
    permission_classes = [IsServiceProvider]
