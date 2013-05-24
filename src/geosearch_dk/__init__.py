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

def name():
    return "Geosearch DK"


def description():
    return "Zoom to named places in Denmark. Uses Kortforsyningen. Developed by Septima."


def version():
    return "Version 0.1.19"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.0"

def author():
    return "Asger Petersen, Septima"

def email():
    return "asger@septima.dk"

def classFactory(iface):
    from septimageosearch import SeptimaGeoSearch
    return SeptimaGeoSearch(iface)
