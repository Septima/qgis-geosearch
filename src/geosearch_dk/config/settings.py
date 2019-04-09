# -*- coding: utf-8 -*-
import os
from PyQt5.QtCore import QFileInfo, QObject
from qgis.PyQt import QtCore

from .qgissettingmanager import *
class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, 'Geosearch DK')

        self.baseurl = "http://kortforsyningen.kms.dk/Geosearch?service=GEO&resources={resources}&area={area}&limit={limit}&token={token}&callback={callback}&search="
        self.resources = {
                'adr': {'id':'Adresser', 'title':'Adresser', 'checkbox': 'adrCheckBox'},
                'ste': {'id':'Stednavne_v2', 'titel':'Stednavne', 'checkbox': 'steCheckBox'},
                'pos': {'id':'Postdistrikter', 'titel':'Postdistrikter', 'checkbox':'posCheckBox'},
                'mat': {'id':'Matrikelnumre', 'titel':'Matrikelnumre', 'checkbox': 'matCheckBox'},
                'kom': {'id':'Kommuner', 'titel':'Kommuner', 'checkbox': 'komCheckBox'},
                'ops': {'id':'Opstillingskredse', 'titel':'Opstillingskredse', 'checkbox': 'opsCheckBox'},
                'pol': {'id':'Politikredse', 'titel':'Politikredse', 'checkbox':'polCheckBox' },
                'reg': {'id':'Regioner', 'titel':'Regioner', 'checkbox':'regCheckBox'}
                }

        self.add_setting(String('token', Scope.Global, '787484d3a8dfee7562ffd6eff1d6e0ee'))
        self.add_setting(String('kommunefilter', Scope.Global, ''))
        self.add_setting(String('resourcesfilter', Scope.Global, ",".join([v['id'] for k,v in self.resources.items()])))

    def emit_updated(self):
        self.settings_updated.emit()

    

