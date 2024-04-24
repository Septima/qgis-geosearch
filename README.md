Geosearch DK
==============

QGIS-plugin der tilføjer en søgeboks der anvender offentlige data, som tillader brugeren lynhurtigt at zoome til navngivne steder i Danmark - f.eks. adresser, stednavne, kommuner.

Pluginet er udviklet af [Septima](http://www.septima.dk) og stilles frit og gratis til rådighed for QGIS-brugere under GNU General Public License v3.0, se nærmere i afsnittet [Ophavsret og videredistribution](#ophavsret-og-videredistribution).

OBS - Er dit plugin stoppet med at virke efter 31. august 2023?
--------------
[Styrelsen for Dataforsyning og Infrastruktur (SDFI)](https://sdfi.dk/) har pr. 31. august 2023 nedlagt den hidtil anvendte API-tjeneste Geosearch, og erstattet den med den nye tjeneste [Gsearch](https://docs.dataforsyningen.dk/#gsearch-dokumentation). Du skal opdatere til den nye version af pluginet (version 2.0.0) for at dit plugin bruger Gsearch - **og derfor virker efter 31. august 2023**. Du henter den nye version fra QGIS' plugin repository - dette er lettest at hente direkte fra QGIS. Læs mere om dette i afsnittet [Opdatering af pluginet](#opdatering-af-pluginet).

Læs nyheden om ændringen i dette plugin [på Septimas hjemmeside](https://septima.dk/nyheder/Ny-version-GeosearchDKplugin) eller detaljer om Gsearch i [projektets koderepository](https://github.com/SDFIdk/gsearch).

Installation af pluginet
--------------
Pluginet er tilgængeligt fra QGIS' officielle plugin repository, dermed finder en installation af QGIS selv en kompatibel version af pluginet.

Det letteste er at installere pluginet via QGIS. Dette gør du således:
   * Under menuen 'Plugins', vælg 'Administrér og Installér Plugins...' (I den engelske version af QGIS hedder denne menu 'Manage and Install Plugins...')
   * I Plugins-dialogen, søg efter 'Geosearch DK'
   * Vælg 'Geosearch DK' i listen (så denne bliver markeret med blå)
   * Klik på 'Installér Plugin'. Derefter installeres pluginet.

![Install-geosearchdk](https://github.com/Septima/qgis-geosearch/assets/16276034/3b5a5d6c-70fe-49a0-9372-1fdb18585831)


Pluginet installerer et QGIS-panel med en søgeboks, der som udgangspunkt lægger sig oven for kortvinduet. Panelet kan flyttes, så det f.eks. ligger oven for lagpanelet i stedet. På denne placering fylder det ikke så meget, men er stadig let tilgængeligt.

Hvis man trykker på krydset i Geosearch DK-panelet bliver det deaktiveret og forsvinder helt fra visningen, men kan nemt genaktiveres ved at sætte flueben ved det under menupunktet Visning->Paneler (på engelsk View->Panels).

Pluginet distribueres med et fungerende token til Dataforsyningen. Det er muligt at angive sit eget token (dvs. [autentificere som en bestemt bruger](https://dataforsyningen.dk/news/3808)) under pluginets indstillinger, som findes ved at gå til menupunktet Indstillinger->Indstillinger->Geosearch DK (engelsk Settings->Options) eller bruge genvejen via skruenøgle-ikonet i panelet.

Opdatering af pluginet
--------------
Nye versioner af pluginet udstilles via QGIS' officielle plugin repository. I Plugin Manageren vil opdateringer fremgå under punktet Upgradeable. Automatisk advisering om opgraderbare plugins kan aktiveres under Settings i Plugin Manageren.

Vil du selv opdatere dit plugin, så gør således:
   * Åbn pluginsdialogen
   * Søg efter 'GeosearchDK'
   * Vælg GeosearchDK i listen
   * Klik på 'Opgradér Plugin'. Derefter opgraderes pluginet til den nyeste version.

![geosearchopgraderplugin](https://github.com/Septima/qgis-geosearch/assets/16276034/7ec1bf18-a5d4-4ba2-ae4d-089f93d6e3bc)


Indstillinger
-----------------
Du kan lave en række indstillinger i pluginets indstillingsfane, som du kan åbne ved at klikke på skruenøgle-ikonet (eller gå til menupunktet Indstillinger->Indstillinger->Geosearch DK (engelsk Settings->Options)):
![geosearchdk-opensettings](https://github.com/Septima/qgis-geosearch/assets/16276034/3f56d335-7397-4779-b7b0-c39e811fd9eb)

Følgende indstillinger kan foretages i pluginets indstillingsdialog:
- Token til Dataforsyningen (Opret token [her](https://dataforsyningen.dk/user#token)) - sørg for at du er logget ind øverst til højre og opret derefter et token under "Administrer token til webservices og API'er"
- Kommunefilter. Indtast et eller flere kommunenumre adskilt af komma. Der vises nu kun søgeresultater fra de listede kommuner.
- Typefilter. Vis kun søgeresultater af bestemte typer, f.eks. adresser, matrikelnumre, stednavne etc.

![geosearchsettings](https://github.com/Septima/qgis-geosearch/assets/16276034/ffcfe419-38af-4ed1-80f8-bc2264919fb0)


Oplever du fejl eller har du ønsker til forbedringer eller ny funktionalitet?
-----------------
Der er allerede en række forslag til forbedringer i projektets [Issuetracker](../../issues).

Har du en idé til en forbedring eller har du måske opdaget en bug i pluginet, så vil Septima med glæde tilbyde sin bistand.

Du kan registrere din idé eller bug i projektets [Issuetracker](../../issues). Her kan du også se eksisterende registreringer af idéer og bugs.

Ophavsret og videredistribution
-------------------------------
Pluginet er udviklet af [Septima](http://www.septima.dk), som er primær ophavsretsindehaver men som har givet tilladelse til distribution under betingelserne i Open Source/Fri Software-licensen [GNU General Public License v3.0](http://www.gnu.org/licenses/gpl.html) eller senere ([GPL3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later)).

Det indeholder dog også kode fra projektet [QGIS Setting Manager](https://opengisch.github.io/qgis_setting_manager/) (under stien `src/geosearch_dk/config/qgissettingmanager/`) som kan distribueres under licensen [GNU General Public License v2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html) eller senere ([GPL2.0-or-later](https://spdx.org/licenses/GPL-2.0-or-later)).

Ophavsretsinformation og licensbetingelser for en konkret fil kan altid ses i toppen af den enkelte fil.
