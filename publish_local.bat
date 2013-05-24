ECHO Publish to local user QGIS

SET DEST=%USERPROFILE%\.qgis\python\plugins\geosearch_dk %USERPROFILE%\.qgis2\python\plugins\geosearch_dk

IF NOT EXIST %DEST% MD %DEST%

REM EXTENSIONS TO COPY
SET EXT=py,qrc,txt

FOR %%d IN (%DEST%) DO (
	IF NOT EXIST %%d MD %%d
	FOR /D %%e IN (%EXT%) DO COPY src\geosearch_dk\*.%%e %%d
)