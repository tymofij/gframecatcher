#!/usr/bin/python
#
# progressWindow.py
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

from gettext import gettext as _

class ProgressWindow(Gtk.Window):
    dialog = None

    def __init__(self , parent):
        self.dialog = Gtk.Dialog("Progress", parent, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
        )
        self.dialog.connect("response", self.__onResponse)
        box = self.dialog.get_child()
        widget = Gtk.ProgressBar()
        box.pack_start(widget, False, False, 0)
        self.dialog.set_data("progress", widget)
        widget.set_text(_("Generating...."))
        widget.grab_add()
    
    def __onResponse(self, widget, response):
        self.close()
    
    def setProgress(self, progress):
        progressBar = self.dialog.get_data("progress")
        progressBar.set_fraction(progress / 100)
    
    def show(self):
        self.dialog.show_all()
    
    def close(self):
        self.dialog.destroy()
