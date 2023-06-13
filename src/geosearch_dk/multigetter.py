import json

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

class MultiGetter(QObject):

    def __init__(self, networkManager):
        QObject.__init__(self)
        self.networkManager = networkManager
        self.replies = {}
        self.results = {}

    def get (self, urls, callback_fn):
        for key, url in urls.items():
            request = QNetworkRequest( QUrl(url) )
            networkReply = self.networkManager.get(request) 
            self.replies[key] = networkReply
            self.results[key] = None
            func = MultiGetter.bind_instance_method(self, "get_data", key, callback_fn)
            networkReply.finished.connect( func )

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
        if not error:
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
            callback_fn(self.results)