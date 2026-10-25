from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from .models import BrandProfile, Review, Revision

class BrandProofWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = BrandProfile.objects.create(
            name="Inkloom",
            product_facts=["The bottle holds 750 ml and uses recycled steel"],
            restricted_words=["cure"],
            required_phrases=["Crafted with care"],
            brand_colours=["#173B35"],
        )

    def test_review_flags_rules_and_unsupported_claims_then_saves_revision_and_decision(self):
        configured = self.client.patch("/api/brand/1/", {
            "name": "Inkloom Studio",
            "product_facts": ["The bottle holds 750 ml and uses recycled steel"],
            "restricted_words": ["cure"],
            "required_phrases": ["Crafted with care"],
            "brand_colours": ["#173B35", "#D8EF76"],
        }, format="json")
        self.assertEqual(configured.status_code, 200)
        self.assertEqual(configured.data["brand_colours"], ["#173B35", "#D8EF76"])
        response = self.client.post("/api/reviews/", {
            "title": "Launch email",
            "content": "Our cure is guaranteed to be the best. It boosts energy.",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        review_id = response.data["id"]
        categories = {finding["category"] for finding in response.data["findings"]}
        self.assertIn("Restricted term", categories)
        self.assertIn("Required phrase", categories)
        self.assertIn("Absolute promise", categories)
        self.assertIn("Superiority claim", categories)
        self.assertIn("Performance claim", categories)
        self.assertEqual(len(response.data["revisions"]), 1)

        revised = self.client.patch(f"/api/reviews/{review_id}/", {"content": "Crafted with care. The bottle holds 750 ml."}, format="json")
        self.assertEqual(revised.status_code, 200)
        self.assertEqual(len(revised.data["revisions"]), 2)
        self.assertEqual(revised.data["findings"], [])

        decision = self.client.post(f"/api/reviews/{review_id}/decide/", {"decision": "approve", "note": "Approved for campaign."}, format="json")
        self.assertEqual(decision.status_code, 200)
        self.assertEqual(decision.data["status"], "approved")
        self.assertEqual(decision.data["reviewer_note"], "Approved for campaign.")
        self.assertIn("approve", {event["action"] for event in decision.data["events"]})

    def test_invalid_palette_and_unsupported_attachment_are_rejected(self):
        invalid_profile = self.client.patch("/api/brand/1/", {"brand_colours": ["green"]}, format="json")
        self.assertEqual(invalid_profile.status_code, 400)
        upload = SimpleUploadedFile("script.exe", b"bad", content_type="application/octet-stream")
        invalid_review = self.client.post("/api/reviews/", {"title": "File check", "content": "Draft", "files": [upload]}, format="multipart")
        self.assertEqual(invalid_review.status_code, 400)

    def test_supported_attachment_is_stored(self):
        upload = SimpleUploadedFile("brief.txt", b"Campaign notes", content_type="text/plain")
        response = self.client.post("/api/reviews/", {"title": "Uploaded brief", "content": "Crafted with care.", "files": [upload]}, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["attachments"][0]["original_name"], "brief.txt")
        self.assertEqual(Revision.objects.filter(review_id=response.data["id"]).count(), 1)
