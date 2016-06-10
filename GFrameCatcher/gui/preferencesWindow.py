#!/usr/bin/python
#
# preferencesWindow.py
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

import os
import time
import datetime

class PreferencesWindow :
    __preferences = None
    def __init__(self, parent, preferences):
        fileDirectory = os.path.dirname(__file__)
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(fileDirectory , "ui/preferencesWindow.ui"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("dialog1")
        self.window.set_transient_for(parent)
        self.window.set_destroy_with_parent(True)
#        self.builder.get_object("imgColumns").set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/column.png")))
#        self.builder.get_object("imgWidth").set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/imagew.png")))
#        self.builder.get_object("imgHeight").set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/imageh.png")))
#        self.builder.get_object("imgMargin").set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/margin.png")))
        self.__preferences = preferences
    def __savePreferences(self):
        self.__preferences.setValue("Image", "columns",str(self.builder.get_object("spnColumns").get_value_as_int()))
        self.__preferences.setValue("Image", "width", str(self.builder.get_object("spnWidth").get_value_as_int()))
        self.__preferences.setValue("Image", "height", str(self.builder.get_object("spnHeight").get_value_as_int()))
        self.__preferences.setValue("Image", "margin", str(self.builder.get_object("spnMargin").get_value_as_int()))
        self.__preferences.setValue("Image", "bilinear", str(int(self.builder.get_object("chkBilinear").get_active())))
        self.__preferences.setValue("Image", "font", self.builder.get_object("fontButton").get_font_name())
        bgColor = self.builder.get_object("colorBackground").get_color()
        rgbColor = str(bgColor.red) + "," + str(bgColor.green) + "," + str(bgColor.blue)
        self.__preferences.setValue("Image", "backgroundColor", rgbColor)
        self.__preferences.setValue("Image", "timeStamp", str(int(self.builder.get_object("chkTimestamps").get_active())))
        self.__preferences.setValue("Image", "logo", str(int(self.builder.get_object("chkLogo").get_active())))
        self.__preferences.setValue("Image", "translateHeaderText", str(int(self.builder.get_object("chkTranslate").get_active())))
        self.__preferences.setValue("Capture", "frames", str(self.builder.get_object("spnCaptureNum").get_value_as_int()))
        captureTime = datetime.timedelta(minutes=int(self.builder.get_object("spnCaptureMin").get_value_as_int()), seconds=int(self.builder.get_object("spnCaptureSec").get_value_as_int()))
        self.__preferences.setValue("Capture", "seconds", str(captureTime.seconds))
        if(self.builder.get_object("rbCaptureSeconds").get_active() == True):
             self.__preferences.setValue("Capture", "type", "SECONDS")
        else :
             self.__preferences.setValue("Capture", "type", "FRAMES")

    def __loadPreferences(self):
        self.builder.get_object("spnColumns").set_value(int(self.__preferences.getValue("Image", "columns")))
        self.builder.get_object("spnWidth").set_value(int(self.__preferences.getValue("Image", "width")))
        self.builder.get_object("spnHeight").set_value(int(self.__preferences.getValue("Image", "height")))
        self.builder.get_object("spnMargin").set_value(int(self.__preferences.getValue("Image", "margin")))
        self.builder.get_object("chkBilinear").set_active(bool(int(self.__preferences.getValue("Image", "bilinear"))))
        self.builder.get_object("fontButton").set_font_name(self.__preferences.getValue("Image", "font"))
        bgColor = str(self.__preferences.getValue("Image", "backgroundColor")).split(",")
        self.builder.get_object("colorBackground").set_color(gtk.gdk.Color(int(bgColor[0]), int(bgColor[1]), int(bgColor[2]), 1))
        self.builder.get_object("chkTimestamps").set_active(bool(int(self.__preferences.getValue("Image", "timeStamp"))))
        self.builder.get_object("chkLogo").set_active(bool(int(self.__preferences.getValue("Image", "logo"))))
        self.builder.get_object("chkTranslate").set_active(bool(int(self.__preferences.getValue("Image", "translateHeaderText"))))
        self.builder.get_object("spnCaptureNum").set_value(int(self.__preferences.getValue("Capture", "frames")))
        captureSeconds = int(self.__preferences.getValue("Capture", "seconds"))
        captureTime = time.gmtime(datetime.timedelta(seconds= captureSeconds).seconds)
        self.builder.get_object("spnCaptureMin").set_value(int(time.strftime("%M",captureTime)))
        self.builder.get_object("spnCaptureSec").set_value(int(time.strftime("%S",captureTime)))
        if(self.__preferences.getValue("Capture", "type").upper() == "SECONDS"):
            self.builder.get_object("rbCaptureSeconds").set_active(True)
        else :
            self.builder.get_object("rbCaptureNum").set_active(True)

    def on_btDefaults_clicked(self, widget):
        self.__preferences.setDefaults()
        self.window.destroy()
    def on_btOk_clicked(self, widget):
        self.__savePreferences()
        self.__preferences.save()
        self.window.destroy()
    def on_btCancel_clicked(self, widget):
        self.window.destroy()
    def show(self):
        self.__loadPreferences()
        self.window.show_all()