#!/usr/bin/python
#
# mediaLibrary.py
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

#
# This library is based in whaaw thumbnailer source code : http://home.gna.org/whaawmp
# Missing plugin install codec functionally is inspired from elisa play_bin_engine : http://elisa.fluendo.com
#

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')

from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject
from gi.repository import GdkPixbuf, Gdk
from gi.repository import Gst as gst
gst.init(None)
from gi.repository import GstPbutils as pbutils

gobject.threads_init()

from gettext import gettext as _
import time
import datetime
import os

class CaptureType :
    SECONDS = 0
    FRAMES = 1

class MediaInfo(gobject.GObject) :
    length = 0
    width = 0
    height = 0
    codec = ""
    fileName = ""
    images = None
    errors = None
    model = None
    player = None
    captureType = CaptureType.SECONDS
    seconds = 0
    frames = 0
    __isEndOfStream = False
    __duration = 0
    __gsignals__ =  { 
            "completed": (
                gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
            "progress": (
                gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [
                gobject.TYPE_FLOAT]),
            "error": (
                gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [
                gobject.TYPE_STRING, gobject.TYPE_STRING])
            }
    def __init__(self):
       gobject.GObject.__init__(self)
       self.size = (128, 128)
       
    def openfile(self, filename ,aModel):
       self.images = list()
       self.errors = list()
       self.fileName = filename
       self.codec = ""
       if (self.player != None):
           self.player.set_state(gst.STATE_NULL)
           
       self.__isEndOfStream = False
       self.player = gst.element_factory_make("playbin", "player")
       videoBin = gst.Bin("video")
       videoFilter = gst.element_factory_make("capsfilter", "videofilter")
       videoBin.add(videoFilter)
       videoFilter.set_property("caps", gst.Caps("video/x-raw-rgb, depth=24, bpp=24"))
       ghostPad = gst.GhostPad("sink", videoFilter.get_pad("sink"))
       videoBin.add_pad(ghostPad)
       videoSink = gst.element_factory_make("fakesink", "videosink")
       videoBin.add(videoSink)
       pad = videoSink.get_pad("sink")
       pad.add_buffer_probe(self.__onBufferProbe)
       gst.element_link_many(videoFilter, videoSink)
       self.player.set_property("video-sink", videoBin)
       
       self.bus = self.player.get_bus()
       self.bus.add_signal_watch()
       self.watchID = self.bus.connect("message", self.__onMessage)
       self.player.set_property("uri", "file://" + filename)
       self.player.set_state(gst.STATE_PAUSED)
       self.model = aModel
    def __seek(self, seek_pos):
       event = self.player.seek(1.0, gst.FORMAT_TIME,
       gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
       gst.SEEK_TYPE_SET, seek_pos,
       gst.SEEK_TYPE_NONE, 0)
       print seek_pos
    def __onBufferProbe(self, pad, buffer):
       if (self.player != None and self.__isEndOfStream == False):
           caps = buffer.caps
           if (caps == None):
               print _("Stream returned no caps, exiting")
               sys.exit(6)
           filters = caps[0]
           self.width = filters["width"]
           self.height = filters["height"]
           pixbuf = gtk.gdk.pixbuf_new_from_data(buffer.data, gtk.gdk.COLORSPACE_RGB, False, 8, self.width, self.height, self.width * 3)
           self.__duration =  self.player.query_duration(gst.FORMAT_TIME)[0]/gst.SECOND
           position = self.player.query_position(gst.FORMAT_TIME)[0]/gst.SECOND
           frame = pixbuf,time.strftime("%H:%M:%S", time.gmtime(datetime.timedelta(seconds= position).seconds))
           self.images.append(frame)
           scaled = pixbuf.scale_simple(self.size[0], self.size[1], gtk.gdk.INTERP_NEAREST)
           self.model.append([scaled, frame[1]])

           if(self.captureType == CaptureType.SECONDS) :
               if(position + self.seconds) <= self.__duration:
                   self.__seek((position + self.seconds) * gst.SECOND)
               else:
                   self.player.send_event(gst.event_new_eos())
                   self.__isEndOfStream = True
           else :
               if(len(self.images) < self.frames):
                   self.__seek((position + (self.__duration / (self.frames - 1))) * gst.SECOND)
               else:
                   self.player.send_event(gst.event_new_eos())
                   self.__isEndOfStream = True
           percentage = float(100 * position) / float(self.__duration)
           self.emit("progress", percentage)
    def __onMessage(self, bus, message):
        if (message.type == gst.MESSAGE_ELEMENT):
            if(message.structure.get_name().startswith("missing-")):
                self.emit("completed")
                self.__getMissingElement(message)
        elif (message.type == gst.MESSAGE_ERROR):
            print message.parse_error()[0]
        elif (message.type == gst.MESSAGE_TAG):
            if(message.structure.get_name() == "video-codec"):
                self.codec = message.structure["video-codec"]
            else:
                tagList = message.parse_tag()
                keys = tagList.keys()
                try:
                    if(keys.index("video-codec") > -1 and self.codec == ""):
                        self.codec = tagList["video-codec"]
                except(ValueError):
                    None
        elif (message.type == gst.MESSAGE_ASYNC_DONE):
            self.emit("completed")
        elif (message.type == gst.MESSAGE_EOS):
            self.emit("completed")
    def __getMissingElement(self, message, window_id = 0):
        if gst.pygst_version < (0, 10, 10):
            print _("This version of gstreamer can't handle missing elements")
            return
        self.errors.append(str(message.structure["type"]))
        self.errors.append(str(message.structure["detail"]))
        self.errors.append(str(message.structure["name"]))
        detail = pbutils.missing_plugin_message_get_installer_detail(message)
        context = pbutils.InstallPluginsContext()
        
        if window_id:
            context.set_x_id(window_id)
            
        msg = pbutils.install_plugins_async([detail], context,self.__pbutils_plugin_installed_cb)

    def __pbutils_plugin_installed_cb(self, result):
        if result == pbutils.INSTALL_PLUGINS_SUCCESS:
            gst.update_registry()
        else:
            self.emit("error", result.value_name, "\n".join(self.errors))
    def __getGStreamerLibraryVersion(self):
        return ".".join([str(integer) for integer in gst.pygst_version])
    def getDuration(self):
        return time.strftime("%H:%M:%S",time.gmtime(datetime.timedelta(seconds= self.__duration).seconds))
    def getDurationSeconds(self):
        return self.__duration
    def getFilename(self):
        return os.path.basename(self.fileName)
    def cancel(self):
        if (self.player != None):
           self.player.set_state(gst.STATE_NULL)
        self.player = None
        self.bus = None
        self.watchID = None

    GStreamerLibraryVersion = property(__getGStreamerLibraryVersion)
gobject.type_register(MediaInfo)
