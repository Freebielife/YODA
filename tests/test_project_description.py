"""Do not publish technical metadata or present self-claims as verified prose."""
import unittest
from scripts.project_description import from_metadata, section, validate


class DescriptionTests(unittest.TestCase):
    def test_metadata_requires_prose_and_keeps_attribution(self):
        source = "https://example.org/token"
        for text in (None, "", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "https://example.org"):
            self.assertIsNone(from_metadata({"description": text}, source))
        description = from_metadata({"description": "A community token."}, source)
        rendered = section(description)
        self.assertIn("A community token.", rendered)
        self.assertIn("заявления проекта не проверены независимо", rendered)
        self.assertIn(source, rendered)

    def test_sources_and_date_required_without_guessing_missing_description(self):
        description = {"text": "A community project.", "origin": "reviewed_sources",
                       "sources": ["https://example.org/"], "checked_at": "2026-11-22"}
        validate(description)
        for patch in ({"sources": []}, {"sources": ["javascript:alert(1)"]},
                      {"checked_at": "tomorrow"}, {"origin": "verified"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate({**description, **patch})
        self.assertIn("Описание пока не подтверждено", section(None))

    def test_metadata_cannot_insert_active_html_or_markdown(self):
        description = from_metadata({"description": '<script>alert(1)</script> ![ad](https://example.org)'},
                                    "https://example.org/token")
        rendered = section(description)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("![ad]", rendered)
        self.assertIn("&lt;script&gt;", rendered)
