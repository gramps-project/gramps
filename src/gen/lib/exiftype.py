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

    """"
    Exif Keys/ Tags for Images
    """

    UNKNOWN                            = -1
    ExifImageMake                      =  0
    ExifImageModel                     =  1
    ExifImageOreintation               =  2
    ExifImageXRes                      =  3
    ExifImageYRes                      =  4
    ExifImageResUnit                   =  5
    ExifImageDT                        =  6
    ExifImageYcbCrPositioning          =  7
    ExifImageExifTag                   =  8
    
    ExifPhotoExpsTime                  =  9
    ExifPhotoFNumber                   = 10
    ExifPhotoExpsProgram               = 11
    ExifPhotoExifVersion               = 12
    ExifPhotoDTOriginal                = 13
    ExifPhotoDTDigitized               = 14
    ExifPhotoComponentsConfiguration   = 15
    ExifPhotoCompressedBitsPerPixel    = 16
    ExifPhotoExposireBiasValue         = 17
    ExifPhotoMaxAperatureValue         = 18
    ExifPhotoMeteringMode              = 19
    ExifPhotoLightSource               = 20
    ExifPhotoFlash                     = 21
    ExifPhotoFocaLight                 = 22
    ExifPhotoFlashpixVersion           = 23
    ExifPhotoColorSpace                = 24
    ExifPhotoPixelXDimension           = 25
    ExifPhotoPixelYDimension           = 26
    ExifPhotoInteroperabilityTag       = 27
    ExifPhotoFileSource                = 28
    ExifPhotoSceneTags                 = 29
    ExifPhotoCustomRendered            = 30
    ExifPhotoExpsMode                  = 31
    ExifPhotoWhiteBalance              = 32
    ExifPhotoSceneCaptureType          = 33

    ExifThumbnailCompression           = 34
    ExifThumbnailMake                  = 35
    ExifThumbnailModel                 = 36
    ExifThumbnailOreintation           = 37
    ExifThumbnailXRes                  = 38
    ExifThumbnailYRes                  = 39
    ExifThumbnailResUnit               = 40
    ExifThumbnailDT                    = 41
    ExifThumbnailJPEGInterchangeFormat = 42
    ExifThumbnailJPEGInterchangeLength = 43
    ExifThumbnailYcbCrPositioning      = 44

    ExiftopInteroperabilityIndex       = 45
    ExiftopInteroperabilityVersion     = 46

    _DATAMAP = [
        [UNKNOWN,  _("Known"),  "Unknown"], 
        [ExifImageMake,   _("Image Make"),  "Exif.Image.Make"],
        ExifImageModel,  _("Image Model"),  "Exif.Image.Model"],
        ExifImageOreintation,  __("Image oreintation"), "Exif.Image.oreintation"],
        ExifImageXRes,   _("Image X Resolution"),  "Exif.Image.XResolution"],
        ExifImageYRes,  __("Image Y Resolution"),  "Exif.Image.YResolution"],
        ExifImageResUnit,   _("Image Resolution Unit"),  "Exif.Image.ResolutionUnit"],
        ExifImageDT,   _("Image Date Time"),  "Exif.Image.DateTime"],
        ExifImageYcbCrPositioning,  _("Image Ycb Cr Positioning"),  "Exif.Image.YcbCrPositioning"],
        ExifImageExifTag,   _("Image Exif Tag"),  "Exif.Image.ExifTag"], 

        ExifPhotoExpsTime,   _("Photo Exposure Time"),  "Exif.Photo.ExposureTime"], 
        ExifPhotoFNumber,   _("Photo F Number"),  "Exif.Photo.FNumber"],
        ExifPhotoExpsProgram,   _("Photo Exposure Program"),  "Exif.Photo.ExposureTime"],
        ExifPhotoExifVersion,   _("Photo Exif Version"),  "Exif.Photo.ExifVersion"],
        ExifPhotoDTOriginal,   _("Photo Date Time Original"),  "Exif.Photo.DateTimeOriginal"], 
        ExifPhotoDTDigitized,  _("Photo Date Time Digitized"),  "Exif.Photo.DateTimeDigitized"],
        ExifPhotoComponentsConfiguration,  _("Photo Component Configuration"), "Exif.Photo.ComponentsConfiguration"],
        ExifPhotoCompressedBitsPerPixel,  _("Photo Compressed Bits Per Pixel"),  "Exif.Photo.CompressedBitsPerPixel"],
        ExifPhotoExpsBiasValue,  _("Photo Exposure Bias Value"),  "Exif.Photo.ExposureBiasValue"],
        ExifPhotoMaxAperatureValue,  _("Photo Max. Aperature Value"),  "Exif.Photo.MaxAperatureValue"],
        ExifPhotoMeteringMode,  _("Photo Metering Mode"),  "Exif.Photo.MeteringMode"],
        ExifPhotoLightSource,  _("Photo Light Source"),  "Exif.Photo.LightSource"],
        ExifPhotoFlash,  _("Photo Flash"),  "Exif.Photo.Flash"],
        ExifPhotoFocaLight,  _("Photo Focal Light"),  "Exif.Photo.FocalLight"],
        ExifPhotoFlashpixVersion,  _("Photo Flash Pixel Version"),  "Exif.Photo.FlashpixVersion"],
        ExifPhotoColorSpace,  _("Photo Color Space"),  "Exif.Photo.ColorSpace"],
        ExifPhotoPixelXDimension,  _("Photo Pixrl X Dimension"),  "Exif.Photo.PixelXDminension"],
        ExifPhotoPixelYDimension,  _("Photo Pixel Y Dimension"),  "Exif.Photo.PixelYDimension"],
        ExifPhotoInteroperabilityTag,  _("Photo Interoperability Tag"),  "Exif.Photo.InteroperabilityTag"],
        ExifPhotoFileSource,  _("Photo File Source"),  "Exif.Photo.FileSource"],
        ExifPhotoSceneTags,  _("Photo Scene tags"),  "Exif.Photo.SceneTags"],
        ExifPhotoCustomRendered,  _("Photo Custom Rendered"),  "Exif.photo.CustomRendered"],
        ExifPhotoExpsMode,  _("Photo Exposure Mode"),  "Exif.Photo.ExposureMode"],
        ExifPhotoWhiteBalance,  _("Photo White Balance"),  "Exif.Photo.WhiteBalance"],
        ExifPhotoSceneCaptureType,  _("Photo Scene Capture Type"),  "Exif.Photo.SceneCaptureType"],

        ExifThumbnailCompression,  _("Thumbnail Compression"), ""Exif.Thumbnail.Compression"],
        ExifThumbnailMake,  _("Thumbnail Make"),  "Exif.Thumbnail.Make"],
        ExifThumbnailModel,  _("Thumbnail Model"),  "Exif.Thumbnail.Model"],
        ExifThumbnailOreintation,  _("Thumbnail Oreintation"),  "Exif.Thumbnail.Oreintation"],
        ExifThumbnailXRes,  _("Thumbnail X Resolution"),  "Exif.Thumbnail.XResolution"],
        ExifThumbnailYRes,  _("Thumbnail Y Resolution"),  "Exif.Thumbnail.YResolution"],
        ExifThumbnailResUnit,  _("Thumbnail Resolution Unit"),  "Exif.Thumbnail.YResolutionUnit"],
        ExifThumbnailDT,  _("Thumbnail Date Time"),  "Exif.Thumbnail.DateTime"],
        ExifThumbnailJPEGInterchangeFormat,  _("Jpeg Interchange Format"),  "Exif.Thumbnail.JPEGInterchangeFormat"],
        ExifThumbnailJPEGInterchangeLength,   _("JPEG Interchange Length"),  "Exif.Thumbnail.JPEGInterchangeLength"],
        ExifThumbnailYcbCrPositioning,  _("Thumbnail Ycb Cr Positioning"),  "Exif.Thumbnail.YcbCrPositioning"],

        ExiftopInteroperabilityIndex,  _("Top Interoperability Index"),  "Exif.top.InteroperabilityIndex"],
        ExiftopInteroperabilityVersion,  _("Top Interoperability Version"),  "Exif.top.InteroperabilityVersion"]
        ]
