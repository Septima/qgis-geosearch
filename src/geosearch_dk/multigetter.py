# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geosearch_dk
Description          : Search suggestions in QGIS using SDFI's Gsearch service
Date                 : 13-06-2023
copyright            : (C) 2023 by Septima
author               : klavs@septima.dk
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
import json
import uuid

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsApplication, QgsMessageLog, QgsNetworkContentFetcher, Qgis, QgsNetworkAccessManager

class MultiGetter(QObject):

    def __init__(self, networkManager):
        QObject.__init__(self)
        self.networkManager = networkManager
        self.replies = {}
        self.results = {}

    def get (self, urls, callback_fn):
        self.get_id = str(uuid.uuid4())
        for key, url in urls.items():
            request = QNetworkRequest( QUrl(url) )
            networkReply = self.networkManager.get(request) 
            self.replies[key] = networkReply
            self.results[key] = None
            func = MultiGetter.bind_instance_method(self, "get_data", key, callback_fn)
            networkReply.finished.connect( func )
        return self.get_id

    def bind(fn, *args):
        def inner(*a):
            return fn(*args, *a)
        return inner        

    def bind_instance_method(obj, method_name, *args):
        method = getattr(obj, method_name)
        return MultiGetter.bind(method, *args)

    def get_data(self, key, callback_fn):
        networkReply = self.replies[key]
        result = {}

        del self.replies[key]
        networkReply.deleteLater()

        error = networkReply.error()
        if error == QNetworkReply.NetworkError.NoError:
            content = networkReply.readAll()
            content = str(content, 'utf-8')

            try:
                result["data"] = json.loads(content)
                result["ok"] = 1
            except Exception as e:
                result["ok"] = None
                result["error"] = e
                result["response"] = str(e)
        else:
            response_content = networkReply.readAll()
            response_content = str(response_content, 'utf-8')
            result["ok"] = None
            result["error"] = error
            result["response"] = response_content

        self.results[key] = result

        finished = True
        for key, result in self.results.items():
            finished = (result != None)
            if not finished:
                break
            
        if finished:
            callback_fn(self.get_id, self.results)