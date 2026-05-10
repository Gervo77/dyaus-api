"""
charts.py — Natale dataset voor Dyaus API (standalone).
Kopie van backend/perceptiecoup/charts.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeboorteData:
    naam: str
    jaar: int
    maand: int
    dag: int
    uur_utc: float
    lat: float
    lon: float
    plaats: str
    tijd_lokaal: str
    tijd_betrouwbaar: bool = True
    relatie: str = ""
    notitie: str = ""

    @property
    def uur_lokaal(self) -> float:
        if ":" in self.tijd_lokaal:
            parts = self.tijd_lokaal.split(":")
            return int(parts[0]) + int(parts[1]) / 60.0
        return self.uur_utc + 1.0


# Coordinaten
WAALWIJK = (51.6875, 5.0750)
DEN_BOSCH = (51.6978, 5.3037)
AALST_GLD = (51.8000, 5.2500)
MEEUWEN = (51.7100, 5.0200)

CHARTS: dict[str, GeboorteData] = {

    "gerard": GeboorteData(
        naam="Gerrit Jan Vos",
        jaar=1977, maand=10, dag=19,
        uur_utc=17.55,
        lat=WAALWIJK[0], lon=WAALWIJK[1],
        plaats="Waalwijk",
        tijd_lokaal="18:33",
        relatie="zelf",
    ),

    "moeder": GeboorteData(
        naam="Moeder Vos",
        jaar=1956, maand=11, dag=27,
        uur_utc=14.25,
        lat=AALST_GLD[0], lon=AALST_GLD[1],
        plaats="Aalst (Gelderland)",
        tijd_lokaal="15:15",
        relatie="moeder",
    ),

    "vader": GeboorteData(
        naam="Jakob Korstiaan Vos",
        jaar=1956, maand=4, dag=12,
        uur_utc=12.0,
        lat=WAALWIJK[0], lon=WAALWIJK[1],
        plaats="Waalwijk (regio)",
        tijd_lokaal="onbekend",
        tijd_betrouwbaar=False,
        relatie="vader",
    ),

    "sophia": GeboorteData(
        naam="Sophia Vos",
        jaar=2014, maand=3, dag=2,
        uur_utc=13.7167,
        lat=DEN_BOSCH[0], lon=DEN_BOSCH[1],
        plaats="Den Bosch",
        tijd_lokaal="14:43",
        relatie="dochter",
    ),

    "max": GeboorteData(
        naam="Max Jakob Korstiaan Vos",
        jaar=2017, maand=2, dag=3,
        uur_utc=13.6167,
        lat=DEN_BOSCH[0], lon=DEN_BOSCH[1],
        plaats="Den Bosch",
        tijd_lokaal="14:37",
        relatie="zoon",
    ),

    "jessica": GeboorteData(
        naam="Jessica",
        jaar=1980, maand=6, dag=24,
        uur_utc=13.1333,
        lat=DEN_BOSCH[0], lon=DEN_BOSCH[1],
        plaats="Den Bosch",
        tijd_lokaal="15:08",
        relatie="ex / moeder kinderen",
    ),

    "chantal": GeboorteData(
        naam="Chantal",
        jaar=1979, maand=2, dag=5,
        uur_utc=13.0,
        lat=52.2567, lon=5.2567,
        plaats="Eemnes",
        tijd_lokaal="14:00",
        relatie="astro-avond gast",
    ),
}


def get_chart(key: str) -> GeboorteData:
    k = key.lower()
    if k not in CHARTS:
        raise KeyError(f"Onbekende persoon: {key!r}. Beschikbaar: {list(CHARTS)}")
    return CHARTS[k]


def list_personen() -> list[str]:
    return sorted(CHARTS.keys())
