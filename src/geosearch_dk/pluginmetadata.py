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
import configparser
import codecs
import os

metadata = None

def plugin_metadata():
    global metadata
    if metadata is None:
        config = configparser.ConfigParser()
        with codecs.open( os.path.dirname( __file__ ).replace("\\", "/") + '/metadata.txt', 'r', 'utf8') as fp:
            config.read_file(fp)
        metadata = dict( config.items('general') )
    return metadata

metadata = plugin_metadata()

def main():
    metadata_to_print = plugin_metadata() 
    print(metadata_to_print)

if __name__ == '__main__':
    main()