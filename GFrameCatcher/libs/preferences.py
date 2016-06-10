#!/usr/bin/python
#
# preferences.py
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

import os
import tempfile
import locale
from ConfigParser import *

class Preferences :
    __preferencesFile = None
    __configParser = None
    __programName = "gframecatcher"
    __version = "1.4"
    __KeyValue = None
    __locale = None
    __localePath = None
    def __init__(self):
        self.__KeyValue = {
        "Window|width" : "400",
        "Window|height" : "300",
        "Window|zoomFit" : "0",
        "Image|bilinear" : "1" ,
        "Image|columns" : "6" ,
        "Image|width" : "148" ,
        "Image|height" : "111" ,
        "Image|margin" : "10" ,
        "Image|bilinear" : "1" ,
        "Image|font" : "Sans 12" ,
        "Image|backgroundColor" : "58082,59110,61166" ,
        "Image|timeStamp" : "1" ,
        "Image|logo" : "1" ,
        "Image|translateHeaderText" : "0" ,
        "Capture|seconds" : "59" ,
        "Capture|frames" : "24" ,
        "Capture|type" : "SECONDS" }
        
        self.__getPreferencesFile()
    def __readForFile(self):
         self.__configParser = ConfigParser()
         self.__configParser.read(self.__getPreferencesFile())
    def setDefaults(self):
         self.__configParser = ConfigParser()
         keys = self.__KeyValue.keys()
         keys.sort()
         lastSection = ""
         for index in range(0, len(keys)):
             section = keys[index].split("|")
             if(section[0] != lastSection):
                 lastSection = section[0]
                 self.__configParser.add_section(section[0])
             self.__configParser.set(section[0], section[1], self.__KeyValue[keys[index]])
    def __getPreferencesFile(self):
       if(self.__preferencesFile == None):
         homePath = os.path.expanduser("~")
         homePath = os.path.join(homePath , "." + self.__programName)
         if(os.path.exists(homePath) == False):
            os.makedirs(homePath)
         homePath = os.path.join(homePath ,  "config")
         if(os.path.exists(homePath) == False):
            myFile = open(homePath,"w")
            myFile.close()
         self.__preferencesFile = homePath
         if(os.path.getsize(homePath) == 0):
            self.setDefaults()
         else:
            self.__readForFile()
       return self.__preferencesFile
    def __getLocalePath(self):
        if(self.__localePath == None):
            basePath = os.path.abspath(__file__)
            prefix = os.path.dirname(os.path.dirname(basePath))
            self.__localePath = os.path.join(prefix,"share","locale")
            if not os.path.isdir(self.__localePath):
                self.__localePath = os.path.join(prefix , "mo")
        return self.__localePath
    def __getLocale(self):
        if(self.__locale == None):
            myLocale = locale.getdefaultlocale()[0]
            if (myLocale != None):
                self.__locale = [myLocale]
            language = os.environ.get('LANGUAGE', None)
            if (language != None):
                self.__locale += language.split(":")
        return self.__locale
    def __getProgramName(self):
        return self.__programName
    def __getVersion(self):
        return self.__version
    def setValue(self,section,key,value):
       self.__configParser.set(section,key,value)
    def getValue(self,section,key):
        try:
            return self.__configParser.get(section,key)
        except NoOptionError:
            myKey = section + "|" + key
            return self.__KeyValue[myKey]
    def save(self):
       myFile = open(self.__getPreferencesFile(),"w")
       self.__configParser.write(myFile)
       myFile.close()

    Version = property(__getVersion)
    ProgramName = property(__getProgramName)
    Locale = property(__getLocale)
    LocalePath = property(__getLocalePath)
    
def version():
    myPreferences = Preferences()
    return myPreferences.Version
def tempFileName(videoFileName):
    temp = tempfile.NamedTemporaryFile(prefix= videoFileName, suffix= ".png")
    nameFile = temp.name
    temp.close()
    return nameFile