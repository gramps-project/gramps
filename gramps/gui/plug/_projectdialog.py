#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Brian McCullough <emyoulation@yahoo.com>
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
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""
Enhanced Project Dialog for Addon Repository Management

This module provides an enhanced dialog for creating and editing addon repository
projects with comprehensive URL validation, multi-line URL fields, and support
for both web URLs and local/network folders.

Usage:
    from gramps.gui.plug._projectdialog import EnhancedProjectDialog
    
    dialog = EnhancedProjectDialog(parent_window, project_name, project_url)
    result = dialog.run()
    if result:
        name = result['name']
        url = result['url']
        is_folder = result['is_folder']
       
Generated-by: Claude AI (Anthropic, Claude Sonnet 4.5, 2026-02-13)
"""

import os
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, urljoin

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# EnhancedProjectDialog
#
#-------------------------------------------------------------------------
class EnhancedProjectDialog:
    """
    Enhanced dialog for creating/editing addon repository projects
    
    Features:
    - Multi-line URL field with wrapping (handles long URLs)
    - Web URL vs Local/Network Folder selection
    - Comprehensive validation with detailed feedback
    - Test URL button for optional validation
    - OK button always enabled (allows offline placeholder creation)
    """
    
    def __init__(self, parent, title, project_name="", project_url=""):
        """
        Initialize the enhanced project dialog
        
        :param parent: Parent window (transient_for)
        :param title: Dialog title (e.g., "New Project" or "Edit Project")
        :param project_name: Initial project name
        :param project_url: Initial project URL/path
        """
        self.parent = parent
        self.result = None
        
        # Create dialog - 50% wider for long URLs
        self.dialog = Gtk.Dialog(
            title=title,
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        self.dialog.set_default_size(900, 500)
        self.dialog.set_border_width(12)
        
        # Build the interface
        self._build_interface(project_name, project_url)
        
        # Connect signals
        self._connect_signals()
    
    def _build_interface(self, project_name, project_url):
        """Build the dialog interface"""
        # Content area
        vbox = self.dialog.get_content_area()
        vbox.set_spacing(12)
        
        # Grid for input fields
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)
        grid.set_column_homogeneous(False)
        
        # Project name
        label = Gtk.Label(label=_("%s: ") % _("Project name"))
        label.set_halign(Gtk.Align.END)
        label.set_width_chars(15)
        grid.attach(label, 0, 0, 1, 1)
        
        self.name_entry = Gtk.Entry()
        self.name_entry.set_hexpand(True)
        self.name_entry.set_text(project_name)
        self.name_entry.set_activates_default(True)
        self.name_entry.set_placeholder_text(_("e.g., My Addons Repository"))
        grid.attach(self.name_entry, 1, 0, 2, 1)
        
        # Location type selector
        label = Gtk.Label(label=_("%s: ") % _("Location Type"))
        label.set_halign(Gtk.Align.END)
        label.set_width_chars(15)
        grid.attach(label, 0, 1, 1, 1)
        
        type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.url_radio = Gtk.RadioButton.new_with_label_from_widget(
            None, _("Web URL")
        )
        self.folder_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.url_radio, _("Local/Network Folder")
        )
        type_box.pack_start(self.url_radio, False, False, 0)
        type_box.pack_start(self.folder_radio, False, False, 0)
        grid.attach(type_box, 1, 1, 2, 1)
        
        # URL/Path label
        url_label = Gtk.Label(label=_("%s: ") % _("URL/Path"))
        url_label.set_halign(Gtk.Align.END)
        url_label.set_valign(Gtk.Align.START)
        url_label.set_width_chars(15)
        grid.attach(url_label, 0, 2, 1, 1)
        
        # URL/Path field - multi-line with wrapping
        url_scroll = Gtk.ScrolledWindow()
        url_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        url_scroll.set_min_content_height(100)
        url_scroll.set_hexpand(True)
        
        self.url_text = Gtk.TextView()
        self.url_text.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.url_text.set_accepts_tab(False)
        self.url_buffer = self.url_text.get_buffer()
        self.url_buffer.set_text(project_url)
        
        # Add helpful placeholder if empty
        if not project_url:
            help_text = _(
                "Enter URL or use Browse button.\n"
                "Examples:\n"
                "  https://example.com/addons/\n"
                "  file:///C:/Users/Name/addons/"
            )
            self.url_text.set_tooltip_text(help_text)
        
        url_scroll.add(self.url_text)
        grid.attach(url_scroll, 1, 2, 1, 1)
        
        # Folder selection button (icon only, like Preferences)
        self.browse_button = Gtk.Button()
        self.browse_button.set_tooltip_text(_("Select folder"))
        self.browse_button.connect('clicked', self._on_browse_clicked)
        browse_image = Gtk.Image()
        browse_image.set_from_icon_name("document-open", Gtk.IconSize.BUTTON)
        browse_image.show()
        self.browse_button.add(browse_image)
        self.browse_button.set_valign(Gtk.Align.START)
        self.browse_button.set_sensitive(False)
        grid.attach(self.browse_button, 2, 2, 1, 1)
        
        vbox.pack_start(grid, False, False, 0)
        
        # Validation status frame
        status_frame = Gtk.Frame(label=_("Validation Status"))
        status_frame.set_margin_top(6)
        
        status_scroll = Gtk.ScrolledWindow()
        status_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        status_scroll.set_min_content_height(150)
        
        self.status_text = Gtk.TextView()
        self.status_text.set_editable(False)
        self.status_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.status_text.set_left_margin(6)
        self.status_text.set_right_margin(6)
        self.status_buffer = self.status_text.get_buffer()
        self.status_buffer.set_text(
            _("Click 'Test Location' to validate the repository.\n\n"
              "Validation is optional - you can save without testing "
              "(useful for creating placeholders offline).")
        )
        
        status_scroll.add(self.status_text)
        status_frame.add(status_scroll)
        vbox.pack_start(status_frame, True, True, 0)
        
        # Dialog buttons
        self.dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.test_button = self.dialog.add_button(_("Test Location"), Gtk.ResponseType.HELP)
        self.ok_button = self.dialog.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        
        # Set initial mode based on current URL
        if project_url and (project_url.startswith('http://') or 
                           project_url.startswith('https://')):
            self.url_radio.set_active(True)
        elif project_url:
            self.folder_radio.set_active(True)
        
        # Update button state based on initial selection
        self._on_type_changed(None)
        
        self.dialog.show_all()
    
    def _connect_signals(self):
        """Connect signal handlers"""
        self.url_radio.connect('toggled', self._on_type_changed)
        self.folder_radio.connect('toggled', self._on_type_changed)
        self.browse_button.connect('clicked', self._on_browse_clicked)
        self.dialog.connect('response', self._on_response)
    
    def _get_url_text(self):
        """Get the URL/path text from the text view"""
        start = self.url_buffer.get_start_iter()
        end = self.url_buffer.get_end_iter()
        return self.url_buffer.get_text(start, end, False).strip()
    
    def _on_type_changed(self, widget):
        """Handle location type change"""
        is_folder = self.folder_radio.get_active()
        self.browse_button.set_sensitive(is_folder)
        self.status_buffer.set_text(
            _("Click 'Test Location' to validate the repository.\n\n"
              "Validation is optional - you can save without testing.")
        )
    
    def _on_browse_clicked(self, widget):
        """Open folder chooser dialog using Gtk.FileChooserDialog"""
        chooser = Gtk.FileChooserDialog(
            title=_("Select Listings Folder"),
            parent=self.dialog,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        chooser.add_buttons(
            _("_Cancel"), Gtk.ResponseType.CANCEL,
            _("_Select"), Gtk.ResponseType.OK
        )
        
        # Set initial folder from current URI if possible
        current_text = self._get_url_text()
        if current_text.startswith('file:///'):
            # Convert file:// URI back to OS path for file chooser
            path = current_text[8:]  # Remove 'file:///'
            if os.name == 'nt':
                # Windows: file:///C:/path -> C:/path
                path = path.replace('/', '\\')
            if os.path.exists(path):
                chooser.set_current_folder(path)
        
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            folder_path = chooser.get_filename()
            
            # Convert to file:// URI immediately
            # Remove /listings suffix if present (Gramps adds it)
            if folder_path.endswith(os.sep + 'listings'):
                folder_path = folder_path.rsplit(os.sep + 'listings', 1)[0]
            
            # Normalize to forward slashes
            uri_path = folder_path.replace('\\', '/')
            if not uri_path.endswith('/'):
                uri_path += '/'
            
            # Create file:// URI
            file_uri = 'file:///' + uri_path.lstrip('/')
            
            # Set the URI in the text field (not the OS path)
            self.url_buffer.set_text(file_uri)
        
        chooser.destroy()
    
    def _validate_local_folder(self, folder_path):
        """
        Validate a local or network folder path
        Accepts both OS paths and file:// URIs
        Returns (success: bool, message: str)
        """
        # Convert file:// URI to OS path if needed
        if folder_path.startswith('file:///'):
            # Remove file:/// prefix
            folder_path = folder_path[8:]
            # On Windows, convert forward slashes to backslashes
            if os.name == 'nt':
                folder_path = folder_path.replace('/', '\\')
            # Remove trailing slash
            folder_path = folder_path.rstrip('/\\')
        
        # Check if path exists
        if not os.path.exists(folder_path):
            return False, _(
                "❌ Error: Path does not exist:\n{}\n\n"
                "Please check the path and try again."
            ).format(folder_path)
        
        if not os.path.isdir(folder_path):
            return False, _(
                "❌ Error: Path is not a directory:\n{}"
            ).format(folder_path)
        
        # Check for listings folder
        listings_path = folder_path
        if not folder_path.endswith('listings'):
            test_listings = os.path.join(folder_path, 'listings')
            if os.path.isdir(test_listings):
                listings_path = test_listings
            else:
                return False, _(
                    "❌ Error: Not a listings folder.\n\n"
                    "The selected folder should be named 'listings' or "
                    "contain a 'listings' subfolder.\n\n"
                    "Path: {}"
                ).format(folder_path)
        
        # Look for JSON files
        try:
            json_files = [f for f in os.listdir(listings_path) 
                         if f.endswith('.json')]
        except PermissionError:
            return False, _(
                "❌ Error: Permission denied reading folder:\n{}"
            ).format(listings_path)
        
        if not json_files:
            return False, _(
                "⚠️  Warning: Listings folder found but no JSON files present.\n\n"
                "Path: {}\n\n"
                "The listings folder should contain files like:\n"
                "  • addons-en.json\n"
                "  • addons-fr.json\n"
                "  • etc."
            ).format(listings_path)
        
        # Check for language-specific file
        locale = glocale.language[0] if glocale.language else 'en'
        native_file = "addons-{}.json".format(locale)
        native_path = os.path.join(listings_path, native_file)
        fallback_path = os.path.join(listings_path, "addons-en.json")
        
        messages = [_("✅ Success: Valid listings folder found!")]
        messages.append(_("\nPath: {}").format(listings_path))
        messages.append(_("\nFound {} JSON file(s):").format(len(json_files)))
        for jf in sorted(json_files):
            messages.append("  • {}".format(jf))
        
        # Check native language file
        if os.path.exists(native_path):
            messages.append(_("\n✅ Native language file found: {}").format(native_file))
            try:
                with open(native_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        messages.append(_("   Contains {} addon(s)").format(len(data)))
                    else:
                        messages.append(_("   ⚠️  Warning: Unexpected JSON format (not an array)"))
            except json.JSONDecodeError as e:
                messages.append(_("   ⚠️  Warning: Invalid JSON: {}").format(str(e)))
            except Exception as e:
                messages.append(_("   ⚠️  Warning: Could not read file: {}").format(str(e)))
        
        elif os.path.exists(fallback_path):
            messages.append(_("\n⚠️  Native language file not found: {}").format(native_file))
            messages.append(_("   Will fallback to: addons-en.json"))
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        messages.append(_("   Contains {} addon(s)").format(len(data)))
            except Exception as e:
                messages.append(_("   ⚠️  Warning: Could not read: {}").format(str(e)))
        
        else:
            messages.append(
                _("\n⚠️  Warning: Neither {} nor addons-en.json found").format(native_file)
            )
        
        # Show what will be saved (the file:// URI currently in the text field)
        # Get the original input text to show
        original_input = self._get_url_text()
        if original_input.startswith('file:///'):
            # Already a URI, show it
            save_uri = original_input
        else:
            # Convert OS path to URI for display
            parent_path = os.path.dirname(listings_path.rstrip('/\\'))
            uri_path = parent_path.replace('\\', '/')
            if not uri_path.endswith('/'):
                uri_path += '/'
            save_uri = 'file:///' + uri_path.lstrip('/')
        
        messages.append(_("\n💾 Will be saved as: {}").format(save_uri))
        messages.append(_("   (Gramps will append 'listings/addons-XX.json')"))
        
        return True, '\n'.join(messages)
    
    def _validate_web_url(self, url):
        """
        Validate a web URL
        Returns (success: bool, message: str)
        """
        # Basic URL format check
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False, _(
                    "❌ Error: Invalid URL scheme.\n\n"
                    "URL must start with http:// or https://\n\n"
                    "Given: {}"
                ).format(url)
            
            if not parsed.netloc:
                return False, _(
                    "❌ Error: Invalid URL format.\n\n"
                    "URL must include a domain name.\n\n"
                    "Example: https://github.com/user/repo/raw/main/"
                ).format(url)
        
        except Exception as e:
            return False, _(
                "❌ Error: Malformed URL.\n\n{}\n\nURL: {}"
            ).format(str(e), url)
        
        # Ensure URL ends with /
        if not url.endswith('/'):
            url = url + '/'
        
        # Gramps appends /listings/ to the configured URL
        # So we need to test with /listings/ appended
        listings_url = urljoin(url, 'listings/')
        
        locale = glocale.language[0] if glocale.language else 'en'
        native_file = "addons-{}.json".format(locale)
        native_url = urljoin(listings_url, native_file)
        fallback_url = urljoin(listings_url, "addons-en.json")
        
        messages = [_("Testing URL: {}").format(url)]
        messages.append(_("Listings URL: {}").format(listings_url))
        
        # Try native language file first
        native_found = False
        try:
            messages.append(_("\nChecking for: {}").format(native_file))
            req = Request(native_url, headers={'User-Agent': 'Gramps'})
            with urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    native_found = True
                    messages.append(_("✅ Found: {}").format(native_file))
                    if isinstance(data, list):
                        messages.append(_("   Contains {} addon(s)").format(len(data)))
                    else:
                        messages.append(_("   ⚠️  Warning: Unexpected JSON format"))
        
        except HTTPError as e:
            if e.code == 404:
                messages.append(_("⚠️  Not found: {} (404)").format(native_file))
            else:
                messages.append(_("⚠️  HTTP Error {}: {}").format(e.code, native_file))
        
        except URLError as e:
            messages.append(_("⚠️  Network Error: {}").format(str(e.reason)))
        
        except json.JSONDecodeError as e:
            messages.append(_("❌ Error: Invalid JSON in {}").format(native_file))
            messages.append(_("   {}").format(str(e)))
        
        except Exception as e:
            messages.append(_("⚠️  Error: {}").format(str(e)))
        
        # Try fallback if native not found
        if not native_found:
            try:
                messages.append(_("\nChecking fallback: addons-en.json"))
                req = Request(fallback_url, headers={'User-Agent': 'Gramps'})
                with urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        messages.append(_("✅ Found: addons-en.json (fallback)"))
                        if isinstance(data, list):
                            messages.append(_("   Contains {} addon(s)").format(len(data)))
                        
                        messages.insert(0, _("✅ Success: Repository validated (using fallback)"))
                        messages.append(_("\n💾 Will be saved as: {}").format(url))
                        messages.append(_("   (Gramps will append 'listings/addons-XX.json')"))
                        return True, '\n'.join(messages)
            
            except HTTPError as e:
                if e.code == 404:
                    messages.append(_("❌ Not found: addons-en.json (404)"))
                    messages.append(_("\nError: No listings found."))
                    messages.append(_("The URL should point to a folder containing:"))
                    messages.append(_("  • listings/addons-en.json (required)"))
                    messages.append(
                        _("  • listings/addons-{}.json (optional)").format(locale)
                    )
                    return False, '\n'.join(messages)
                else:
                    messages.append(_("❌ HTTP Error {}").format(e.code))
                    return False, '\n'.join(messages)
            
            except URLError as e:
                messages.append(_("❌ Network Error: {}").format(str(e.reason)))
                messages.append(_("\nPossible causes:"))
                messages.append(_("  • No internet connection"))
                messages.append(_("  • URL is incorrect"))
                messages.append(_("  • Server is down"))
                messages.append(_("  • Firewall blocking access"))
                return False, '\n'.join(messages)
            
            except Exception as e:
                messages.append(_("❌ Error: {}").format(str(e)))
                return False, '\n'.join(messages)
        
        else:
            # Native file found - success!
            messages.insert(0, _("✅ Success: Repository validated"))
            messages.append(_("\n💾 Will be saved as: {}").format(url))
            messages.append(_("   (Gramps will append 'listings/addons-XX.json')"))
            return True, '\n'.join(messages)
    
    def _on_response(self, dialog, response_id):
        """
        Handle dialog response
        
        Note: Gramps Addon Manager expects URLs in specific formats:
        - Web: http://example.com/path/to/listings/
        - Local: file:///C:/path/to/listings/ (Windows)
        - Local: file:///path/to/listings/ (Unix)
        
        Local paths are converted to file:// URIs automatically.
        """
        if response_id == Gtk.ResponseType.HELP:
            # Test button clicked - validate
            self._test_url()
            dialog.stop_emission_by_name('response')  # Don't close dialog
        
        elif response_id == Gtk.ResponseType.OK:
            # OK button - save result
            url_text = self._get_url_text()
            is_folder = self.folder_radio.get_active()
            
            # For web URLs, ensure we don't have /listings/ (Gramps adds it)
            if not is_folder and url_text:
                url_text = url_text.rstrip('/')
                if url_text.endswith('/listings'):
                    url_text = url_text[:-9]  # Remove '/listings'
                # Ensure trailing slash
                if not url_text.endswith('/'):
                    url_text += '/'
            
            # For file:// URIs, they're already in correct format from browse/validation
            # Just ensure trailing slash
            if is_folder and url_text:
                if not url_text.endswith('/'):
                    url_text += '/'
            
            self.result = {
                'name': self.name_entry.get_text().strip(),
                'url': url_text,
                'is_folder': is_folder
            }
    
    def _test_url(self):
        """Test URL/path validation"""
        self.status_buffer.set_text(_("Validating...\n\nPlease wait..."))
        
        # Force UI update
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        url_text = self._get_url_text()
        if not url_text:
            self.status_buffer.set_text(_("❌ Error: URL/Path cannot be empty."))
            return
        
        # Auto-detect type: file:// URIs or OS paths are folders, http/https are web
        if url_text.startswith('file:///'):
            # It's a file:// URI
            success, message = self._validate_local_folder(url_text)
        elif url_text.startswith('http://') or url_text.startswith('https://'):
            # It's a web URL
            success, message = self._validate_web_url(url_text)
        elif os.path.exists(url_text):
            # It's an OS path (legacy or manually entered)
            success, message = self._validate_local_folder(url_text)
        else:
            # Assume it's a web URL
            success, message = self._validate_web_url(url_text)
        
        self.status_buffer.set_text(message)
    
    def run(self):
        """
        Run the dialog and return result
        
        :returns: Dictionary with 'name', 'url', 'is_folder' keys, or None if cancelled
        """
        self.dialog.run()
        self.dialog.destroy()
        return self.result
