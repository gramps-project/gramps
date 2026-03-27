"""Unittest for display.py"""

import unittest
from unittest.mock import patch
from ..display import display_help
from gramps.gen.const import URL_WIKISTRING


class Test_display_help(unittest.TestCase):

    def test_page(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("page")
            mock.assert_called_with(URL_WIKISTRING + "page")

    def test_page_section(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("page", "section")
            mock.assert_called_with(URL_WIKISTRING + "page#section")

    def test_page_section2(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("page#section")
            mock.assert_called_with(URL_WIKISTRING + "page#section")

    def test_http_page(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("https://page")
            mock.assert_called_with("https://page")

    def test_http_page_section(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("https://page", "section")
            mock.assert_called_with("https://page#section")

    def test_http_page_section2(self):
        with patch("gramps.gui.display.display_url") as mock:
            display_help("https://page#section")
            mock.assert_called_with("https://page#section")

    def test_page_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("page")
                mock.assert_called_with(URL_WIKISTRING + "page/fr")

    def test_page_section_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("page", "section")
                mock.assert_called_with(URL_WIKISTRING + "page/fr#section")

    def test_page_section2_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("page#section")
                mock.assert_called_with(URL_WIKISTRING + "page/fr#section")

    def test_http_page_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("https://page")
                mock.assert_called_with("https://page/fr")

    def test_http_page_section_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("https://page", "section")
                mock.assert_called_with("https://page/fr#section")

    def test_http_page_section2_fr(self):
        with patch("gramps.gui.display.EXTENSION", "/fr"):
            with patch("gramps.gui.display.display_url") as mock:
                display_help("https://page#section")
                mock.assert_called_with("https://page/fr#section")


if __name__ == "__main__":
    unittest.main()
