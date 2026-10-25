from django.core.validators import RegexValidator
from django.db import models

hex_color = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #173B35.")

class BrandProfile(models.Model):
    name = models.CharField(max_length=120, default="Inkloom Studio")
    product_facts = models.JSONField(default=list, blank=True)
    restricted_words = models.JSONField(default=list, blank=True)
    required_phrases = models.JSONField(default=list, blank=True)
    brand_colours = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In review"
        CHANGES = "changes_requested", "Changes requested"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=160)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.IN_REVIEW)
    findings = models.JSONField(default=list, blank=True)
    reviewer_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReviewAttachment(models.Model):
    review = models.ForeignKey(Review, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="review-uploads/%Y/%m/")
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Revision(models.Model):
    review = models.ForeignKey(Review, related_name="revisions", on_delete=models.CASCADE)
    version = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-version"]
        constraints = [models.UniqueConstraint(fields=["review", "version"], name="unique_review_revision")]

class WorkflowEvent(models.Model):
    review = models.ForeignKey(Review, related_name="events", on_delete=models.CASCADE)
    action = models.CharField(max_length=32)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
