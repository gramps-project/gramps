# -*- coding: utf-8 -*-

""" Unittest for utils.py """

import unittest
from ..utils import get_contrast_color


class Test_get_contrast_color(unittest.TestCase):
    def setUp(self):
        self.black = (0, 0, 0)
        self.white = (1, 1, 1)

    def test_contrast_black_returns_white(self):
        contrast_color = get_contrast_color(self.black)
        self.assertEqual(
            contrast_color,
            self.white,
            "Contrasting color for black did not return white",
        )

    def test_contrast_white_returns_black(self):
        contrast_color = get_contrast_color(self.white)
        self.assertEqual(
            contrast_color,
            self.black,
            "Contrasting color for white did not return black",
        )


if __name__ == "__main__":
    unittest.main()
