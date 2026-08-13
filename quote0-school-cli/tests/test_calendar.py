from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from PIL import Image

from quote0_school.api import image_payload
from quote0_school.calendar_data import status_for
from quote0_school.render import render_calendar


class CalendarStatusTests(unittest.TestCase):
    def test_summer_countdown(self) -> None:
        status = status_for(date(2026, 8, 13))
        self.assertEqual(status.period.name, "暑假")
        self.assertEqual(status.primary_label, "距秋季开学")
        self.assertEqual(status.primary_value, 19)
        self.assertEqual(status.secondary_value, 44)

    def test_first_term_progress(self) -> None:
        status = status_for(date(2026, 9, 8))
        self.assertEqual(status.period.name, "第一学期")
        self.assertEqual(status.primary_value, 8)
        self.assertEqual(status.teaching_week, 2)
        self.assertEqual(status.secondary_value, 136)

    def test_render_dimensions_and_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "screen.png"
            info = render_calendar(date(2026, 8, 13), output)
            with Image.open(output) as image:
                self.assertEqual(image.size, (296, 152))
                self.assertEqual(image.mode, "1")
            self.assertEqual(info["width"], 296)
            payload = image_payload(output)
            self.assertEqual(payload["ditherType"], "NONE")
            self.assertEqual(payload["taskAlias"], "沪上校历")
            self.assertTrue(payload["image"])


if __name__ == "__main__":
    unittest.main()
