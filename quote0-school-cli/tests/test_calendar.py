from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from quote0_school.api import image_payload, push_canvas
from quote0_school.calendar_data import status_for
from quote0_school.canvas import canvas_payload, render_canvas_preview
from quote0_school.cli import filter_tasks
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

    def test_canvas_payload_matches_official_shape(self) -> None:
        payload = canvas_payload(date(2026, 8, 13), refresh_now=False)
        self.assertFalse(payload["refreshNow"])
        self.assertEqual(payload["taskAlias"], "沪上校历")
        self.assertEqual(payload["data"]["date"], "2026.08.13")
        self.assertEqual(payload["data"]["primaryValue"], 19)
        self.assertEqual(payload["data"]["secondaryValue"], 44)
        self.assertEqual(payload["data"]["nextEvent"], "09.01 秋季开学")
        self.assertTrue(payload["windowData"]["default"])
        self.assertEqual(payload["layoutFull"], {"tw": "p-[10px]"})
        self.assertNotIn("meta", payload)

    def test_canvas_preview_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "canvas.png"
            info = render_canvas_preview(date(2026, 8, 13), output)
            with Image.open(output) as image:
                self.assertEqual(image.size, (296, 152))
                self.assertEqual(image.mode, "1")
            self.assertEqual(info["api"], "canvas")

    def test_task_filter_finds_canvas_content(self) -> None:
        tasks = [
            {"key": "one", "type": "IMAGE_API", "alias": "图像"},
            {"key": "two", "taskType": "CANVAS_API", "alias": "校历"},
        ]
        self.assertEqual(filter_tasks(tasks, "canvas"), [tasks[1]])
        self.assertEqual(filter_tasks(tasks, "image"), [tasks[0]])

    @patch("quote0_school.api.request_json")
    def test_push_canvas_uses_official_endpoint(self, request_json) -> None:
        request_json.return_value = {"message": "Canvas API content switched."}
        payload = canvas_payload(date(2026, 8, 13))
        result = push_canvas("secret", "device-1", payload)
        self.assertIn("Canvas API", result["message"])
        request_json.assert_called_once_with(
            "POST",
            "/api/authV2/open/device/device-1/canvas",
            "secret",
            base_url="https://dot.mindreset.tech",
            body=payload,
        )


if __name__ == "__main__":
    unittest.main()
