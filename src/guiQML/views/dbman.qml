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
  width: 400 
  height: 600
  
  //Delegate for a famtree entry. Two modes:
  // 1. List mode (default): shows just the name and allows selection
  // 2. Details mode: show extra information
  Component { 
    id: famtreeDelegate
    Item {
      id: famtree
        // Create a property to contain the visibility of the details.
        // We bind multiple element's opacity to this one property,
      property real detailsOpacity : 0

      width: pythonList.width 
      height: 30 
      
      Rectangle { 
        id: background
        anchors.fill: parent
        color: ((index % 2 == 0)?'#222':'#111') 
        radius: 5  //rounded corners
      }
      //click shows details, close button must be clicked to go back to normal
      MouseArea { 
        anchors.fill: parent 
        onClicked: {  
          famtree.state = 'Details'
        }
      }
      //Now the data on the background, detailsOpacity for what to see
      Row{
        id: topfamtreelayout
        width: parent.width
        anchors.verticalCenter: parent.verticalCenter
        x:10
        spacing:10
        Column {
          id: innerfamtreecol
          width: parent.width - 70; 
          spacing: 5
          Text { 
            id: title 
            text: model.name.name 
            color: 'white'
            font.bold: true 
            opacity: (famtree.detailsOpacity ? 0 : 1 )
          }
          Item {
            id: titleEdit
            height: 20
            width: parent.width
            opacity: famtree.detailsOpacity
            
            TextInput {
              id: titleinput
              text: model.name.name
              anchors.fill: parent.fill
              color: 'white'
              cursorVisible: true; font.bold: true
            }
            Keys.forwardTo: [(returnKey), (titleinput)]
            Item {
              id: returnKey
              Keys.onReturnPressed: model.name.name = titleinput.text
              Keys.onEnterPressed: model.name.name = titleinput.text
              Keys.onEscapePressed: titleinput.text = model.name.name
            }
          }
          Text { 
            id: lastaccess 
            elide: Text.ElideRight 
            text: model.name.last_access
            color: 'white'
            font.bold: true 
            opacity: famtree.detailsOpacity
          }
        }
        Image {
          id:famtreeimage
          anchors.verticalCenter: topfamtreelayout.verticalCenter
          width: 22; height: 22
          anchors.rightMargin: 20
          source: Const.famtreeicon
          opacity: famtree.detailsOpacity
        }
      }
      Row{
        id: buttonfamtreelayout
        anchors.top: topfamtreelayout.bottom
        anchors.rightMargin: 20
        spacing: 20
        // A button to select the famtree
        Widgets.TextButton {
          y: 10
          opacity: famtree.detailsOpacity
          text: "Open"
          onClicked: {
            DbManager.famtreeSelected(model.name)
          }
        }// A button to close the detailed view, i.e. set the state back to default ('').
        Widgets.TextButton {
            y: 10
            opacity: famtree.detailsOpacity
            text: "Close"
            onClicked: famtree.state = '';
        }
      }
      
      states: State {
          name: "Details"
          PropertyChanges { target: famtree; detailsOpacity: 1; x: 0 } // Make details visible
          PropertyChanges { target: famtree; height: 120 } // Fill the entire list area with the detailed view

          // Move the list so that this item is at the top.
          PropertyChanges { target: famtree.ListView.view; explicit: true; contentY: famtree.y }

          // Disallow flicking while in in detailed view
          PropertyChanges { target: famtree.ListView.view; interactive: false }
      }

      transitions: Transition {
          // Make the state changes smooth
          ParallelAnimation {
              ColorAnimation { property: "color"; duration: 500 }
              NumberAnimation { duration: 300; properties: "detailsOpacity,x,contentY,height,width" }
          }
      }
    }
  }
  ListView { 
    id: pythonList 
    y: 25
    width: parent.width
    height: parent.height-20-40
    //anchors.top: container.top
    //anchors.bottom: container.bottom
    //anchors.fill: parent
    //anchors.leftMargin: 5
    //anchors.rightMargin: 5
    model: FamTreeListModel 
    delegate: famtreeDelegate 
  }
  // TOP BAR
  Widgets.TopBar {
    text: Const.titlelabel
  }
  // BOTTOM BAR
  Item {
    id: bottombar
    y: parent.height-40
    width: parent.width
    height: 40
    Rectangle {
      anchors.fill: parent
      color: "#343434"
    }
    Row {
      anchors.left: parent.left
      anchors.leftMargin: 10 
      anchors.verticalCenter: parent.verticalCenter
      spacing: 10
      Widgets.TextButton {
        text: Const.addbtnlbl
        onClicked: {DbManager.addfamtree("")
        }
      }
    }
  }
}