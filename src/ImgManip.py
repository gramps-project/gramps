#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import md5
import tempfile

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Mime
import Config
import Utils

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class ImgManip:
    def __init__(self, source):
        self.src = source
        try:
            self.img = gtk.gdk.pixbuf_new_from_file(self.src)
            self.width = self.img.get_width()
            self.height = self.img.get_height()
        except gobject.GError:
            self.width = 0
            self.height = 0

    def size(self):
        return (self.width, self.height)
    
    def fmt_thumbnail(self,dest,width,height,cnv):
        scaled = self.img.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
        scaled.save(dest,cnv)
        
    def fmt_data(self, cnv):
        fd, dest = tempfile.mkstemp()
        self.img.save(dest,cnv)
        fh = open(dest,mode='rb')
        data = fh.read()
        fh.close()
        try:
            os.unlink(dest)
        except:
            pass
        return data

    def fmt_scale_data(self, x, y, cnv):
        fd, dest = tempfile.mkstemp()
        scaled = self.img.scale_simple(int(x), int(y), gtk.gdk.INTERP_BILINEAR)
        scaled.save(dest,cnv)
        fh = open(dest,mode='rb')
        data = fh.read()
        fh.close()
        try:
            os.unlink(dest)
        except:
            pass
        return data

    def jpg_thumbnail(self, dest, width, height):
        self.fmt_thumbnail(dest, width, height, "jpeg")

    def jpg_data(self):
        return self.fmt_data("jpeg")

    def png_data(self):
        return self.fmt_data("png")

    def jpg_scale_data(self, x, y):
        return self.fmt_scale_data(x, y, "jpeg")

    def png_scale_data(self,x,y):
        return self.fmt_scale_data(x, y, "png")


def _build_thumb_path(path):
    m = md5.md5(path)
    return os.path.join(const.thumb_dir, m.hexdigest()+'.png')

def run_thumbnailer(mtype, frm, to, size=const.thumbScale):
    if const.use_thumbnailer and os.path.isfile(frm):
        sublist = {
            '%s' : "%dx%d" % (int(size),int(size)),
            '%u' : frm,
            '%o' : to,
            }

        base = '/desktop/gnome/thumbnailers/%s' % mtype.replace('/','@')

        cmd = Config.get_string(base + '/command')
        enable = Config.get_bool(base + '/enable')

        if cmd and enable:
            cmdlist = map(lambda x: sublist.get(x,x),cmd.split())
            os.spawnvpe(os.P_WAIT, cmdlist[0], cmdlist, os.environ)
            return True
        else:
            return False
    return False

def set_thumbnail_image(path, mtype=None):
    if mtype and not mtype.startswith('image/'):
        run_thumbnailer(mtype,path,_build_thumb_path(path))
    else:
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            w = pixbuf.get_width()
            h = pixbuf.get_height()
            scale = const.thumbScale / (float(max(w,h)))
            
            pw = int(w*scale)
            ph = int(h*scale)
            
            pixbuf = pixbuf.scale_simple(pw,ph,gtk.gdk.INTERP_BILINEAR)
            pixbuf.save(_build_thumb_path(path),"png")
        except:
            pass

def get_thumbnail_image(path, mtype=None):
    filename = _build_thumb_path(path)

    try:
        path = Utils.find_file( path)
        if not os.path.isfile(filename):
            set_thumbnail_image(path,mtype)
        elif os.path.getmtime(path) > os.path.getmtime(filename):
            set_thumbnail_image(path,mtype)
        return gtk.gdk.pixbuf_new_from_file(filename)
    except (gobject.GError, OSError):
        if mtype:
            return Mime.find_mime_type_pixbuf(mtype)
        else:
            return gtk.gdk.pixbuf_new_from_file(os.path.join(
                const.image_dir,"document.png"))

def get_thumbnail_path(path, mtype=None):
    filename = _build_thumb_path(path)
    if not os.path.isfile(filename):
        set_thumbnail_image(path,mtype)
    return filename

def get_thumb_from_obj(obj):
    mtype = obj.get_mime_type()
    if mtype.startswith("image/"):
        image = get_thumbnail_image(obj.get_path())
    else:
        image = Mime.find_mime_type_pixbuf(mtype)
    if not image:
        image = gtk.gdk.pixbuf_new_from_file(const.icon)
    return image
