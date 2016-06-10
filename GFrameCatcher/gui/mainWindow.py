#!/usr/bin/python
#
# mainWindow.py
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
import gobject
import pango
import gettext
from gettext import gettext as _
import os
import sys
import mimetypes
import urlparse
import aboutWindow
import progressWindow
import preferencesWindow
import GFrameCatcher.media.mediaLibrary
import GFrameCatcher.libs.frameImage
import GFrameCatcher.libs.preferences

class MainWindow :
    fileName = None
    mediaInfo = None
    preferences = None
    __selectedPixbuf = None
    __size = (0, 0)
    __scrolledWindowSize = (0, 0)
    __isMaximized = False
    __tempFilename = None
    def __init__(self):
        fileDirectory = os.path.dirname(__file__)
        self.preferences = GFrameCatcher.libs.preferences.Preferences()
        gobject.set_application_name(self.preferences.ProgramName)
        gettext.bindtextdomain(self.preferences.ProgramName, self.preferences.LocalePath)
        gettext.textdomain(self.preferences.ProgramName)
        gettext.install(self.preferences.ProgramName, localedir= self.preferences.LocalePath,unicode= True)
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(fileDirectory , "ui/mainWindow.ui"))
        self.builder.set_translation_domain(self.preferences.ProgramName)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file(os.path.join(fileDirectory , "../icons/gframecatcher16.png")))
        self.window.set_default_size(int(self.preferences.getValue("Window", "width")), int(self.preferences.getValue("Window", "height")))
        self.builder.get_object("toolZoomFitButton").set_active(bool(int(self.preferences.getValue("Window", "zoomFit"))))
        self.window.show_all()
        self.MediaInfo = GFrameCatcher.media.mediaLibrary.MediaInfo()
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str)
        self.builder.get_object("frameView").set_from_pixbuf(None)
        videoDrop = [("text/uri-list" , 0 , 82 )]
        self.builder.get_object("frameIconView").set_model(self.model)
        self.builder.get_object("frameIconView").drag_dest_set(
        gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP, videoDrop , gtk.gdk.ACTION_COPY)
        self.__imageDrag = [("text/uri-list", 0, 81), ("image/png", 0, 82)]
        self.builder.get_object("viewPort").drag_source_set(gtk.gdk.BUTTON1_MASK, self.__imageDrag, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
        self.builder.get_object("viewPort").drag_dest_unset()
        self.window.connect("configure-event", self.on_configure_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        self.window.connect("destroy", self.on_imageQuit_activate)
    def show(self):
        gtk.main()
    def on_frameIconView_drag_data_received(self, widget, dragContext, x, y, selectionData, info, time):
        filesUri = selectionData.data.split()
        if(filesUri[0].find("file:") < 0):
            self.__showErrorDialog(_("Drop not allowed"))
        else:
            fileName = urlparse.urlparse(filesUri[0]).path
            mimeType = mimetypes.guess_type(fileName)
            if(mimeType[0] == None):
                return
            if(mimeType[0].find("video/") < 0 ):
                errorMessage = _("mimetype %s not supported") % mimeType[0]
                self.__showErrorDialog(errorMessage)
            else:
                self.fileName = fileName
                self.loadThumbnails()
    def on_frameIconView_selection_changed(self, widget):
        selected = widget.get_selected_items()
        if len(selected) == 0:
            return
        index = selected[0][0]        
        self.__selectedPixbuf = self.MediaInfo.images[index][0]
        self.__setFrameViewPixbuf()
    def on_viewPort_drag_begin(self, widget, dragContext):
        self.__tempFilename = GFrameCatcher.libs.preferences.tempFileName(self.MediaInfo.getFilename() + _("Frame"))
    def on_viewPort_drag_end(self, widget, dragContext):
        if(os.path.exists(self.__tempFilename) == True):
            os.remove(self.__tempFilename)
        self.__tempFilename = None
    def on_viewPort_drag_data_get(self, widget, dragContext, selectionData, target, time):
        try:
            if(self.__selectedPixbuf == None):
                raise ValueError
        except ValueError:
            return False

        if(target == self.__imageDrag[0][2]):
            if(self.__tempFilename == None):
                return False
            self.__selectedPixbuf.save(self.__tempFilename, "png")
            fileUri = "file://" + self.__tempFilename
            selectionData.set_uris([(fileUri)])
        elif(target == self.__imageDrag[1][2]):
            selectionData.set_pixbuf(self.__selectedPixbuf)
            selectionData.targets_include_image(True)

    def on_viewPort_size_allocate (self, widget, allocation):
       if(self.__scrolledWindowSize[0] != allocation.width or self.__scrolledWindowSize[1] != allocation.height):
           self.__scrolledWindowSize = allocation.width, allocation.height
           self.__setFrameViewPixbuf()
    def on_imageOpen_activate(self, widget):
        fileChooser = gtk.FileChooserDialog(_("Open File..."),
        self.window, gtk.FILE_CHOOSER_ACTION_OPEN, 
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        fileChooser.set_select_multiple(False)
        fileChooser.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name(_("Video Files"))
        filter.add_mime_type("video/x-msvideo")
        filter.add_mime_type("video/x-ms-asf")
        filter.add_mime_type("video/x-ms-wmv")
        filter.add_mime_type("video/x-matroska")
        filter.add_mime_type("video/x-dv")
        filter.add_mime_type("video/quicktime")
        filter.add_mime_type("video/ogg")
        filter.add_mime_type("video/mp4")
        filter.add_mime_type("video/mpeg")
        filter.add_mime_type("video/*")
        fileChooser.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name(_("All Files"))
        filter.add_pattern("*")
        fileChooser.add_filter(filter)
        
        fileChooserResponse = fileChooser.run()
        
        if fileChooserResponse == gtk.RESPONSE_OK:
             self.fileName =  fileChooser.get_filename()
             fileChooser.destroy()
             self.loadThumbnails()
        else:
             fileChooser.destroy()
    def on_mediaLibrary_progress(self, mediaInfo, progress, widget):
        widget.setProgress(progress)
    def on_mediaLibrary_error(self, mediaInfo, error, description, widget):
        self.MediaInfo.cancel()
        self.finishLoad()
        widget.close()
        self.__showErrorDialog(description, error)
    def on_mediaLibrary_completed(self, mediaInfo, widget):
        self.MediaInfo.cancel()
        self.finishLoad()
        widget.close()
    def on_progressWindow_cancel(self, widget):
        self.MediaInfo.cancel()
        self.finishLoad()
        widget = None
    def on_imageAbout_activate(self, widget):
        myAboutWindow = aboutWindow.AboutWindow(self.window)
        myAboutWindow.show()
    def on_imagePreferences_activate(self, widget):
        myPreferencesWindow = preferencesWindow.PreferencesWindow(self.window,self.preferences)
        myPreferencesWindow.show()
    def on_window_state_event(self, window, event):
        if(event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED):
            self.__isMaximized = True
        else:
            self.__isMaximized = False
    def on_configure_event(self, window, event):
        self.__size = window.get_size()
    def on_imageQuit_activate(self, widget):
        if(self.__isMaximized == False) :
            self.preferences.setValue("Window", "width", str(self.__size[0]))
            self.preferences.setValue("Window", "height",str(self.__size[1]))
        self.preferences.setValue("Window", "zoomFit", str(int(self.builder.get_object("toolZoomFitButton").get_active())))
        self.preferences.save()
        #self.window.destroy()
        gtk.main_quit()
    def on_menuSaveAllItem_activate(self, widget):
        if(self.MediaInfo == None or self.MediaInfo.fileName == None or
        self.MediaInfo.fileName == ""):
            self.__showErrorDialog(_("There is no video open"))
            return

        fileChooser = gtk.FileChooserDialog(_("Select Directory..."),
        self.window, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
        gtk.STOCK_SAVE,   gtk.RESPONSE_OK))

        fileChooser.set_select_multiple(False)
        fileChooser.set_default_response(gtk.RESPONSE_OK)

        fileChooser.set_filename(self.MediaInfo.fileName)
        fileChooserResponse = fileChooser.run()

        if fileChooserResponse == gtk.RESPONSE_OK:
             outputDirectory =  fileChooser.get_current_folder()
             fileChooser.destroy()
             frameImage = GFrameCatcher.libs.frameImage.FrameImage(self.MediaInfo)
             self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
             try :
                 frameImage.saveAllTo(outputDirectory)
             except Exception , exc:
                 self.__showErrorDialog(exc)
             self.window.window.set_cursor(None)
        else:
             fileChooser.destroy()
    def on_toolReloadButton_clicked(self, widget):
        if(self.fileName == None):
            self.__showErrorDialog(_("There is no video open"))
            return
        if(self.MediaInfo == None):
            return
        self.loadThumbnails()
    def on_menuSaveFileItem_activate(self, widget):
        if(self.MediaInfo == None or self.MediaInfo.fileName == None or self.MediaInfo.fileName == ""):
            self.__showErrorDialog(_("There is no video open"))
            return
        outputFileName = self.__saveFileDialog(self.MediaInfo.fileName, self.MediaInfo.getFilename())
        if(outputFileName != None):
            frameImage = GFrameCatcher.libs.frameImage.FrameImage(self.MediaInfo)
            bgColor = str(self.preferences.getValue("Image", "backgroundColor")).split(",")
            frameImage.backgroundColor = int(bgColor[0]), int(bgColor[1]), int(bgColor[2])
            frameImage.size =  int(self.preferences.getValue("Image", "width")) ,  int(self.preferences.getValue("Image", "height"))
            frameImage.margin = int(self.preferences.getValue("Image", "margin"))
            frameImage.columns = int(self.preferences.getValue("Image", "columns"))
            frameImage.showLogo = bool(int(self.preferences.getValue("Image", "logo")))
            frameImage.showTimestamp = bool(int(self.preferences.getValue("Image", "timeStamp")))
            frameImage.translateHeaderText = bool(int(self.preferences.getValue("Image", "translateHeaderText")))
            frameImage.font = pango.FontDescription(self.preferences.getValue("Image", "font"))
            self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            try :
                frameImage.createImage(outputFileName)
            except Exception, exc:
                self.__showErrorDialog(exc)
            self.window.window.set_cursor(None)
    def loadThumbnails(self):
        self.__selectedPixbuf = None
        self.__setFrameViewPixbuf()
        self.model.clear()
        if(self.preferences.getValue("Capture", "type").upper() == "SECONDS"):
            self.MediaInfo.captureType = GFrameCatcher.media.mediaLibrary.CaptureType.SECONDS
            self.MediaInfo.seconds = int(self.preferences.getValue("Capture", "seconds"))
        else :
            self.MediaInfo.captureType = GFrameCatcher.media.mediaLibrary.CaptureType.FRAMES
            self.MediaInfo.frames = int(self.preferences.getValue("Capture", "frames"))

        try:
            myProgressWindow = progressWindow.ProgressWindow(self.window)
            self.MediaInfo.connect("error", self.on_mediaLibrary_error, myProgressWindow)
            self.MediaInfo.connect("progress", self.on_mediaLibrary_progress, myProgressWindow)
            self.MediaInfo.connect("completed", self.on_mediaLibrary_completed, myProgressWindow)
            
            self.MediaInfo.openfile(self.fileName,self.model)
            
            self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
            self.builder.get_object("frameIconView").queue_draw()
            
            myProgressWindow.dialog.connect("destroy",self.on_progressWindow_cancel)
            myProgressWindow.show()

        except Exception:
            self.__showErrorDialog(sys.exc_value)

    def finishLoad(self):
        self.builder.get_object("frameIconView").queue_resize()
        self.window.window.set_cursor(None)
    def on_toolButtonSave_clicked(self, widget):
        try:
            if(self.__selectedPixbuf == None):
                raise ValueError
        except ValueError:
            self.__showErrorDialog(_("There is no image selected to save"))
            return

        outputFileName = self.__saveFileDialog(self.MediaInfo.fileName, self.MediaInfo.getFilename() + _("Frame"))
        if(outputFileName != None):
            self.__selectedPixbuf.save(outputFileName, "png")
            
    def on_toolButtonCopy_clicked(self, widget):
        try:
            clipBoard = gtk.Clipboard()
            if(self.__selectedPixbuf == None):
                raise ValueError
            clipBoard.set_image(self.__selectedPixbuf)
        except ValueError:
            return
    def on_toolButtonPrint_clicked(self, widget):
        try:
            if(self.__selectedPixbuf == None):
                raise ValueError
        except ValueError:
            self.__showErrorDialog(_("There is no image selected to print"))
            return
        printOperation = gtk.PrintOperation()
        printOperation.set_default_page_setup()
        printOperation.set_n_pages(1)
        printOperation.set_unit(gtk.UNIT_PIXEL)
        printOperation.connect("draw_page", self.__printPixBuf)
        printOperation.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, self.window)
    def on_toolZoomFitButton_toggled(self, widget):
        self.__setFrameViewPixbuf()
    def __printPixBuf(self, operation, context, pageNum):
        cairoContext = context.get_cairo_context()
        width = context.get_width()
        pixBuf = self.__selectedPixbuf
        cairoContext.set_source_pixbuf(pixBuf, 0, 0)
        cairoContext.rectangle(0 , 0, width , pixBuf.get_height())
        cairoContext.fill()
        cairoContext.restore()
    def __setFrameViewPixbuf(self):
        gtk.gdk.threads_enter()
        if(self.__selectedPixbuf != None):
            if(self.builder.get_object("toolZoomFitButton").get_active() == True):
                if(self.__scrolledWindowSize[0] < self.__selectedPixbuf.get_width() or self.__scrolledWindowSize[1] < self.__selectedPixbuf.get_height()):
                    imageWidth = self.__scrolledWindowSize[0]
                    if(self.__scrolledWindowSize[0] > self.__selectedPixbuf.get_width()):
                        imageWidth = self.__selectedPixbuf.get_width()

                    imageHeight = self.__scrolledWindowSize[1]
                    if(self.__scrolledWindowSize[1] > self.__selectedPixbuf.get_height()):
                        imageHeight = self.__selectedPixbuf.get_height()

                    fitPixbuf = self.__selectedPixbuf.scale_simple(imageWidth, imageHeight, gtk.gdk.INTERP_NEAREST)
                    while gtk.events_pending():
                        gtk.main_iteration()
                        
                    self.builder.get_object("frameView").set_from_pixbuf(fitPixbuf)
                else :
                    self.builder.get_object("frameView").set_from_pixbuf(self.__selectedPixbuf)
            else:
                self.builder.get_object("frameView").set_from_pixbuf(self.__selectedPixbuf)
        else:
            self.builder.get_object("frameView").clear()
        gtk.gdk.threads_leave()
    def __saveFileDialog(self, FileName, name):
        outputFileName = None
        fileChooser = gtk.FileChooserDialog(_("Save File..."),
        self.window, gtk.FILE_CHOOSER_ACTION_SAVE,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
        gtk.STOCK_SAVE,   gtk.RESPONSE_OK))

        fileChooser.set_select_multiple(False)
        fileChooser.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("Image Files"))
        filter.add_mime_type("image/png")
        fileChooser.add_filter(filter)

        fileChooser.set_filename(FileName + ".png")
        fileChooser.set_current_name(name + ".png")
        fileChooserResponse = fileChooser.run()

        if fileChooserResponse == gtk.RESPONSE_OK:
             outputFileName =  fileChooser.get_filename()
             fileChooser.destroy()
        else:
             fileChooser.destroy()
        return outputFileName
    def __showErrorDialog(self, exc, headerText= None):
        ErrorDialog = gtk.MessageDialog(self.window, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, None)
        if(headerText == None):
            headerText= _("Error")
        ErrorDialog.set_markup("<span weight=\"bold\" size=\"larger\">" + str(headerText) + "</span>")
        ErrorDialog.format_secondary_text(str(exc))
        ErrorDialog.set_destroy_with_parent(True)
        if (ErrorDialog.run()) :
            ErrorDialog.destroy()
