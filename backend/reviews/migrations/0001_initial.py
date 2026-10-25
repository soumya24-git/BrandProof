import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="BrandProfile", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(default="Inkloom Studio", max_length=120)), ("product_facts", models.JSONField(blank=True, default=list)), ("restricted_words", models.JSONField(blank=True, default=list)), ("required_phrases", models.JSONField(blank=True, default=list)), ("brand_colours", models.JSONField(blank=True, default=list)), ("updated_at", models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name="Review", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("title", models.CharField(max_length=160)), ("content", models.TextField(blank=True)), ("status", models.CharField(choices=[("draft", "Draft"), ("in_review", "In review"), ("changes_requested", "Changes requested"), ("approved", "Approved"), ("rejected", "Rejected")], default="in_review", max_length=24)), ("findings", models.JSONField(blank=True, default=list)), ("reviewer_note", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name="Revision", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("version", models.PositiveIntegerField()), ("content", models.TextField()), ("created_at", models.DateTimeField(auto_now_add=True)), ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="reviews.review"))], options={"ordering": ["-version"]}),
        migrations.CreateModel(name="WorkflowEvent", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("action", models.CharField(max_length=32)), ("note", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="reviews.review"))]),
        migrations.CreateModel(name="ReviewAttachment", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("file", models.FileField(upload_to="review-uploads/%Y/%m/")), ("original_name", models.CharField(max_length=255)), ("uploaded_at", models.DateTimeField(auto_now_add=True)), ("review", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="reviews.review"))]),
        migrations.AddConstraint(model_name="revision", constraint=models.UniqueConstraint(fields=("review", "version"), name="unique_review_revision")),
    ]
