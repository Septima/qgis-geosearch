Geosearch DK
==============

QGIS plugin med en søgebox, som tillader brugeren lynhurtigt at zoome til navngivne steder i Danmark.

Pluginet er udviklet af [Septima](http://www.septima.dk), som har frigivet det under Open Source licensen [GPL3](http://www.gnu.org/licenses/gpl.html).
Installation
--------------
Den nemmeste måde at installere pluginet på, er at tilføje Septima's repository til QGIS. På den måde finder QGIS selv en kompatibel version af pluginet, og du får atumatisk besked, når der kommer nye versioner af pluginet.

Uanset installationsmetoden kræver pluginet et fungerende login til [Kortforsyningen.dk](http://www.kortforsyningen.dk/). Selvom geosearch-servicen på Kortforsyningen er fri, så er der set eksempler på, at der ikke er åbnet for servicen for eksisterende (feks kommunale) brugere af Kortforsyningen.

Pluginet installerer en søgebox, der som udgangspunkt lægger sig oven for kortvinduet. Panelet kan feks flyttes, så det ligger oven for lagkontrollen i stedet. På denne placering fylder det ikke så meget, men er stadig let tilgængeligt.

###QGIS 1.8
 - 1) Åbn Plugin Installeren (Klik Plugins -> Fetch python plugins...)
 - 2) Under fanebladet Repositories klikkes Add
 - 3) Indtast et selvvalgt navn (feks Septima) og under URL indtastes http://qgis.septima.dk/plugins
 - 4) Pluginet vil nu være listet Under fanebladet Plugins

###QGIS 2.0 (inkl nyere 1.9)
 - 1) Åbn Plugin Manageren (Klik Plugins -> Manage and Install Plugins)
 - 2) Vælg Settings
 - 3) Klik Add under Plugin Repositories
 - 4) Indtast et selvvalgt navn (feks Septima) og under URL indtastes http://qgis.septima.dk/plugins
 - 5) I Plugin Manageren vil pluginet nu være listet under Get more

![Add repository](http://septima.github.io/qgis-geosearch/img/qgis2-addrepo.PNG)

Ny funktionalitet
-----------------
Der er allerede en række forslag til forbedringer i projektets [Issuetracker](../../issues).

Har du en idé til en forbedring eller har du måske opdaget en bug i pluginet, så vil Septima med glæde tilbyde sin bistand.

Du kan registrere din idé eller bug i projektets [Issuetracker](../../issues). Her kan du også se eksistrende registreringer af idéer og bugs.
