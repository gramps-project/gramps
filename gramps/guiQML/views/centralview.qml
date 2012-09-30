/*#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: __init__.py 13807 2009-12-15 05:56:12Z pez4brian $
*/

import Qt 4.7

import "../qmlwidgets" as Widgets

Rectangle{
  id: container
  color: "#343434"
  ListView {
    id: detviewSumList
    y: 25
    width: parent.width
    height: parent.height-25
    model: DetViewSumModel
    delegate: Component {
      Rectangle { 
        width: detviewSumList.width 
        height: 40 
        color: ((index % 2 == 0)?'#222':'#111') 
        Text { 
          id: detviewname 
          elide: Text.ElideRight 
          text: model.name.name 
          color: 'white'
          font.bold: true 
          anchors.leftMargin: 10 
          anchors.fill: parent 
          verticalAlignment: Text.AlignVCenter   
        } 
        MouseArea { 
          anchors.fill: parent 
          onClicked: { 
            CentralView.detviewSelected(model.name)  
          } 
        } 
      } 
    } 
  }
  // TOP BAR
  Widgets.TopBar {
    text: Const.titlelabel
  }
}
