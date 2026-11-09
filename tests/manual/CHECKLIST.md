# Manual checklist

Exploratory checks of the plugin in a real QGIS. The automated visual run
(`make visual`, see [docs/development.md](../../docs/development.md)) covers
searching and zooming for the cases in `tests/cases.yaml`; this list covers
the rest.

Run the list in **both QGIS 4 and QGIS 3**:

```sh
make dev            # QGIS 4
make dev QGIS=3     # QGIS 3
```

Keep *View > Panels > Log Messages* open, and the Python console if you want.
Note anything unexpected in the log (Python errors, warnings from the plugin).

Copy the list into the PR or issue and tick the boxes there.

Items marked *(Bifrost)* only apply to the Bifrost version of the plugin.

```
QGIS version: ____   OS: ____   Plugin commit: ____
```

## Search and selection

- [ ] Typing in the search box opens the result popup after a short pause.
      Typing more updates the list.
- [ ] **Keyboard**: Down/Up moves through the hits. Enter selects the hit:
      the map zooms to it and draws it (marker for a point, outline for an
      area).
- [ ] **Mouse**: clicking a hit selects it in the same way.
- [ ] Clicking the empty area of the popup, or outside it, does not select
      anything and does not leave a broken popup.
- [ ] **Esc** closes the popup and keeps the typed text. The search box keeps
      the focus.
- [ ] Clearing the search box (the ✕ button) removes the marker or outline
      from the map.
- [ ] A new search replaces the previous marker or outline; it does not add
      another one.
- [ ] A search with no hits gives an empty result or a clear message, not an
      error.
- [ ] Danish letters (æ, ø, å) and prefixes such as `kom:` work.

## Map and CRS

- [ ] With the project CRS **EPSG:25832**, the hit is drawn in the right
      place over a basemap.
- [ ] With a **different project CRS** (e.g. EPSG:4326 and EPSG:3857), the
      hit is drawn in the right place and the map zooms to the right area.
- [ ] Changing the project CRS while a hit is shown does not leave the hit in
      the wrong place (or the hit is removed).
- [ ] Areas (kommune, matrikel, ...) are zoomed so the whole area is
      visible. Points are zoomed to a sensible scale.

## Panel

- [ ] The *Geosearch DK* panel can be docked at the top, the sides and the
      bottom, and floated. The search box works in every position.
- [ ] Closing the panel and opening it again from *View > Panels* works.
- [ ] The panel position is kept after a QGIS restart.
- [ ] The popup is placed under the search box, also when the panel is
      floating or near the edge of the screen.

## Settings

- [ ] The settings open from the panel (wrench icon) and from
      *Settings > Options > Geosearch DK*.
- [ ] Turning a result type (adresser, stednavne, ...) off removes those hits
      from the next search. Turning it on again brings them back.
- [ ] The kommunefilter limits the hits to the chosen kommuner. An empty
      filter gives hits from the whole country.
- [ ] *(Bifrost)* The kommunefilter is off by default. The code field is
      enabled only when *Filtrér søgeresultater lokalt på kommune* is ticked,
      and the explanation of the gotchas is always visible below it.
- [ ] *(Bifrost)* With the filter on, hidden hits are counted in a grey last
      row ("N resultater uden for kommunefilteret er skjult"). Choosing it
      (click or Enter) explains the filter and offers to open the settings;
      it does not zoom anywhere. `1a` with kommune 615 shows only that row.
- [ ] *(Bifrost)* An unknown kommune code (e.g. `999`) gives an error row
      and a message bar with a button to the settings.
- [ ] Settings are kept after a QGIS restart.
- [ ] Cancel in the options dialog does not change the settings.

## Dialogs and messages

- [ ] *(Bifrost)* **No dialog at startup**: the "what's new" dialog opens
      only from ⓘ, the banner link or the kommunefilter links. Links in it
      open in the web browser.
- [ ] *(Bifrost)* **Info banner** (blue): after upgrading from the GSearch
      version (a profile with an old token, kommunefilter or saved types),
      the search panel shows "Geosearch DK søger nu i Klimadatastyrelsens
      Bifrost …" and ⓘ has a red dot. A new profile shows neither.
- [ ] *(Bifrost)* **✕** hides the banner, also after a restart; the red dot
      stays until the dialog has been opened. *Se hvad der er ændret* or ⓘ
      opens the dialog and removes both.
- [ ] *(Bifrost)* **Key banner** (yellow, no ✕): shown when no Bifrost key is
      set. *Indtast nøgle* opens the settings with the cursor in the key
      field; *Hvorfor?* opens the dialog at the key section. Saving a key
      hides it at once. Searching without a key shows no message bar.
- [ ] *(Bifrost)* Both banners read well docked at the top (long text) and in
      a narrow side dock (short text, links on their own line), in a light
      and a dark theme.
- [ ] *(Bifrost)* **Kommunefilter migration**: in a profile with an old
      GSearch kommunefilter setting, the filter is migrated on first start,
      and the **message bar** explains what happened. The message is shown
      only once.
- [ ] Message bar messages can be closed.
- [ ] *(Bifrost)* **One language at a time**: with QGIS in Danish (or any
      language but English) everything is Danish; with QGIS in English
      (*Settings > Options > General > Override system locale*, e.g.
      `en_DK`, then restart) the panel, banners, tooltips, settings page, type
      checkboxes, message bars, error rows and the "what's new" dialog
      including its text are all English.

## Errors

- [ ] **Offline** (turn off Wi-Fi): searching gives a clear message, not a
      Python error. Searching works again when the network is back, without
      restarting QGIS.
- [ ] **401** (invalid Bifrost API key; set it under Bifrost API-nøgle in the
      settings, or point Avanceret → Bifrost URL at the mock server): a clear message that tells the
      user what to do.
- [ ] **503** (service unavailable, e.g. with the mock server): a clear
      message, and the plugin keeps working afterwards.
- [ ] A slow service does not freeze QGIS while typing.

## Unload

- [ ] Turning the plugin off in *Plugins > Manage and Install Plugins*
      removes the panel, the options page and any marker on the map, without
      errors in the log.
- [ ] Turning it on again works, and searching works.
- [ ] Reloading with Plugin Reloader works several times in a row, without
      duplicate panels or errors.
- [ ] Quitting QGIS with the plugin loaded does not give errors or a crash.
