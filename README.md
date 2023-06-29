Geosearch DK
==============

QGIS plugin med en søgebox, som tillader brugeren lynhurtigt at zoome til navngivne steder i Danmark - fx adresser, stednavne, kommuner.

Pluginet er udviklet af [Septima](http://www.septima.dk), som har frigivet det under Open Source licensen [GPL3](http://www.gnu.org/licenses/gpl.html).

Vigtig information
--------------
SDFI lukker tjenesten `Geosearch`, hvilket har betydning for dette plugin. Læs [mere her](https://github.com/Septima/qgis-geosearch/issues/50).

Installation
--------------
Pluginet er tilgængeligt fra QGIS' officielle plugin repository, dermed finder QGIS selv en kompatibel version af pluginet.

Pluginet installerer en søgebox, der som udgangspunkt lægger sig oven for kortvinduet. Panelet kan f.eks. flyttes, så det ligger oven for lagkontrollen i stedet. På denne placering fylder det ikke så meget, men er stadig let tilgængeligt.

Pluginet distribueres med et fungerende token til Dataforsyningen. Det er muligt at angive sit eget token.

Opdatering
--------------
Nye versioner af pluginet udstilles via QGIS' officielle plugin repository. I Plugin Manageren vil opdateringer fremgå under punktet Upgradeable. Automatisk advisering om opgraderbare plugins kan aktiveres under Settings i Plugin Manageren.

Indstillinger
-----------------
Følgende instilllinger kan foretages i pluginets indstillingsdialog (Klik Indstillinger -> Generelle Indstillinger -> Geosearch DK):
- Token til dataforsyningen (Opret bruger [her]([https://dataforsyningen.dk/user#token](https://dataforsyningen.dk/)) - sørg for at du er logget ind øverst til højre og opret derefter et token under "Administrer token til webservices og API'er"
- Kommunefilter. Indtast et eller flere kommunenumre adskilt af komma. Der vises nu kun søgeresultater fra de listede kommuner.
- Typefilter. Vis kun søgeresultater af bestemte typer, fx adresser, matrikelnumre, stednavne etc.

Ny funktionalitet
-----------------
Der er allerede en række forslag til forbedringer i projektets [Issuetracker](../../issues).

Har du en idé til en forbedring eller har du måske opdaget en bug i pluginet, så vil Septima med glæde tilbyde sin bistand.

Du kan registrere din idé eller bug i projektets [Issuetracker](../../issues). Her kan du også se eksistrende registreringer af idéer og bugs.
