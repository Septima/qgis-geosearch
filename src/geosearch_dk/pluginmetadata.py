# -*- coding: utf-8 -*-
"""
#-------------------------------------------------------------------------------
Name:        pluginmetadata
Purpose:     Convenience class for getting plugin metadata in QGIS
Date                 : 24-05-2013
copyright            : (C) 2013 by Septima
author               : asger@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import configparser
import codecs
import os

metadata = None

def plugin_metadata():
    global metadata
    if metadata is None:
        config = configparser.ConfigParser()
        config.readfp(codecs.open( os.path.dirname( __file__ ).replace("\\", "/") + '/metadata.txt', 'r', 'utf8'))
        metadata = dict( config.items('general') )
    return metadata

metadata = plugin_metadata()

def main():
    # fix_print_with_import
    print(plugin_metadata())

if __name__ == '__main__':
    main()