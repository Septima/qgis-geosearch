# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geosearch_dk
Description          : Search suggestions in QGIS using GST's geosearch service
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

from . import pluginmetadata

def name():
    return pluginmetadata.metadata['name']


def description():
    return pluginmetadata.metadata['description']


def version():
    return "Version " + pluginmetadata.metadata['version']


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return pluginmetadata.metadata['qgisMinimumVersion']

def author():
    return pluginmetadata.metadata['author']

def email():
    return pluginmetadata.metadata['email']

def classFactory(iface):
    from .septimageosearch import SeptimaGeoSearch
    return SeptimaGeoSearch(iface)
