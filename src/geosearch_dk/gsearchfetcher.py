import re
import json

from qgis.PyQt import QtCore
from qgis.core import QgsApplication, QgsMessageLog, QgsNetworkContentFetcher, Qgis, QgsNetworkAccessManager
from qgis.PyQt.QtCore import QObject, QUrl

from .multigetter import MultiGetter

class GSearchFetcher(QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, settings):
        QObject.__init__(self)
        self.settings = settings
        self.networkManager = QgsNetworkAccessManager.instance()
        self.result = None
        self.last_get_id = None
    
    def fetch (self, term):
        urls = self.geturls(term)
        multigetter = MultiGetter(self.networkManager)
        self.last_get_id = multigetter.get(urls, self.handleMultiGetterResult)
        #multigetter.finished.connect(self.handleMultiGetterResult)


    def geturls(self, searchterm):
        urls = {}
        limit = 40
        #https://api.dataforsyningen.dk/rest/gsearch/v1.0/kommune?token=fd44f26ab5701c01ca9f570e507fe9ab&q=kom&limit=10
        selected_resources = self.settings.selected_resources()
        split = searchterm.split(':')
        if len(split)>1:
            first3letters_lowerCase = split[0][0:3].lower()
            if first3letters_lowerCase in self.settings.resources:
                selected_resources[first3letters_lowerCase] = self.settings.resources[first3letters_lowerCase]
                searchterm = split[1].lstrip()
        if not searchterm:
            return None
        if len(selected_resources) > 0:
            limit = limit // len(selected_resources)
            kommunekoder = re.findall(r'\d+', self.settings.value('kommunefilter'))
            filter = '%20or%20'.join(['kommunekode%20like%20%27%25' + str(k) + '%25%27' for k in kommunekoder])
            for key, resource in selected_resources.items():
                url = self.settings.baseurl.format(
                    resource=resource["id"],
                    limit=limit,
                    token = self.settings.value('token'),
                    query = searchterm
                )
                if len(kommunekoder)>0:
                    url = url + "&filter=" + filter
                urls[key] = url
            return urls
        else:
            return None

    def get_result(self):
        return self.result

    def handleMultiGetterResult(self, get_id, results):
        if self.last_get_id == get_id:
            self.result = []
            for key, result in results.items():
                resource = self.settings.resources[key]
                if result["ok"]:
                    rows = result["data"]
                    for row in rows:
                        row["key"] = key
                        row["status"] = "ok"
                        row["resource"] = resource
                    self.result.extend(rows)
                else:
                    row = {}
                    row["key"] = key
                    row["status"] = "error"
                    row["resource"] = resource
                    row["response"] = result["response"]
                    self.result.extend([row])
                    QgsApplication.messageLog().logMessage('Fejl i kald til GSearch: [' + str(result["error"]) + '] ' + result["response"], __package__)
            self.finished.emit()


