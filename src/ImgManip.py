#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import os
import const

#-------------------------------------------------------------------------
#
# Check for the python imaging library
#
#-------------------------------------------------------------------------
try:
    import PIL.Image
    no_pil = 0
except:
    import popen2
    import GDK
    import GTK
    import gtk
    import GdkImlib
    no_pil = 1

class ImgManip:
    def __init__(self,source):
        self.source = source

    def jpg_thumbnail(self,dest,width,height):
        if no_pil:
            w = int(width)
            h = int(height)
            cmd = "%s -geometry %dx%d '%s' 'jpg:%s'" % (const.convert,w,h,self.source,dest)
            os.system(cmd)
        else:
            im = PIL.Image.open(self.source)
            im.thumbnail((width,height))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(dest,"JPEG")

    def png_thumbnail(self,dest,width,height):
        if no_pil:
            w = int(width)
            h = int(height)
            cmd = "%s -geometry %dx%d '%s' 'png:%s'" % (const.convert,w,h,self.source,dest)
            os.system(cmd)
        else:
            im = PIL.Image.open(self.source)
            im.thumbnail((width,height))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(dest,"PNG")

    def size(self):
        if no_pil:
            img = GdkImlib.Image(self.source)
            return (img.rgb_width,img.rgb_height)
        else:
            return PIL.Image.open(self.source).size
    
    def jpg_data(self):
        if no_pil:
            cmd = "%s '%s' 'jpg:-'" % (const.convert,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            im = PIL.Image.open(self.source)
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring("jpeg","RGB")

    def jpg_scale_data(self,x,y):
        if no_pil:
            cmd = "%s -geometry %dx%d '%s' 'jpg:-'" % (const.convert,x,y,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            im = PIL.Image.open(self.source)
            im.thumbnail((x,y))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring("jpeg","RGB")

    def eps_data(self):
        if no_pil:
            cmd = "%s '%s' 'eps:-'" % (const.convert,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            import StringIO

            g = StringIO.StringIO()
            im = PIL.Image.open(self.source)
            im.save(g,"eps")
            g.seek(0)
            buf = g.read()
            g.close()
            return buf

    def eps_scale_data(self,x,y):
        if no_pil:
            cmd = "%s -geometry %dx%d '%s' 'eps:-'" % (const.convert,x,y,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            import StringIO

            g = StringIO.StringIO()
            im = PIL.Image.open(self.source)
            im.thumbnail((x,y))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(g,"eps")
            g.seek(0)
            buf = g.read()
            g.close()
            return buf

    def png_data(self):
        if no_pil:
            cmd = "%s -geometry '%s' 'jpg:-'" % (const.convert,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            im = PIL.Image.open(self.source)
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring("png","RGB")

    def png_scale_data(self,x,y):
        if no_pil:
            cmd = "%s -geometry %dx%d '%s' 'jpg:-'" % (const.convert,x,y,self.source)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf
        else:
            im = PIL.Image.open(self.source)
            im.thumbnail((x,y))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring("png","RGB")

            
