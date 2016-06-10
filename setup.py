#!/usr/bin/python
#
# setup.py
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA>.

import os
from os import path
import re

import GFrameCatcher.libs.preferences
from distutils.core import setup

data_files= [("share/applications/", ["GFrameCatcher/icons/gframecatcher.desktop"]),
            ("share/pixmaps/", ["GFrameCatcher/icons/gframecatcher.svg"])]

#Take a look at OggConvert : http://oggconvert.tristanb.net
for name in os.listdir("po"):
	pattern = re.match(r'(.+)\.po$', name)
	if pattern != None:
		lang = pattern.group(1)
		out_dir = "GFrameCatcher/mo/%s/LC_MESSAGES" % lang
		out_name = path.join(out_dir, "gframecatcher.mo")
		install_dir = "share/locale/%s/LC_MESSAGES/" % lang
		os.makedirs(out_dir)
  		os.system("msgfmt -o %s po/%s" % (out_name, name))
		data_files.append((install_dir, [out_name]))

setup(name= "gframecatcher",
      version= GFrameCatcher.libs.preferences.version(),
      author= "Raul E.",
      description= "GFrameCatcher is a program that captures frames from a video file and save these frames as thumbnails in a single image file or all frames into a folder.",
      long_description = "GFrameCatcher is a program that captures frames from a video file and save these frames as thumbnails in a single image file or all frames into a folder.",
      url = "http://developer.berlios.de/projects/gframecatcher",
      license= "GPL",
      platforms= "Any",
      classifiers = ["Topic :: Multimedia :: Video"],
      packages= ["GFrameCatcher","GFrameCatcher.gui","GFrameCatcher.libs","GFrameCatcher.media"],
      package_dir = {"GFrameCatcher": "GFrameCatcher"},
      package_data= {"GFrameCatcher.gui": ["ui/*"] , "GFrameCatcher": ["icons/*.png"]},
      scripts= ["gframecatcher"],
      data_files= data_files
     )
