#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Tests for the image geometry helpers.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.image import crop_percentage_to_pixel, image_actual_size
from gramps.gen.utils.image import image_crop_to_ratio


# -------------------------------------------------------------------------
#
# TestImageActualSize
#
# -------------------------------------------------------------------------
class TestImageActualSize(unittest.TestCase):
    """Tests for the ratio preserving fit of an image inside a box."""

    def test_matching_ratio_is_unchanged(self):
        """A box matching the image ratio is left alone."""
        self.assertEqual((2.0, 2.0), image_actual_size(2.0, 2.0, 100, 100))

    def test_wide_box_letterboxes_vertically(self):
        """A wide image in a square box is limited by the width."""
        self.assertEqual((2.0, 1.0), image_actual_size(2.0, 2.0, 200, 100))

    def test_tall_image_limited_by_height(self):
        """A tall image in a square box is limited by the height."""
        self.assertEqual((1.0, 2.0), image_actual_size(2.0, 2.0, 100, 200))

    def test_result_stays_inside_the_box(self):
        """The fit never grows beyond either side of the box."""
        for img_w, img_h in [(300, 100), (100, 300), (640, 480), (17, 4000)]:
            width, height = image_actual_size(2.0, 2.0, img_w, img_h)
            self.assertLessEqual(width, 2.0)
            self.assertLessEqual(height, 2.0)

    def test_ratio_is_preserved(self):
        """The fit keeps the aspect ratio of the source image."""
        width, height = image_actual_size(2.0, 2.0, 300, 100)
        self.assertAlmostEqual(width / height, 3.0, places=6)


# -------------------------------------------------------------------------
#
# TestImageCropToRatio
#
# -------------------------------------------------------------------------
class TestImageCropToRatio(unittest.TestCase):
    """Tests for the cropping used to fill a box with an image."""

    def _cropped_ratio(self, crop, width, height):
        """Return the aspect ratio of the region left after cropping."""
        start_x, start_y, end_x, end_y = crop
        return ((end_x - start_x) * width) / float((end_y - start_y) * height)

    def test_wide_image_trims_the_sides(self):
        """A wide image in a square box is cropped left and right."""
        crop = image_crop_to_ratio(200, 100, 1.0, 1.0)
        self.assertEqual((0, 100), (crop[1], crop[3]))
        self.assertLess(crop[0], 50)
        self.assertGreater(crop[2], 50)
        self.assertAlmostEqual(1.0, self._cropped_ratio(crop, 200, 100), places=1)

    def test_tall_image_trims_top_and_bottom(self):
        """A tall image in a square box is cropped top and bottom."""
        crop = image_crop_to_ratio(100, 200, 1.0, 1.0)
        self.assertEqual((0, 100), (crop[0], crop[2]))
        self.assertGreater(crop[1], 0)
        self.assertLess(crop[3], 100)
        self.assertAlmostEqual(1.0, self._cropped_ratio(crop, 100, 200), places=1)

    def test_crop_is_centred(self):
        """Whatever is trimmed is split evenly between the two sides."""
        crop = image_crop_to_ratio(400, 100, 1.0, 1.0)
        self.assertAlmostEqual(crop[0], 100 - crop[2], delta=1)
        crop = image_crop_to_ratio(100, 400, 1.0, 1.0)
        self.assertAlmostEqual(crop[1], 100 - crop[3], delta=1)

    def test_matching_ratio_is_not_cropped(self):
        """An image already matching the box is left whole."""
        self.assertEqual([0, 0, 100, 100], image_crop_to_ratio(100, 100, 2.0, 2.0))
        self.assertEqual([0, 0, 100, 100], image_crop_to_ratio(400, 200, 2.0, 1.0))

    def test_degenerate_sizes_are_safe(self):
        """Zero or negative sizes fall back to no cropping."""
        self.assertEqual([0, 0, 100, 100], image_crop_to_ratio(0, 0, 1.0, 1.0))
        self.assertEqual([0, 0, 100, 100], image_crop_to_ratio(100, 100, 0.0, 1.0))
        self.assertEqual([0, 0, 100, 100], image_crop_to_ratio(-1, 10, 1.0, 1.0))

    def test_crop_stays_within_bounds(self):
        """The crop never runs outside the image."""
        for img_w, img_h in [(300, 100), (100, 300), (1000, 999), (7, 5)]:
            crop = image_crop_to_ratio(img_w, img_h, 1.0, 1.0)
            self.assertGreaterEqual(crop[0], 0)
            self.assertGreaterEqual(crop[1], 0)
            self.assertLessEqual(crop[2], 100)
            self.assertLessEqual(crop[3], 100)
            self.assertLess(crop[0], crop[2])
            self.assertLess(crop[1], crop[3])

    def test_crop_matches_the_crop_to_pixel_conversion(self):
        """A crop survives conversion to pixel coordinates."""
        width, height = 400, 300
        crop = image_crop_to_ratio(width, height, 1.0, 1.0)
        start_x, start_y, end_x, end_y = crop_percentage_to_pixel(width, height, crop)
        self.assertGreater(end_x - start_x, 0)
        self.assertGreater(end_y - start_y, 0)
        self.assertLessEqual(end_x, width)
        self.assertLessEqual(end_y, height)


if __name__ == "__main__":
    unittest.main()
