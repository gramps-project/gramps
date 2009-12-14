#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2009 Rob G. Healey <robhealey1@gmail.com>
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
# $Id: exiftype.py 13797 2009-12-13 07:00.00Z robhealey1Z robhealey1 $

"""
Provide the different exif types
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.grampstype import GrampsType

class ExifType(GrampsType):

    ExifImageMake = 0
    ExifImageModel = 1
    ExifImageOreintation = 2
    ExifImageXResolution = 3
    ExifImageYResolution = 4
    ExifImageResolutionUnit = 5
    ExifImageDateTime = 6
    ExifImageYcbCrPositioning = 7
    ExifImageExifTag = 8
    
    ExifPhotoExposureTime = 9
    ExifPhotoFNumber = 10
    ExifPhotoExposureProgram = 11
    ExifPhotoExifVersion = 12
    ExifPhotoDateTimeOriginal = 13
    ExifPhotoDateTimeDigitized = 14
    ExifPhotoComponentsConfiguration = 15
    ExifPhotoCompressedBitsPerPixel = 16
    ExifPhotoExposireBiasValue = 17
    ExifPhotoMaxAperatureValue = 18
    ExifPhotoMeteringMode = 19
    ExifPhotoLightSource = 20
    ExifPhotoFlash = 21
    ExifPhotoFocaLight = 22
    ExifPhotoFlashpixVersion = 23
    ExifPhotoColorSpace = 24
    ExifPhotoPixelXDimension = 25
    ExifPhotoPixelYDimension = 26
    ExifPhotoInteroperabilityTag = 27
    ExifPhotoFileSource = 28
    ExifPhotoSceneTags = 29
    ExifPhotoCustomRendered = 30
    ExifPhotoExposureMode = 31
    ExifPhotoWhiteBalance = 32
    ExifPhotoSceneCaptureType = 33

    ExifThumbnailCompression = 34
    ExifThumbnailMake = 35
    ExifThumbnailModel = 36
    ExifThumbnailOreintation = 37
    ExifThumbnailXResolution = 38
    ExifThumbnailYResolution = 39
    ExifThumbnailResolutionUnit = 40
    ExifThumbnailDateTime = 41
    ExifThumbnailJPEGInterchangeFormat = 42
    ExifThumbnailJPEGInterchangeLength = 43
    ExifThumbnailYcbCrPositioning = 44

    ExiftopInteroperabilityIndex = 45
    ExiftopInteroperabilityVersion = 46
