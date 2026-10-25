import re
from pathlib import Path
from rest_framework import serializers
from .models import BrandProfile, Review, ReviewAttachment, Revision, WorkflowEvent

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

def clean_string_list(value, label, limit=100):
    if not isinstance(value, list):
        raise serializers.ValidationError(f"{label} must be a list of strings.")
    if len(value) > limit or any(not isinstance(item, str) or not item.strip() or len(item.strip()) > 500 for item in value):
        raise serializers.ValidationError(f"{label} contains an empty or overlong entry (maximum {limit} entries, 500 characters each).")
    return list(dict.fromkeys(item.strip() for item in value))

class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = ["id", "name", "product_facts", "restricted_words", "required_phrases", "brand_colours", "updated_at"]
        read_only_fields = ["id", "updated_at"]
    def validate_name(self, v):
        if not v.strip(): raise serializers.ValidationError("Brand name is required.")
        return v.strip()
    def validate_product_facts(self, v): return clean_string_list(v, "Product facts")
    def validate_restricted_words(self, v): return clean_string_list(v, "Restricted words")
    def validate_required_phrases(self, v): return clean_string_list(v, "Required phrases")
    def validate_brand_colours(self, v):
        values = clean_string_list(v, "Brand colours", 24)
        if any(not re.fullmatch(r"#[0-9A-Fa-f]{6}", colour) for colour in values):
            raise serializers.ValidationError("Each brand colour must be a six-digit hex value, such as #173B35.")
        return values

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAttachment
        fields = ["id", "original_name", "uploaded_at"]

class RevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revision
        fields = ["version", "content", "created_at"]

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowEvent
        fields = ["action", "note", "created_at"]

class ReviewSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    revisions = RevisionSerializer(many=True, read_only=True)
    events = EventSerializer(many=True, read_only=True)
    files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    class Meta:
        model = Review
        fields = ["id", "title", "content", "status", "findings", "reviewer_note", "created_at", "updated_at", "attachments", "revisions", "events", "files"]
        read_only_fields = ["id", "status", "findings", "reviewer_note", "created_at", "updated_at", "attachments", "revisions", "events"]
    def validate_title(self, v):
        if not v.strip(): raise serializers.ValidationError("A review title is required.")
        return v.strip()
    def validate_files(self, files):
        errors = []
        if len(files) > 5: raise serializers.ValidationError("Upload up to 5 files per review.")
        for f in files:
            if Path(f.name).suffix.lower() not in ALLOWED_EXTENSIONS: errors.append(f"{f.name}: unsupported file type.")
            if f.size > MAX_UPLOAD_BYTES: errors.append(f"{f.name}: files must be 10 MB or smaller.")
        if errors: raise serializers.ValidationError(errors)
        return files
