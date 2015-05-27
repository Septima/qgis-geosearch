KMR TESTER
Geosearch DK
==============

QGIS plugin med en søgebox, som tillader brugeren lynhurtigt at zoome til navngivne steder i Danmark.

Pluginet er udviklet af [Septima](http://www.septima.dk), som har frigivet det under Open Source licensen [GPL3](http://www.gnu.org/licenses/gpl.html).
Installation
--------------
Den nemmeste måde at installere pluginet på, er at tilføje Septima's repository til QGIS. På den måde finder QGIS selv en kompatibel version af pluginet, og du får atumatisk besked, når der kommer nye versioner af pluginet.

Uanset installationsmetoden kræver pluginet et fungerende login til [Kortforsyningen.dk](http://www.kortforsyningen.dk/).

Pluginet installerer en søgebox, der som udgangspunkt lægger sig oven for kortvinduet. Panelet kan feks flyttes, så det ligger oven for lagkontrollen i stedet. På denne placering fylder det ikke så meget, men er stadig let tilgængeligt.

###QGIS 2.x
 - 1) Åbn Plugin Manageren (Klik Plugins -> Manage and Install Plugins)
 - 2) Vælg Settings
 - 3) Klik Add under Plugin Repositories
 - 4) Indtast et selvvalgt navn (feks Septima) og under URL indtastes http://qgis.septima.dk/plugins
 - 5) I Plugin Manageren vil pluginet nu være listet under Get more

![Add repository](http://septima.github.io/qgis-geosearch/img/qgis2-addrepo.PNG)

Opdatering
--------------
Nye versioner af pluginet udstilles via Septimas plugin repository, som installeret ovenfor. I Plugin Manageren vil opdateringer fremgå under punktet Upgradeable. Automatisk advisering om opgraderbare plugins kan aktiveres under Settings i Plugin Manageren.

Indstillinger
-----------------
Følgende instilllinger kan foretages i pluginets indstillingsdialog (Klik Plugins -> Geosearch DK -> Indstillinger):
- Brugernavn og password til Kortforsyningen (Opret bruger [her](http://download.kortforsyningen.dk/user/register))
- Kommunefilter. Indtast et eller flere kommunenumre adskilt af komma. Der vises nu kun søgeresultater fra de listede kommuner.

Ny funktionalitet
-----------------
Der er allerede en række forslag til forbedringer i projektets [Issuetracker](../../issues).

Har du en idé til en forbedring eller har du måske opdaget en bug i pluginet, så vil Septima med glæde tilbyde sin bistand.

Du kan registrere din idé eller bug i projektets [Issuetracker](../../issues). Her kan du også se eksistrende registreringer af idéer og bugs.
