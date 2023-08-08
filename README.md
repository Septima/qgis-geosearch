Geosearch DK
==============

QGIS plugin med en søgebox, som tillader brugeren lynhurtigt at zoome til navngivne steder i Danmark - fx adresser, stednavne, kommuner.

Pluginet er udviklet af [Septima](http://www.septima.dk), som har frigivet det under Open Source licensen [GPL3](http://www.gnu.org/licenses/gpl.html).

OBS - Er dit plugin stoppet med at virke efter 31. august 2023?
--------------
Styrelsen for Dataforsyning og Infrastruktur (SDFI) har pr. 31. august 2023 nedlagt API-tjenesten Geosearch. Denne tjeneste er erstattet af den nye tjeneste Gsearch. Du skal opdatere til den nye version af pluginet (version 2.0.0) for at dit plugin bruger Gsearch - **og derfor virker efter 31. august 2023**. Du henter den nye version fra QGIS' plugin repository - dette er lettest at hente direkte fra QGIS. Læs mere om dette under afsnittet 'Opdatering af pluginet'.

Installation af pluginet
--------------
Pluginet er tilgængeligt fra QGIS' officielle plugin repository, dermed finder QGIS selv en kompatibel version af pluginet.

Det letteste er at installere pluginet via QGIS. Dette gør du således:
   * Under menuen 'Plugins', vælg 'Administrér og Installér Plugins...' (I den engelske version af QGIS hedder denne menu 'Manage and Install Plugins...')
   * I Plugins-dialogen, søg efter 'GeosearchDK'
   * Vælg 'GeosearchDK' i listen (så denne bliver markeret med blå)
   * Klik på 'Installér Plugin'. Derefter installeres pluginet.

![Install-geosearchdk](https://github.com/Septima/qgis-geosearch/assets/16276034/3b5a5d6c-70fe-49a0-9372-1fdb18585831)


Pluginet installerer en søgebox, der som udgangspunkt lægger sig oven for kortvinduet. Panelet kan flyttes, så det fx ligger oven for lagpanelet i stedet. På denne placering fylder det ikke så meget, men er stadig let tilgængeligt.

Pluginet distribueres med et fungerende token til Dataforsyningen. Det er muligt at angive sit eget token under pluginets indstillinger.

Opdatering af pluginet
--------------
Nye versioner af pluginet udstilles via QGIS' officielle plugin repository. I Plugin Manageren vil opdateringer fremgå under punktet Upgradeable. Automatisk advisering om opgraderbare plugins kan aktiveres under Settings i Plugin Manageren.

Vil du selv opdatere dit plugin, så gør således:
   * Åbn pluginsdialogen
   * Søg efter 'GeosearchDK'
   * Vælg GeosearchDK i listen
   * Klik på 'Opgradér Plugin'. Derefter opgraderes pluginet til den nyeste version.

![geosearchopgrader](https://github.com/Septima/qgis-geosearch/assets/16276034/58e8fd02-a770-4931-9079-8e949e3f97a3)


Indstillinger
-----------------
Du kan lave en række indstillinger i pluginets indstillingsfane, som du kan åbne ved at klikke på skruenøgle-ikonet:
![geosearchdk-opensettings](https://github.com/Septima/qgis-geosearch/assets/16276034/3f56d335-7397-4779-b7b0-c39e811fd9eb)

Følgende instilllinger kan foretages i pluginets indstillingsdialog:
- Token til Dataforsyningen (Opret token [her]([https://dataforsyningen.dk/user#token](https://dataforsyningen.dk/)) - sørg for at du er logget ind øverst til højre og opret derefter et token under "Administrer token til webservices og API'er"
- Kommunefilter. Indtast et eller flere kommunenumre adskilt af komma. Der vises nu kun søgeresultater fra de listede kommuner.
- Typefilter. Vis kun søgeresultater af bestemte typer, fx adresser, matrikelnumre, stednavne etc.

![geosearchsettings](https://github.com/Septima/qgis-geosearch/assets/16276034/ffcfe419-38af-4ed1-80f8-bc2264919fb0)


Oplever du fejl eller har du ønsker til forbedringer eller ny funktionalitet?
-----------------
Der er allerede en række forslag til forbedringer i projektets [Issuetracker](../../issues).

Har du en idé til en forbedring eller har du måske opdaget en bug i pluginet, så vil Septima med glæde tilbyde sin bistand.

Du kan registrere din idé eller bug i projektets [Issuetracker](../../issues). Her kan du også se eksistrende registreringer af idéer og bugs.
