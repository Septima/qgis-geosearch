"""Display texts for Bifrost matches (#1).

GSearch returned a ready-made ``visningstekst``. Bifrost returns a short
``result`` plus structured ``components``, so the plugin builds the text. The
rules reproduce GSearch's texts wherever Bifrost has the data (checked against
GSearch for every kommune, region, opstillingskreds, politikreds and
retskreds). Stednavne cannot: the subtype and locality are not in
Bifrost, so they get "Skodsborg (bebyggelse, Rudersdal)" instead of
"Skodsborg (By i Rudersdal Kommune)".

Pure Python: must not import qgis or PyQt.
"""

# Kommuner whose GSearch text is not "<navn> Kommune". Keyed by kommunekode.
KOMMUNE_TEXT_EXCEPTIONS = {
    "0101": "Københavns Kommune",
    "0411": "Christiansø",
}

ADDRESS_KINDS = ("unit", "entrance")

LIFECYCLE_NOTES = {"retired": "udgået"}

EJENDOM_TYPE_NOTES = {
    "bygning_paa_fremmed_grund": "bygning på fremmed grund",
}


def _first(components, key):
    items = components.get(key) or []
    return items[0] if items else {}


def _join(*parts, sep=", "):
    return sep.join(p for p in parts if p)


def _address(match, c, result):
    if result:
        return result
    number = _join(c.get("house_number"), c.get("house_letter"), sep="")
    floor_door = ""
    if c.get("floor"):
        floor_door = _join(c["floor"] + ".", c.get("door"), sep=" ")
    elif c.get("door"):
        floor_door = c["door"]
    pc = _first(c, "postcodes")
    return _join(
        _join(c.get("street"), number, sep=" "),
        floor_door,
        c.get("sub_locality"),
        _join(pc.get("postcode"), pc.get("city"), sep=" "),
    )


def _postcode(match, c, result):
    pc = _first(c, "postcodes")
    if pc.get("postcode"):
        return _join(pc["postcode"], pc.get("city") or result, sep=" ")
    return result


def _kommune(match, c, result):
    k = _first(c, "kommuner")
    code = k.get("kommunekode")
    if code in KOMMUNE_TEXT_EXCEPTIONS:
        return KOMMUNE_TEXT_EXCEPTIONS[code]
    name = k.get("kommune") or result
    return name + " Kommune" if name else ""


def _region(match, c, result):
    return _first(c, "regioner").get("region") or result


def _opstillingskreds(match, c, result):
    name = _first(c, "opstillingskredse").get("opstillingskreds") or result
    return name + "kredsen" if name else ""


def _politikreds(match, c, result):
    name = _first(c, "politikredse").get("politikreds") or result
    if name.endswith(" Politi"):
        return name + "kreds"
    return name


def _retskreds(match, c, result):
    return _first(c, "retskredse").get("retskreds") or result


def _sogn(match, c, result):
    # Many sogne share a name ("Vor Frue"), so the kommune is added.
    name = _first(c, "sogne").get("sogn") or result
    if not name:
        return ""
    kommuner = _join(*(k.get("kommune") for k in c.get("kommuner") or []))
    text = name + " sogn"
    return "%s (%s)" % (text, kommuner) if kommuner else text


def _stednavn(match, c, result):
    name = c.get("stednavn") or result
    kommune = _first(c, "kommuner").get("kommune")
    detail = _join(c.get("type"), kommune)
    return "%s (%s)" % (name, detail) if detail else name


def _street(match, c, result):
    name = c.get("street") or result
    postcodes = _join(
        *(
            _join(p.get("postcode"), p.get("city"), sep=" ")
            for p in c.get("postcodes") or []
        )
    )
    return "%s (%s)" % (name, postcodes) if postcodes else name


def _city(match, c, result):
    name = result or _first(c, "postcodes").get("city") or ""
    codes = _join(*(p.get("postcode") for p in c.get("postcodes") or []))
    return "%s (%s)" % (name, codes) if codes else name


def _ejerlav(match, c, result):
    return result or c.get("ejerlav") or ""


def _parcel_count_note(ejendom):
    """"del af ejendom med 27 matrikler" for a property on more than one parcel.

    The hit is the whole property, but its text names only the matched parcel,
    as GSearch's parcel hits did (#4).
    """
    parcels = ejendom.get("parcels") or {}
    n = len(parcels.get("items") or [])
    if n < 2:
        return None
    more = "" if parcels.get("complete", True) else "+"
    return "del af ejendom med %d%s matrikler" % (n, more)


def _ejendom(match, c, result):
    # result names the parcel the search matched, e.g. "3kg, Søllerød By, Søllerød",
    # which is GSearch's matrikel text.
    text = result or _join(c.get("matrikelnummer"), c.get("ejerlav"))
    ejendom = match.get("ejendom") or {}
    notes = []
    etype = ejendom.get("type")
    # An ejerlejlighed or a bygning på fremmed grund lists the land it stands
    # on, so the count is only shown for the property that owns the land.
    if etype in (None, "samlet_fast_ejendom"):
        count = _parcel_count_note(ejendom)
        if count:
            notes.append(count)
    if etype == "ejerlejlighed":
        notes.append(
            _join("ejerlejlighed", ejendom.get("ejerlejlighedsnummer"), sep=" ")
        )
    elif etype in EJENDOM_TYPE_NOTES:
        notes.append(EJENDOM_TYPE_NOTES[etype])
    notes = [n for n in notes if n.lower() not in text.lower()]
    if notes:
        text = "%s (%s)" % (text, ", ".join(notes))
    return text


_BUILDERS = {
    "unit": _address,
    "entrance": _address,
    "postcode": _postcode,
    "kommune": _kommune,
    "region": _region,
    "opstillingskreds": _opstillingskreds,
    "politikreds": _politikreds,
    "retskreds": _retskreds,
    "sogn": _sogn,
    "stednavn": _stednavn,
    "street": _street,
    "city": _city,
    "ejerlav": _ejerlav,
    "ejendom": _ejendom,
}


def display_text(match, kind=None):
    """The text shown in the result list for a Bifrost match.

    ``kind`` defaults to ``match["ref"]["kind"]``. Unknown kinds fall back to
    Bifrost's ``result``. Retired hits get " (udgået)".
    """
    if kind is None:
        kind = (match.get("ref") or {}).get("kind")
    components = match.get("components") or {}
    result = match.get("result") or ""
    builder = _BUILDERS.get(kind)
    text = (builder(match, components, result) if builder else "") or result
    note = LIFECYCLE_NOTES.get(match.get("lifecycle"))
    if note and note not in text:
        text = "%s (%s)" % (text, note)
    return text
