"""Display texts. Expected values are GSearch's visningstekst for the same feature
unless marked as proposed (no GSearch counterpart, or not reproducible)."""

import pytest

from geosearch_dk.bifrost import display_text


def m(kind, result="", lifecycle="current", ejendom=None, **components):
    return {
        "ref": {"kind": kind, "id": "x"},
        "result": result,
        "lifecycle": lifecycle,
        "components": components,
        "ejendom": ejendom,
    }


def kom(code, name):
    return [{"kommunekode": code, "kommune": name}]


def pc(*pairs):
    return [{"postcode": p, "city": c} for p, c in pairs]


@pytest.mark.parametrize(
    "match, text",
    [
        (
            m("entrance", "Borgergade 15, Magleby, 4672 Klippinge"),
            "Borgergade 15, Magleby, 4672 Klippinge",
        ),
        (
            m(
                "entrance",
                street="Vangebovej",
                house_number="71",
                sub_locality="Søllerød",
                postcodes=pc(("2840", "Holte")),
            ),
            "Vangebovej 71, Søllerød, 2840 Holte",
        ),
        (
            m(
                "unit",
                street="Nøddebogade",
                house_number="1",
                floor="st",
                door="th",
                postcodes=pc(("2200", "København N")),
            ),
            "Nøddebogade 1, st. th, 2200 København N",
        ),
        (
            m(
                "entrance",
                street="Vestergade",
                house_number="1",
                house_letter="B",
                postcodes=pc(("8000", "Aarhus C")),
            ),
            "Vestergade 1B, 8000 Aarhus C",
        ),
        (
            m("postcode", "Aarhus C", postcodes=pc(("8000", "Aarhus C"))),
            "8000 Aarhus C",
        ),
        (m("kommune", "Aarhus", kommuner=kom("0751", "Aarhus")), "Aarhus Kommune"),
        (
            m("kommune", "København", kommuner=kom("0101", "København")),
            "Københavns Kommune",
        ),
        (
            m("kommune", "Christiansø", kommuner=kom("0411", "Christiansø")),
            "Christiansø",
        ),
        (
            m("kommune", "Bornholm", kommuner=kom("0400", "Bornholm")),
            "Bornholm Kommune",
        ),
        (
            m(
                "region",
                "Region Hovedstaden",
                regioner=[{"regionskode": "1084", "region": "Region Hovedstaden"}],
            ),
            "Region Hovedstaden",
        ),
        (
            m(
                "opstillingskreds",
                "Aarhus Nord",
                opstillingskredse=[
                    {
                        "opstillingskredsnummer": "0049",
                        "opstillingskreds": "Aarhus Nord",
                    }
                ],
            ),
            "Aarhus Nordkredsen",
        ),
        (
            m(
                "opstillingskreds",
                "Esbjerg By",
                opstillingskredse=[
                    {"opstillingskredsnummer": "0070", "opstillingskreds": "Esbjerg By"}
                ],
            ),
            "Esbjerg Bykredsen",
        ),
        (
            m(
                "politikreds",
                "Midt- og Vestjyllands Politi",
                politikredse=[
                    {
                        "politikredsnummer": "1466",
                        "politikreds": "Midt- og Vestjyllands Politi",
                    }
                ],
            ),
            "Midt- og Vestjyllands Politikreds",
        ),
        (
            m(
                "retskreds",
                "Retten i Lyngby",
                retskredse=[
                    {"retskredsnummer": "1163", "retskreds": "Retten i Lyngby"}
                ],
            ),
            "Retten i Lyngby",
        ),
        (
            m(
                "ejendom",
                "3kg, Øverød By, Søllerød",
                matrikelnummer="3kg",
                ejerlav="Øverød By",
            ),
            "3kg, Øverød By, Søllerød",
        ),
    ],
)
def test_gsearch_texts(match, text):
    assert display_text(match) == text


