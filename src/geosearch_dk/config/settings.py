# -*- coding: utf-8 -*-
import os

from qgis.PyQt import QtCore

from .qgissettingmanager import *

DEFAULT_DATAFORSYNING_TOKEN = "0350b5341749c0970454474881173412"

class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, 'Geosearch DK')
        #self.baseurl = "https://api.dataforsyningen.dk/rest/gsearch/v1.0/{resource}?token={token}&q={query}&limit={limit}&filter={filter}"
        self.baseurl = "https://api.dataforsyningen.dk/rest/gsearch/v1.0/{resource}?token={token}&q={query}&limit={limit}"


        # The order here is the order results are displayed in
        self.resources = {
                'hus': {'id':'husnummer', 'titel':'Husnumre'},
                'ste': {'id':'stednavn', 'titel':'Stednavne'},
                'pos': {'id':'postnummer', 'titel':'Postdistrikter'},
                'mat': {'id':'matrikel', 'titel':'Matrikelnumre'},
                'kom': {'id':'kommune', 'titel':'Kommuner'},
                'ops': {'id':'opstillingskreds', 'titel':'Opstillingskredse'},
                'pol': {'id':'politikreds', 'titel':'Politikredse'},
                'reg': {'id':'region', 'titel':'Regioner'}
                }

        self.add_setting(String('token', Scope.Global, DEFAULT_DATAFORSYNING_TOKEN))
        self.add_setting(String('kommunefilter', Scope.Global, ''))

        self._migratesettings()

        for k, dict in self.resources.items():
            self.add_setting(Bool(f"search_{k}",Scope.Global, True))

    def selected_resources(self):
        selected_resources = {}
        for key, dict in self.resources.items():
            if self.value(f"search_{key}"):
                selected_resources[key] = self.resources[key]
        return selected_resources

    def emit_updated(self):
        self.settings_updated.emit()

    def _migratesettings(self):
        # Migrerer existerende settings

        # Gammelt, nu nedlagt dataforsyningstoken erstattes. Brugerens evt eget token skal ikke røres.
        old_default_token = "787484d3a8dfee7562ffd6eff1d6e0ee"
        if self.value("token") == old_default_token:
            self.set_value("token", DEFAULT_DATAFORSYNING_TOKEN)

    

