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
    import StringIO
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
        self.src = source

    if no_pil:

        def size(self):
            img = GdkImlib.Image(self.src)
            return (img.rgb_width,img.rgb_height)

        def fmt_thumbnail(self,dest,width,height,cnv):
            w = int(width)
            h = int(height)
            cmd = "%s -geometry %dx%d '%s' '%s:%s'" % (const.convert,w,h,self.src,cnv,dest)
            os.system(cmd)

        def fmt_convert(self,dest,cnv):
            cmd = "%s '%s' '%s:%s'" % (const.convert,self.src,cnv,dest)
            os.system(cmd)

        def fmt_data(self,cnv):
            cmd = "%s '%s' '%s:-'" % (const.convert,cnv,self.src)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf

        def fmt_scale_data(self,x,y,cnv):
            cmd = "%s -geometry %dx%d '%s' '%s:-'" % (const.convert,x,y,cnv,self.src)
            r,w = popen2.popen2(cmd)
            buf = r.read()
            r.close()
            w.close()
            return buf

        def eps_data(self):
            return self.fmt_data("eps")

        def eps_scale_data(self,x,y):
            return self.fmt_scale_data("eps")

    else:

        def size(self):
            return PIL.Image.open(self.src).size

        def fmt_thumbnail(self,dest,width,height,pil):
            im = PIL.Image.open(self.src)
            im.thumbnail((width,height))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(dest,pil)
        
        def fmt_convert(self,dest,pil):
            im = PIL.Image.open(self.src)
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(dest,pil)

        def fmt_data(self,pil):
            im = PIL.Image.open(self.src)
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring(pil,"RGB")

        def fmt_scale_data(self,x,y,pil):
            im = PIL.Image.open(self.src)
            im.thumbnail((x,y))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            return im.tostring(pil,"RGB")

        def eps_data(self):
            g = StringIO.StringIO()
            im = PIL.Image.open(self.src)
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(g,"eps")
            g.seek(0)
            buf = g.read()
            g.close()
            return buf

        def eps_scale_data(self,x,y):

            # need to write to a file-like object, otherwise
            # PIL won't generate the header information
            g = StringIO.StringIO()
            im = PIL.Image.open(self.src)
            im.thumbnail((x,y))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(g,"eps")
            g.seek(0)
            buf = g.read()
            g.close()
            return buf

    def jpg_thumbnail(self,dest,width,height):
        self.fmt_thumbnail(dest,width,height,"jpeg")

    def png_thumbnail(self,dest,width,height):
        self.fmt_thumbnail(dest,width,height,"png")

    def eps_thumbnail(self,dest,width,height):
        self.fmt_thumbnail(dest,width,height,"eps")

    def jpg_convert(self,dest):
        self.fmt_convert(dest,"jpeg")

    def png_convert(self,dest):
        self.fmt_convert(dest,"png")

    def eps_convert(self,dest):
        self.fmt_convert(dest,"eps")

    def jpg_data(self):
        return self.fmt_data("jpeg")

    def png_data(self):
        return self.fmt_data("png")

    def jpg_scale_data(self,x,y):
        return self.fmt(x,y,"jpeg")

    def png_scale_data(self,x,y):
        return self.fmt(x,y,"png")


if __name__ == "__main__":

    import sys
    
    img = ImgManip(sys.argv[1])
    img.jpg_thumbnail("foo.jpg",50,50)
    img.png_thumbnail("foo.png",50,50)
    img.eps_thumbnail("foo.eps",50,50)