@pytest.mark.parametrize(
    "match, text",
    [
        # GSearch: "Skodsborg (By i Rudersdal Kommune)"; Bifrost lacks the subtype.
        (
            m(
                "stednavn",
                "Skodsborg",
                stednavn="Skodsborg",
                type="bebyggelse",
                kommuner=kom("0230", "Rudersdal"),
            ),
            "Skodsborg (bebyggelse, Rudersdal)",
        ),
        (
            m("stednavn", "Kattegat", stednavn="Kattegat", type="farvand"),
            "Kattegat (farvand)",
        ),
        (
            m(
                "sogn",
                "Vor Frue",
                sogne=[{"sognekode": "7158", "sogn": "Vor Frue"}],
                kommuner=kom("0265", "Roskilde"),
            ),
            "Vor Frue sogn (Roskilde)",
        ),
        (
            m(
                "street",
                "Skodsborgvej",
                street="Skodsborgvej",
                postcodes=pc(
                    ("2830", "Virum"),
                    ("2840", "Holte"),
                    ("2850", "Nærum"),
                    ("2942", "Skodsborg"),
                ),
            ),
            "Skodsborgvej (2830 Virum, 2840 Holte, 2850 Nærum, 2942 Skodsborg)",
        ),
        (
            m(
                "street",
                "Skodsborgvej, 9270 Klarup",
                street="Skodsborgvej",
                postcodes=pc(("9270", "Klarup")),
            ),
            "Skodsborgvej (9270 Klarup)",
        ),
        (
            m(
                "city",
                "Aarhus",
                postcodes=pc(("8000", "Aarhus C"), ("8200", "Aarhus N")),
            ),
            "Aarhus (8000, 8200)",
        ),
        (
            m("ejerlav", "Søllerød By", ejerlav="Søllerød By", ejerlavskode=2000151),
            "Søllerød By",
        ),
        (
            m("ejendom", "1an, Gentofte", lifecycle="retired", matrikelnummer="1an"),
            "1an, Gentofte (udgået)",
        ),
        (
            m(
                "ejendom",
                "12, Vesterbro",
                ejendom={"type": "ejerlejlighed", "ejerlejlighedsnummer": "4"},
            ),
            "12, Vesterbro (ejerlejlighed 4)",
        ),
        (
            m("ejendom", "7b, Lyngby", ejendom={"type": "bygning_paa_fremmed_grund"}),
            "7b, Lyngby (bygning på fremmed grund)",
        ),
        (
            m(
                "ejendom",
                "3kg, Vangede",
                ejendom={
                    "type": "samlet_fast_ejendom",
                    "parcels": {"items": [{}, {}, {}], "complete": True},
                },
            ),
            "3kg, Vangede (del af ejendom med 3 matrikler)",
        ),
        (
            m(
                "ejendom",
                "1a, Stort Ejerlav",
                ejendom={"parcels": {"items": [{}] * 1000, "complete": False}},
            ),
            "1a, Stort Ejerlav (del af ejendom med 1000+ matrikler)",
        ),
        (
            m(
                "ejendom",
                "3kg, Søllerød By, Søllerød",
                ejendom={"type": "samlet_fast_ejendom", "parcels": {"items": [{}]}},
            ),
            "3kg, Søllerød By, Søllerød",
        ),
        (
            m(
                "ejendom",
                "12, Vesterbro",
                ejendom={
                    "type": "ejerlejlighed",
                    "ejerlejlighedsnummer": "4",
                    "parcels": {"items": [{}, {}]},
                },
            ),
            "12, Vesterbro (ejerlejlighed 4)",
        ),
        (
            m("ejendom", "", matrikelnummer="3kg", ejerlav="Søllerød By"),
            "3kg, Søllerød By",
        ),
        (m("something_new", "Whatever it is"), "Whatever it is"),
    ],
)
def test_proposed_texts(match, text):
    assert display_text(match) == text


def test_kind_argument_overrides_ref_kind():
    match = m("unit", "Vangebovej 71, Søllerød, 2840 Holte")
    assert display_text(match, "entrance") == "Vangebovej 71, Søllerød, 2840 Holte"
