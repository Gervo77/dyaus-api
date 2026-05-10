"""
DYAUS STEM ENGINE — Standalone versie voor Railway deployment.
Aangepaste paden (ephemeris/ zit naast dit bestand).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import swisseph as swe

# Paden — ephemeris/ zit naast dit bestand
_BASE = Path(__file__).resolve().parent
_EPHE = str(_BASE / "ephemeris")
swe.set_ephe_path(_EPHE)


# ═══════════════════════════════════════════════════════════════════
# BEWEZEN BEVINDINGEN
# ═══════════════════════════════════════════════════════════════════

class BewezenBevindingen:
    SATURN_GCR_ACTIVATIE = {
        "beschrijving": "Saturn-oppositie activeert extreme GCR-events",
        "ratio": 1.18,
        "monte_carlo_p": 0.0094,
        "dose_response_r2": 0.75,
        "oppositie_drop_freq": 0.085,
        "baseline_drop_freq": 0.070,
        "gcr_mean_drop_opp": -33.3,
        "gcr_mean_drop_base": -31.2,
        "bron": "dyaus_saturn_mars_asymmetrie.py",
        "status": "BEWEZEN",
    }

    SATURN_SEISMISCH = {
        "beschrijving": "Meer M7+ aardbevingen tijdens Saturn-oppositie",
        "totaal_bevingen": 848,
        "periode": "1964-2025",
        "opp_150_plus": {
            "n": 148,
            "percentage": 17.5,
            "verwacht": 15.0,
            "monte_carlo_p": 0.040,
        },
        "magnitude_afhankelijk": {
            "M7.0-7.5": {"pct": 17.0},
            "M7.5-8.0": {"pct": 15.7},
            "M8.0-8.5": {"pct": 26.2},
            "M8.5+":    {"pct": 50.0},
        },
        "top20_zwaarste": {
            "tijdens_opp": 6,
            "totaal": 20,
            "voorbeelden": [
                "Tohoku 2011 (M9.1)",
                "Sumatra 2004 (M9.1)",
                "Chile 2010 (M8.8)",
            ],
        },
        "bron": "dyaus_usgs_kruisreferentie.py",
        "status": "BEWEZEN",
    }

    MARS_DEMPING = {
        "beschrijving": "Mars-oppositie dempt extreme GCR-events",
        "mars_opp_ratio": 0.82,
        "richting": "tegengesteld aan Saturn",
        "onafhankelijk": True,
        "bron": "dyaus_saturn_mars_asymmetrie.py",
        "status": "BEWEZEN",
    }

    JUPITER_BESCHERMING = {
        "beschrijving": "Jupiter-oppositie correleert met minder aardbevingen",
        "z_score": -2.06,
        "richting": "beschermend",
        "bron": "dyaus_usgs_kruisreferentie.py",
        "status": "BEWEZEN",
    }

    DOMEIN_SPECIFICITEIT = {
        "beschrijving": "Effect is fysiek, NIET financieel",
        "financieel_ratio": 1.0,
        "financieel_p": 0.62,
        "fysiek_ratio": 1.20,
        "conclusie": "Saturn moduleert fysieke systemen, niet menselijke markten",
        "bron": "dyaus_financieel.py",
        "status": "BEWEZEN",
    }

    ONAFHANKELIJKHEID = {
        "beschrijving": "Saturn-activatie en Mars-demping zijn onafhankelijke effecten",
        "interactie_factor": 0.96,
        "bron": "dyaus_saturn_mars_asymmetrie.py",
        "status": "BEWEZEN",
    }


# ═══════════════════════════════════════════════════════════════════
# GEWOGEN HYPOTHESEN
# ═══════════════════════════════════════════════════════════════════

class GewogenHypothesen:
    SEIZOENSEFFECT = {
        "beschrijving": "Saturn-GCR effect sterker in herfst/winter",
        "herfst_ratio": 1.50,
        "winter_ratio": 1.30,
        "lente_ratio": 0.95,
        "zomer_ratio": 0.90,
        "betrouwbaarheid": "SUGGESTIEF",
        "bron": "dyaus_saturn_mars_asymmetrie.py",
    }

    KACHEL_MODEL = {
        "beschrijving": "Geintegreerde risicoscore",
        "top10_risico_ratio": 1.12,
        "top5_risico_ratio": 0.94,
        "welch_t": 0.709,
        "betrouwbaarheid": "ZWAK",
        "bron": "dyaus_kachel_model.py",
    }

    DREMPELGEDRAG = {
        "beschrijving": "Non-lineair omslagpunt rond 140-155 graden",
        "piek_zone": "150-155",
        "piek_ratio": 1.257,
        "omslagpunt": 140,
        "betrouwbaarheid": "SUGGESTIEF",
        "bron": "dyaus_kachel_model.py",
    }

    CREDO_CASCADE = {
        "beschrijving": "GCR-stormen voorafgaand aan aardbevingen",
        "onze_data": "niet bevestigd",
        "betrouwbaarheid": "NIET GEREPLICEERD",
        "bron": "dyaus_kachel_model.py",
    }

    SEISMISCHE_STILTE = {
        "beschrijving": "Grote bevingen voorafgegaan door seismische stilte",
        "verschil": 0.15,
        "welch_t": 0.560,
        "betrouwbaarheid": "NIET BEWEZEN",
        "bron": "dyaus_kachel_model.py",
    }


# ═══════════════════════════════════════════════════════════════════
# REAL-TIME PLANETAIRE BEREKENINGEN
# ═══════════════════════════════════════════════════════════════════

def _jd(d: date) -> float:
    return swe.julday(d.year, d.month, d.day, 12.0)


def bereken_elongatie(planeet_id: int, datum: date) -> float:
    jd = _jd(datum)
    zon_pos = swe.calc_ut(jd, swe.SUN)[0][0]
    planeet_pos = swe.calc_ut(jd, planeet_id)[0][0]
    verschil = abs(planeet_pos - zon_pos)
    if verschil > 180:
        verschil = 360 - verschil
    return round(verschil, 2)


def bereken_afstand_au(planeet_id: int, datum: date) -> float:
    jd = _jd(datum)
    result = swe.calc_ut(jd, planeet_id)
    return round(result[0][2], 4)


def bereken_snelheid(planeet_id: int, datum: date) -> float:
    jd = _jd(datum)
    result = swe.calc_ut(jd, planeet_id)
    return round(result[0][3], 4)


def bereken_positie(planeet_id: int, datum: date) -> Tuple[float, str]:
    jd = _jd(datum)
    lon = swe.calc_ut(jd, planeet_id)[0][0]
    tekens = [
        "Ram", "Stier", "Tweelingen", "Kreeft", "Leeuw", "Maagd",
        "Weegschaal", "Schorpioen", "Boogschutter", "Steenbok",
        "Waterman", "Vissen",
    ]
    teken_nr = int(lon / 30)
    graad = lon % 30
    return round(lon, 2), f"{tekens[teken_nr]} {graad:.1f}"


@dataclass
class PlanetairVeld:
    datum: date
    saturn_elongatie: float = 0.0
    saturn_afstand_au: float = 0.0
    saturn_positie: str = ""
    saturn_snelheid: float = 0.0
    saturn_retrograde: bool = False
    saturn_fase: str = ""
    saturn_kachel_actief: bool = False
    mars_elongatie: float = 0.0
    mars_positie: str = ""
    mars_demping_actief: bool = False
    jupiter_elongatie: float = 0.0
    jupiter_positie: str = ""
    jupiter_bescherming_actief: bool = False
    veld_status: str = ""
    risico_niveau: str = ""


def bereken_planetair_veld(datum: date = None) -> PlanetairVeld:
    if datum is None:
        datum = date.today()

    veld = PlanetairVeld(datum=datum)

    veld.saturn_elongatie = bereken_elongatie(swe.SATURN, datum)
    veld.saturn_afstand_au = bereken_afstand_au(swe.SATURN, datum)
    veld.saturn_snelheid = bereken_snelheid(swe.SATURN, datum)
    veld.saturn_retrograde = veld.saturn_snelheid < 0
    _, veld.saturn_positie = bereken_positie(swe.SATURN, datum)

    e = veld.saturn_elongatie
    if e < 30:
        veld.saturn_fase = "conjunctie"
    elif e < 60:
        veld.saturn_fase = "vroeg transit"
    elif e < 90:
        veld.saturn_fase = "kwadratuur"
    elif e < 120:
        veld.saturn_fase = "laat transit"
    elif e < 150:
        veld.saturn_fase = "pre-oppositie"
    else:
        veld.saturn_fase = "oppositie"

    veld.saturn_kachel_actief = e >= 140

    veld.mars_elongatie = bereken_elongatie(swe.MARS, datum)
    _, veld.mars_positie = bereken_positie(swe.MARS, datum)
    veld.mars_demping_actief = veld.mars_elongatie >= 140

    veld.jupiter_elongatie = bereken_elongatie(swe.JUPITER, datum)
    _, veld.jupiter_positie = bereken_positie(swe.JUPITER, datum)
    veld.jupiter_bescherming_actief = veld.jupiter_elongatie >= 150

    if veld.saturn_kachel_actief and not veld.mars_demping_actief:
        veld.veld_status = "verhit"
        veld.risico_niveau = "verhoogd"
    elif veld.saturn_kachel_actief and veld.mars_demping_actief:
        veld.veld_status = "gemengd"
        veld.risico_niveau = "neutraal"
    elif veld.mars_demping_actief and not veld.saturn_kachel_actief:
        veld.veld_status = "gedempt"
        veld.risico_niveau = "laag"
    elif veld.jupiter_bescherming_actief:
        veld.veld_status = "beschermd"
        veld.risico_niveau = "laag"
    else:
        veld.veld_status = "neutraal"
        veld.risico_niveau = "normaal"

    return veld


# ═══════════════════════════════════════════════════════════════════
# PERSOONLIJKE KRUISING
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PersoonlijkeStemData:
    naam: str
    geboortedatum: date
    nataal_saturn_lon: float = 0.0
    nataal_saturn_teken: str = ""
    nataal_saturn_huis: int = 0
    nataal_saturn_digniteit: str = ""
    natale_spanning: float = 0.0
    maximale_druk_planeten: List[str] = field(default_factory=list)
    cardinale_punten: Dict[str, str] = field(default_factory=dict)
    actieve_transits: List[Dict] = field(default_factory=list)
    saturn_transit_nataal: Dict = field(default_factory=dict)
    veld_resonantie: str = ""


def bereken_persoonlijke_data(
    birth_data: dict,
    datum: date = None,
) -> PersoonlijkeStemData:
    if datum is None:
        datum = date.today()

    naam = birth_data.get("naam", "Onbekend")
    geb = date(birth_data["year"], birth_data["month"], birth_data["day"])
    psd = PersoonlijkeStemData(naam=naam, geboortedatum=geb)

    hour = birth_data.get("hour", 12)
    minute = birth_data.get("minute", 0)
    utc_decimal = hour + minute / 60.0
    jd_natal = swe.julday(geb.year, geb.month, geb.day, utc_decimal)

    sat_result = swe.calc_ut(jd_natal, swe.SATURN)
    psd.nataal_saturn_lon = sat_result[0][0]
    tekens = [
        "Ram", "Stier", "Tweelingen", "Kreeft", "Leeuw", "Maagd",
        "Weegschaal", "Schorpioen", "Boogschutter", "Steenbok",
        "Waterman", "Vissen",
    ]
    teken_nr = int(psd.nataal_saturn_lon / 30)
    graad = psd.nataal_saturn_lon % 30
    psd.nataal_saturn_teken = f"{tekens[teken_nr]} {graad:.1f}"

    lat = birth_data.get("lat", 51.68)
    lon = birth_data.get("lon", 5.07)
    houses, ascmc = swe.houses(jd_natal, lat, lon, b'P')

    sat_lon = psd.nataal_saturn_lon
    for h in range(12):
        cusp_start = houses[h]
        cusp_end = houses[(h + 1) % 12]
        if cusp_end < cusp_start:
            if sat_lon >= cusp_start or sat_lon < cusp_end:
                psd.nataal_saturn_huis = h + 1
                break
        elif cusp_start <= sat_lon < cusp_end:
            psd.nataal_saturn_huis = h + 1
            break

    teken_naam = tekens[teken_nr]
    if teken_naam in ["Steenbok", "Waterman"]:
        psd.nataal_saturn_digniteit = "domicile"
    elif teken_naam == "Weegschaal":
        psd.nataal_saturn_digniteit = "exaltatie"
    elif teken_naam in ["Kreeft", "Leeuw"]:
        psd.nataal_saturn_digniteit = "detriment"
    elif teken_naam == "Ram":
        psd.nataal_saturn_digniteit = "val"
    else:
        psd.nataal_saturn_digniteit = "peregrine"

    planeet_ids = {
        "Zon": swe.SUN, "Maan": swe.MOON, "Mercurius": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturnus": swe.SATURN, "Uranus": swe.URANUS, "Neptunus": swe.NEPTUNE,
        "Pluto": swe.PLUTO, "Chiron": swe.CHIRON,
    }

    natale_posities = {}
    for naam_p, pid in planeet_ids.items():
        try:
            pos = swe.calc_ut(jd_natal, pid)[0][0]
            natale_posities[naam_p] = pos
        except Exception:
            pass

    jd_transit = _jd(datum)
    transit_planeten = {
        "Saturn": swe.SATURN, "Chiron": swe.CHIRON,
        "Pluto": swe.PLUTO, "Neptunus": swe.NEPTUNE,
        "Uranus": swe.URANUS, "Jupiter": swe.JUPITER,
    }

    aspect_hoeken = {
        "conjunctie": 0, "sextiel": 60, "vierkant": 90,
        "driehoek": 120, "oppositie": 180,
    }
    orbs = {
        "conjunctie": 3.0, "sextiel": 2.5, "vierkant": 2.5,
        "driehoek": 2.5, "oppositie": 3.0,
    }

    for t_naam, t_id in transit_planeten.items():
        t_lon = swe.calc_ut(jd_transit, t_id)[0][0]
        for n_naam, n_lon in natale_posities.items():
            for asp_naam, asp_hoek in aspect_hoeken.items():
                verschil = abs(t_lon - n_lon)
                if verschil > 180:
                    verschil = 360 - verschil
                orb = abs(verschil - asp_hoek)
                max_orb = orbs[asp_naam]
                if orb <= max_orb:
                    psd.actieve_transits.append({
                        "transit": t_naam,
                        "natal": n_naam,
                        "aspect": asp_naam,
                        "orb": round(orb, 2),
                        "exact": orb < 0.5,
                    })

    transit_saturn_lon = swe.calc_ut(jd_transit, swe.SATURN)[0][0]
    verschil_sat = abs(transit_saturn_lon - psd.nataal_saturn_lon)
    if verschil_sat > 180:
        verschil_sat = 360 - verschil_sat

    psd.saturn_transit_nataal = {
        "verschil_graden": round(verschil_sat, 2),
        "fase": _saturn_cyclus_fase(verschil_sat),
    }

    exacte_transits = [t for t in psd.actieve_transits if t["exact"]]
    zware_transits = [t for t in psd.actieve_transits
                      if t["transit"] in ("Saturn", "Pluto", "Chiron")]

    if len(exacte_transits) >= 3 or len(zware_transits) >= 4:
        psd.veld_resonantie = "hoge activatie"
    elif len(exacte_transits) >= 1 or len(zware_transits) >= 2:
        psd.veld_resonantie = "actief"
    else:
        psd.veld_resonantie = "rustig"

    return psd


def _saturn_cyclus_fase(verschil_graden: float) -> str:
    v = verschil_graden
    if v < 10:
        return "Saturn return (terugkeer)"
    elif v < 45:
        return "na return - opbouwfase"
    elif v < 95:
        return "openend vierkant - crisis in actie"
    elif v < 135:
        return "na vierkant - doorbraak of consolidatie"
    elif v < 185:
        return "oppositie - volledige confrontatie"
    elif v < 225:
        return "na oppositie - oogst of verlies"
    elif v < 275:
        return "sluitend vierkant - loslaten"
    else:
        return "pre-return - afronding"


# ═══════════════════════════════════════════════════════════════════
# SAMENGESTELD DATA-OBJECT
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DyausStemData:
    veld: PlanetairVeld = None
    persoon: PersoonlijkeStemData = None
    bewezen: dict = field(default_factory=dict)
    hypothesen: dict = field(default_factory=dict)
    seizoen: str = ""
    kachel_actief: bool = False
    kachel_beschrijving: str = ""


def bereken_stem_data(
    birth_data: dict,
    datum: date = None,
) -> DyausStemData:
    if datum is None:
        datum = date.today()

    swe.set_ephe_path(_EPHE)

    data = DyausStemData()
    data.veld = bereken_planetair_veld(datum)
    data.persoon = bereken_persoonlijke_data(birth_data, datum)

    data.bewezen = {
        "saturn_gcr": BewezenBevindingen.SATURN_GCR_ACTIVATIE,
        "saturn_seismisch": BewezenBevindingen.SATURN_SEISMISCH,
        "mars_demping": BewezenBevindingen.MARS_DEMPING,
        "jupiter_bescherming": BewezenBevindingen.JUPITER_BESCHERMING,
        "domein": BewezenBevindingen.DOMEIN_SPECIFICITEIT,
        "onafhankelijkheid": BewezenBevindingen.ONAFHANKELIJKHEID,
    }

    data.hypothesen = {
        "seizoen": GewogenHypothesen.SEIZOENSEFFECT,
        "kachel": GewogenHypothesen.KACHEL_MODEL,
        "drempel": GewogenHypothesen.DREMPELGEDRAG,
        "cascade": GewogenHypothesen.CREDO_CASCADE,
        "stilte": GewogenHypothesen.SEISMISCHE_STILTE,
    }

    maand = datum.month
    if maand in (3, 4, 5):
        data.seizoen = "lente"
    elif maand in (6, 7, 8):
        data.seizoen = "zomer"
    elif maand in (9, 10, 11):
        data.seizoen = "herfst"
    else:
        data.seizoen = "winter"

    v = data.veld
    if v.saturn_kachel_actief:
        data.kachel_actief = True
        if v.mars_demping_actief:
            data.kachel_beschrijving = (
                "De kachel brandt, maar Mars dempt het vuur. "
                "Het systeem is warm maar niet oververhit."
            )
        else:
            data.kachel_beschrijving = (
                "De kachel brandt zonder demping. "
                f"Saturn elongatie {v.saturn_elongatie:.0f} - "
                "het systeem is verhit."
            )
    else:
        data.kachel_actief = False
        data.kachel_beschrijving = (
            f"De kachel is uit. Saturn elongatie {v.saturn_elongatie:.0f} - "
            "het systeem is in rustfase."
        )

    return data


# ═══════════════════════════════════════════════════════════════════
# BLOK BOUWERS
# ═══════════════════════════════════════════════════════════════════

def bouw_data_stem_blok(data: DyausStemData) -> str:
    v = data.veld
    p = data.persoon

    lines = []
    lines.append("=== DYAUS DATA-STEM ===\n")
    lines.append(f"DATUM: {v.datum}")
    lines.append(f"SEIZOEN: {data.seizoen}\n")

    lines.append("-- PLANETAIR VELD --")
    lines.append(f"Saturn elongatie: {v.saturn_elongatie:.1f} ({v.saturn_fase})")
    lines.append(f"Saturn positie: {v.saturn_positie}")
    lines.append(f"Saturn afstand: {v.saturn_afstand_au:.3f} AU")
    lines.append(f"Saturn retrograde: {'ja' if v.saturn_retrograde else 'nee'}")
    lines.append(f"Saturn kachel actief: {'JA' if v.saturn_kachel_actief else 'nee'}")
    lines.append("")
    lines.append(f"Mars elongatie: {v.mars_elongatie:.1f} - demping: {'ACTIEF' if v.mars_demping_actief else 'nee'}")
    lines.append(f"Mars positie: {v.mars_positie}")
    lines.append("")
    lines.append(f"Jupiter elongatie: {v.jupiter_elongatie:.1f} - bescherming: {'ACTIEF' if v.jupiter_bescherming_actief else 'nee'}")
    lines.append(f"Jupiter positie: {v.jupiter_positie}")
    lines.append("")
    lines.append(f"VELD-STATUS: {v.veld_status.upper()}")
    lines.append(f"RISICO-NIVEAU: {v.risico_niveau.upper()}")

    lines.append("\n-- BEWEZEN BEVINDINGEN --")
    b = data.bewezen
    lines.append(f"Saturn-oppositie -> +20% M7+ aardbevingen (p={b['saturn_seismisch']['opp_150_plus']['monte_carlo_p']})")
    lines.append(f"Saturn-oppositie -> GCR-activatie (p={b['saturn_gcr']['monte_carlo_p']})")
    lines.append(f"Mars-oppositie -> demping (ratio {b['mars_demping']['mars_opp_ratio']})")
    lines.append(f"Jupiter-oppositie -> beschermend (z={b['jupiter_bescherming']['z_score']})")
    lines.append(f"Domein: fysieke systemen JA, financiele markten NEE")

    if p:
        lines.append(f"\n-- PERSOONLIJK: {p.naam} --")
        lines.append(f"Geboortedatum: {p.geboortedatum}")
        lines.append(f"Natale Saturn: {p.nataal_saturn_teken} (huis {p.nataal_saturn_huis}, {p.nataal_saturn_digniteit})")
        lines.append(f"Saturn-cyclus fase: {p.saturn_transit_nataal.get('fase', '?')}")
        lines.append(f"Veld-resonantie: {p.veld_resonantie.upper()}")

        if p.actieve_transits:
            lines.append(f"\nActieve transits ({len(p.actieve_transits)}):")
            gesorteerd = sorted(p.actieve_transits, key=lambda t: t["orb"])
            for t in gesorteerd[:12]:
                exact_marker = " * EXACT" if t["exact"] else ""
                lines.append(
                    f"  Transit {t['transit']} {t['aspect']} nataal {t['natal']} "
                    f"(orb {t['orb']:.2f}){exact_marker}"
                )

    lines.append(f"\n-- KACHEL-MODEL --")
    lines.append(data.kachel_beschrijving)

    return "\n".join(lines)


def bouw_veld_stem_blok(data: DyausStemData) -> str:
    v = data.veld
    p = data.persoon

    lines = []
    lines.append("=== VELD-DATA ===\n")

    if v.saturn_kachel_actief:
        lines.append("HET VELD IS VERHIT.")
        lines.append(f"Saturn staat op {v.saturn_elongatie:.0f} van de Zon.")
        lines.append("De kachel brandt. Wat al onder spanning stond, voelt het nu.")
    else:
        lines.append("HET VELD IS IN RUSTFASE.")
        lines.append(f"Saturn staat op {v.saturn_elongatie:.0f} - nog niet in de verwarmingszone.")

    if v.mars_demping_actief:
        lines.append("Mars dempt. De hitte wordt getemperd.")
    if v.jupiter_bescherming_actief:
        lines.append("Jupiter beschermt. Er is een buffer.")

    if p:
        lines.append(f"\nPERSOON: {p.naam}")
        lines.append(f"Leeftijd: {(date.today() - p.geboortedatum).days // 365} jaar")
        lines.append(f"Natale Saturn: {p.nataal_saturn_teken}, huis {p.nataal_saturn_huis}")
        lines.append(f"Saturn digniteit: {p.nataal_saturn_digniteit}")
        lines.append(f"Saturn-cyclus: {p.saturn_transit_nataal.get('fase', '?')}")
        lines.append(f"Veld-resonantie: {p.veld_resonantie}")

        exacte = [t for t in p.actieve_transits if t["exact"]]
        zware = [t for t in p.actieve_transits
                 if t["transit"] in ("Saturn", "Pluto", "Chiron", "Neptunus")]

        if exacte:
            lines.append(f"\nEXACTE TRANSITS (binnen 0.5):")
            for t in exacte:
                lines.append(f"  {t['transit']} {t['aspect']} {t['natal']} ({t['orb']:.2f})")

        if zware:
            lines.append(f"\nZWARE TRANSITS:")
            for t in sorted(zware, key=lambda x: x["orb"]):
                lines.append(f"  {t['transit']} {t['aspect']} {t['natal']} ({t['orb']:.2f})")

    if data.seizoen in ("herfst", "winter") and v.saturn_kachel_actief:
        lines.append(f"\nSEIZOEN: {data.seizoen} - historisch sterker (hypothese)")
    elif data.seizoen in ("lente", "zomer") and v.saturn_kachel_actief:
        lines.append(f"\nSEIZOEN: {data.seizoen} - historisch zwakker (hypothese)")

    return "\n".join(lines)
