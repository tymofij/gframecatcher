#!/usr/bin/python
#
# frameImage.py
# Copyright (C) Raul E. 2008 <>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

import pygtk
pygtk.require('2.0')
import gtk
import cairo
import pango

from gettext import gettext as _
import os

class FrameImage:
    mediaLibrary = None
    backgroundColor = (58082, 59110, 61166)
    size = (128, 128)
    margin = 10
    columns = 6
    showLogo = True
    showTimestamp = True
    font = None
    useBilinearResize = True
    translateHeaderText = False
    def __init__(self, aMediaLibrary):
        self.mediaLibrary = aMediaLibrary
        self.font = pango.FontDescription("Sans 12")
        
    def createImage(self, outputPath):
        if (self.mediaLibrary.images == None):
            raise Exception(_("There is no images"))
        
        fontHeigth = self.font.get_size() / pango.SCALE
        logoSize = 0, 0
        numRows = len(self.mediaLibrary.images) / self.columns
        if(len(self.mediaLibrary.images) % self.columns) != 0:
            numRows = numRows + 1
        width = self.columns * self.size[0] + self.margin * (self.columns -1) + fontHeigth * 2
        height = numRows * (self.size[1] + self.margin) + fontHeigth * 8

        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        context = cairo.Context(surface)
        context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        
        context.set_source_rgb(self.backgroundColor[0] / 65535.0, self.backgroundColor[1] / 65535.0, self.backgroundColor[2] / 65535.0)
        context.rectangle(0, 0, width, height)
        context.fill()

        if(self.showLogo == True):
            logoSize = 64, 64
            fileDirectory = os.path.dirname(__file__)
            myImage = gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/gframecatcher64.png"))
            self.__addPixBufToCairo(myImage, logoSize, fontHeigth, fontHeigth, context)

        filemameText = "Filename : "
        codecText = "Codec : "
        resolutionText = "Resolution : "
        durationText = "Duration : "

        if(self.translateHeaderText == True):
            filemameText = _("Filename : ")
            codecText = _("Codec : ")
            resolutionText = _("Resolution : ")
            durationText = _("Duration : ")

        self.__drawText(fontHeigth + logoSize[0], fontHeigth * 2 + 2, filemameText + self.mediaLibrary.getFilename(), (0, 0, 0), context)
        self.__drawText(fontHeigth + logoSize[0], fontHeigth * 3 + 2, codecText + self.mediaLibrary.codec, (0, 0, 0), context)
        self.__drawText(fontHeigth + logoSize[0], fontHeigth * 4 + 2, resolutionText + str(self.mediaLibrary.width) + "x" + str(self.mediaLibrary.height), (0, 0, 0), context)
        self.__drawText(fontHeigth + logoSize[0], fontHeigth * 5 + 2, durationText + self.mediaLibrary.getDuration(), (0, 0, 0), context)
        xPos = fontHeigth
        yPos = fontHeigth * 8
        count = 0
        for anImage in self.mediaLibrary.images:
            self.__addPixBufToCairo(anImage[0], self.size, xPos, yPos, context)
            if(self.showTimestamp == True):
                self.__drawText(xPos + 2, yPos + self.size[1] - 2, anImage[1], (1, 1, 1), context)
            xPos = xPos + self.size[0] + self.margin
            count = count + 1
            if count % self.columns == 0:
                yPos = yPos + self.size[1] + self.margin
                xPos = fontHeigth
                count = 0
            while gtk.events_pending():
                gtk.main_iteration()
        surface.write_to_png(outputPath)
        del context
        del surface

    def saveAllTo(self, directory):
        if (self.mediaLibrary.images == None):
            raise Exception(_("There is no images"))
        count = 0
        path = os.path.join(directory, self.mediaLibrary.getFilename()) + "_"
        for anImage in self.mediaLibrary.images:
            anImage[0].save(path + str(count) + ".png", "png")
            count = count + 1
            while gtk.events_pending():
                gtk.main_iteration()
        
    def __drawText(self, x , y, text, color, context):
        context.set_source_rgb(color[0], color[1], color[2])
        context.move_to(x, y)
        cairoFontWeight = cairo.FONT_WEIGHT_NORMAL
        cairoFontSlant = cairo.FONT_SLANT_NORMAL
        if(self.font.get_weight() == pango.WEIGHT_BOLD or self.font.get_weight() == pango.WEIGHT_ULTRABOLD):
            cairoFontWeight = cairo.FONT_WEIGHT_BOLD
        if(self.font.get_style() == pango.STYLE_ITALIC or self.font.get_style() == pango.STYLE_OBLIQUE):
            cairoFontSlant = cairo.FONT_SLANT_ITALIC
        context.select_font_face(self.font.get_family(), cairoFontSlant, cairoFontWeight)
        context.set_font_size(self.font.get_size() / pango.SCALE)
        context.show_text(text)
        context.stroke()
        
    def __addPixBufToCairo(self, pixbuf, size, x, y, context):
        myImage = None
        if(self.useBilinearResize == True):
            myImage = pixbuf.scale_simple(size[0], size[1], gtk.gdk.INTERP_BILINEAR)
        else:
            myImage = pixbuf.scale_simple(size[0], size[1], gtk.gdk.INTERP_NEAREST)
        
        gdkcontext = gtk.gdk.CairoContext(context)
        gdkcontext.set_source_pixbuf(myImage, x, y)
        gdkcontext.paint()

