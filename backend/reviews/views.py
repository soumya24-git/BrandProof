from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import BrandProfile, Review, Revision, WorkflowEvent
from .risk import evaluate
from .serializers import BrandProfileSerializer, ReviewSerializer

class BrandProfileViewSet(viewsets.ViewSet):
    def get_object(self):
        return BrandProfile.objects.first() or BrandProfile.objects.create()
    def list(self, request): return Response(BrandProfileSerializer(self.get_object()).data)
    def retrieve(self, request, pk=None): return Response(BrandProfileSerializer(self.get_object()).data)
    def update(self, request, pk=None):
        profile = self.get_object()
        serializer = BrandProfileSerializer(profile, data=request.data, partial=request.method == "PATCH")
        serializer.is_valid(raise_exception=True); serializer.save()
        return Response(serializer.data)
    partial_update = update

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.prefetch_related("attachments", "revisions", "events").order_by("-updated_at", "-id")
    serializer_class = ReviewSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        files = serializer.validated_data.pop("files", [])
        with transaction.atomic():
            review = serializer.save()
            profile = BrandProfile.objects.first() or BrandProfile.objects.create()
            review.findings = evaluate(review.content, profile); review.save(update_fields=["findings"])
            Revision.objects.create(review=review, version=1, content=review.content)
            for f in files: review.attachments.create(file=f, original_name=f.name)
            WorkflowEvent.objects.create(review=review, action="submitted", note="Submitted for review")
        return Response(self.get_serializer(review).data, status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        old_content = review.content
        updated = serializer.save()
        if updated.content != old_content:
            profile = BrandProfile.objects.first() or BrandProfile.objects.create()
            updated.findings = evaluate(updated.content, profile)
            updated.status = Review.Status.IN_REVIEW
            updated.save(update_fields=["findings", "status"])
            version = (updated.revisions.order_by("-version").values_list("version", flat=True).first() or 0) + 1
            Revision.objects.create(review=updated, version=version, content=updated.content)
            WorkflowEvent.objects.create(review=updated, action="revised", note=f"Saved version {version}")
            updated.refresh_from_db()
        return Response(self.get_serializer(updated).data)
    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        review = self.get_object()
        decision = request.data.get("decision")
        note = request.data.get("note", "")
        allowed = {"approve": Review.Status.APPROVED, "reject": Review.Status.REJECTED, "request_changes": Review.Status.CHANGES}
        if decision not in allowed: raise ValidationError({"decision": "Choose approve, reject, or request_changes."})
        if not isinstance(note, str) or len(note) > 2000: raise ValidationError({"note": "Reviewer note must be text up to 2,000 characters."})
        review.status = allowed[decision]; review.reviewer_note = note.strip(); review.save(update_fields=["status", "reviewer_note", "updated_at"])
        WorkflowEvent.objects.create(review=review, action=decision, note=review.reviewer_note)
        review.refresh_from_db()
        return Response(self.get_serializer(review).data)
