# -*- coding: utf-8 -*-
import os
from PyQt5.QtCore import QFileInfo, QObject
from qgis.PyQt import QtCore

from .qgissettingmanager import *

DEFAULT_DATAFORSYNING_TOKEN = "0350b5341749c0970454474881173412"

class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, 'Geosearch DK')

        self.baseurl = "https://api.dataforsyningen.dk/Geosearch?service=GEO&resources={resources}&area={area}&limit={limit}&token={token}&callback={callback}&search="

        # The order here is the order results are displayed in
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

        self.add_setting(String('token', Scope.Global, DEFAULT_DATAFORSYNING_TOKEN))
        self.add_setting(String('kommunefilter', Scope.Global, ''))

        self._migratesettings()

        for k, dict in self.resources.items():
            self.add_setting(Bool(f"search_{k}",Scope.Global, True))

    def resourcesfilter(self):
        resultlist = []
        for k, dict in self.resources.items():
            if self.value(f"search_{k}"):
                resultlist.append(dict["id"])
        return resultlist

    def emit_updated(self):
        self.settings_updated.emit()

    def _migratesettings(self):
        # Migrerer existerende settings

        # Gammelt, nu nedlagt dataforsyningstoken erstattes. Brugerens evt eget token skal ikke røres.
        old_default_token = "787484d3a8dfee7562ffd6eff1d6e0ee"
        if self.value("token") == old_default_token:
            self.set_value("token", DEFAULT_DATAFORSYNING_TOKEN)

    

