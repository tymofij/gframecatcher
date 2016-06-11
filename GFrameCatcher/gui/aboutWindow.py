#!/usr/bin/python
#
# aboutWindow.py
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

import os
from gettext import gettext as _

import GFrameCatcher.libs.preferences

class AboutWindow(Gtk.Window):
    def __init__(self, parent):
        fileDirectory = os.path.dirname(__file__)
        self.dialog = Gtk.AboutDialog()
        self.dialog.set_name("GFrameCatcher")
        self.dialog.set_version(GFrameCatcher.libs.preferences.version())
        self.dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(os.path.join(fileDirectory , "../icons/gframecatcher128.png")))
        self.dialog.set_comments(_(
            "GFrameCatcher is a program that captures frames from a video file "
            "and save these frames as thumbnails in a single image file or all frames into a folder."))
        #self.dialog.set_authors("Raul E.")
        try:
            self.dialog.set_license(open("/usr/share/common-licenses/GPL-3").read())
        except Exception:
            self.dialog.set_license(_(
                "Release under GNU General Public License Version 3 \n"
                "See http://www.gnu.org/licenses/gpl.html for details."))
        self.dialog.set_copyright("(c) 2008 Raul E.")
        self.dialog.set_website_label("http://developer.berlios.de/projects/gframecatcher")
        self.dialog.set_website("http://developer.berlios.de/projects/gframecatcher")
        self.dialog.set_transient_for(parent)
        self.dialog.set_destroy_with_parent(True)
        self.dialog.connect("response", self.close)

    def show(self):
        self.dialog.show()

    def close(self, widget, response):
        self.dialog.hide()
 