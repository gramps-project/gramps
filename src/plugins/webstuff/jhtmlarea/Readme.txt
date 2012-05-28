/* jHtmlArea - WYSIWYG Html Editor jQuery Plugin
 * Copyright (c) 2009 Chris Pietschmann
 * http://jhtmlarea.codeplex.com
 * Licensed under the Microsoft Reciprocal License (Ms-RL)
 * http://jhtmlarea.codeplex.com/license
*/

EXAMPLE USAGE:
-----------------------
See "Default.htm" for example usages.
Or, check out http://jhtmlarea.codeplex.com


CHANGE LOG
-----------------------
v0.7.0
- Fixed ColorPickerMenu positioning when placed within a "position: relative"
div element.

- Fixed ColorPickerMenu to auto-hide after a short delay (1 second) once the
user moves the mouse off the menu.

- Fixed Form Submit issue that caused the text to not be posted. Also fixed a
related issue with ASP.NET Postbacks.

- Added jHtmlArea.p method and "paragraph" functionality + toolbar button
This allows the user to change the formatting from <H1>, <H2>, etc. to <P>

- Added an "Automatic" color option to the ColorPickerMenu.


v0.6.0
- Hide All Toolbar buttons except the "html" button when entering
HTML Source view (via clicking "html" button or executing
jHtmlArea.showHTMLView). When toggling view back to the WYSIWYG editor
all other buttons will then be shown again.

- Added jHtmlArea.dispose method - Allows you to remove the WYSIWYG
editor, and go back to having a plain TextArea. Beware, there is a
memory leak when using this method; it's not too bad, but you want
to call this as few a number of times if you can. The memory leak
is due to the way the browsers handle removing DOM Elements.

- Added Indent and Outdent functionality - This includes toolbar buttons
and jHtmlArea.indent and jHtmlArea.outdent buttons.

- Added justifyLeft, justifyCenter, justifyRight functionality and toolbar
buttons.

- Added insertHorizontalRule functionality and toolbar button. This adds a
<hr> tag to the currently selected area.

- Added an "alias" method for jHtmlArea.execCommand named "ec" to help reduce the
file size of the script.

- Added increaseFontSize and decreaseFontSize functionality and toolbar buttons.
The increaseFontSize and decreaseFontSize doesn't currently work in Safari.

- Added forecolor functionality - Changes a font color for the selection or at the
insertion point. Requires a color value string to be passed in as a value argument.

- Fixed bug in jHtmlArea.toString method

- Added jHtmlArea.queryCommandValue method and it's alias "jHtmlArea.qc"

- Added the jHtmlAreaColorPickerMenu plugin/extension that resides within the
"jHtmlAreaColorPickerMenu.js" file. This file includes a somewhat generic color
picker menu that can be used for any purpose, plus it includes the code to wire
up and override the "stock" jHtmlColor.forecolor functionality and inject the new
Color Picker Menu functionality in it's place when you click on the "forecolor"
toolbar button.

- Changed the "execCommand" and "ec" second parameter to default to "false" if not
specified, and third parameter to default to "null" if not specified. This helps to
reduce the overall file size of the script.

- Added support for Toolbar Button Grouping, now with the additional buttons included
in this release, or even when any custom buttons are used, they will be able to display
nicely by "auto-wrapping" to the next line.

- Added a gradient background to the Toolbar Button Groups, with a slight reverse
gradient on the Buttons when the mouse is hovered over.


v0.5.0 - Initial Release




ICONS / IMAGES:
-----------------------

Some of the Icons within the jHtmlArea.png file are from the
Silk icon set at www.famfamfam.com.
They are licensed under the following license:

Silk icon set 1.3
_________________________________________
Mark James
http://www.famfamfam.com/lab/icons/silk/
_________________________________________

This work is licensed under a
Creative Commons Attribution 2.5 License.
[ http://creativecommons.org/licenses/by/2.5/ ]

This means you may use it for any purpose,
and make any changes you like.
All I ask is that you include a link back
to this page in your credits.

Are you using this icon set? Send me an email
(including a link or picture if available) to
mjames@gmail.com

Any other questions about this icon set please
contact mjames@gmail.com