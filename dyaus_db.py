"""
DYAUS DB — Supabase database client voor Dyaus API.
Slaat profielen, sessies, berichten, olie-aanbevelingen, emails en analytics op.

Gerard Vos / The Rock and the Eagle — Mei 2026
"""

import os
from datetime import datetime
from typing import Optional, Dict, List

import requests as http_requests

# ══════════════════════════════════════════════════════════════════
# SUPABASE CONFIGURATIE
# ══════════════════════════════════════════════════════════════════

SUPABASE_URL = os.environ.get("DYAUS_SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("DYAUS_SUPABASE_KEY", "")  # service_role key

_DB_ACTIEF = bool(SUPABASE_URL and SUPABASE_KEY)


def _headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _sb_url(tabel: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{tabel}"


def _sb_get(tabel: str, params: dict = None) -> list:
    """GET request naar Supabase REST API."""
    if not _DB_ACTIEF:
        return []
    try:
        res = http_requests.get(
            _sb_url(tabel),
            headers=_headers(),
            params=params or {},
            timeout=8,
        )
        if res.status_code == 200:
            return res.json()
        print(f"DB GET fout ({tabel}): {res.status_code} — {res.text[:200]}")
    except Exception as e:
        print(f"DB GET exception ({tabel}): {e}")
    return []


def _sb_post(tabel: str, data: dict) -> Optional[dict]:
    """INSERT naar Supabase."""
    if not _DB_ACTIEF:
        return None
    try:
        res = http_requests.post(
            _sb_url(tabel),
            headers=_headers(),
            json=data,
            timeout=8,
        )
        if res.status_code in (200, 201):
            rows = res.json()
            return rows[0] if rows else None
        print(f"DB POST fout ({tabel}): {res.status_code} — {res.text[:200]}")
    except Exception as e:
        print(f"DB POST exception ({tabel}): {e}")
    return None


def _sb_patch(tabel: str, filters: str, data: dict) -> Optional[dict]:
    """UPDATE naar Supabase met query filter."""
    if not _DB_ACTIEF:
        return None
    try:
        url = f"{_sb_url(tabel)}?{filters}"
        res = http_requests.patch(
            url,
            headers=_headers(),
            json=data,
            timeout=8,
        )
        if res.status_code in (200, 204):
            rows = res.json() if res.text else []
            return rows[0] if rows else None
        print(f"DB PATCH fout ({tabel}): {res.status_code} — {res.text[:200]}")
    except Exception as e:
        print(f"DB PATCH exception ({tabel}): {e}")
    return None


def _sb_upsert(tabel: str, data: dict, conflict_cols: str = "") -> Optional[dict]:
    """UPSERT naar Supabase (insert or update)."""
    if not _DB_ACTIEF:
        return None
    try:
        headers = _headers()
        if conflict_cols:
            headers["Prefer"] = f"return=representation,resolution=merge-duplicates"
        res = http_requests.post(
            _sb_url(tabel),
            headers=headers,
            json=data,
            timeout=8,
        )
        if res.status_code in (200, 201):
            rows = res.json()
            return rows[0] if rows else None
        print(f"DB UPSERT fout ({tabel}): {res.status_code} — {res.text[:200]}")
    except Exception as e:
        print(f"DB UPSERT exception ({tabel}): {e}")
    return None


# ══════════════════════════════════════════════════════════════════
# PROFIELEN
# ══════════════════════════════════════════════════════════════════

def zoek_profiel(naam: str, jaar: int = None, maand: int = None, dag: int = None) -> Optional[dict]:
    """Zoek een bestaand profiel op naam + geboortedatum."""
    params = {"naam": f"eq.{naam}"}
    if jaar:
        params["geboorte_jaar"] = f"eq.{jaar}"
    if maand:
        params["geboorte_maand"] = f"eq.{maand}"
    if dag:
        params["geboorte_dag"] = f"eq.{dag}"
    params["limit"] = "1"

    rows = _sb_get("dyaus_profielen", params)
    return rows[0] if rows else None


def zoek_profiel_op_email(email: str) -> Optional[dict]:
    """Zoek profiel op email."""
    rows = _sb_get("dyaus_profielen", {
        "email": f"eq.{email}",
        "limit": "1",
    })
    return rows[0] if rows else None


def sla_profiel_op(birth_data: dict, email: str = None,
                   zon_element: str = None, maan_element: str = None) -> Optional[dict]:
    """Sla profiel op of update bestaand profiel."""
    data = {
        "naam": birth_data.get("naam", "Onbekend"),
        "geboorte_jaar": birth_data.get("year"),
        "geboorte_maand": birth_data.get("month"),
        "geboorte_dag": birth_data.get("day"),
        "geboorte_uur": birth_data.get("hour", 12),
        "geboorte_minuut": birth_data.get("minute", 0),
        "geboorte_lat": birth_data.get("lat"),
        "geboorte_lon": birth_data.get("lon"),
        "geboorte_plaats": birth_data.get("plaats", ""),
        "profiel_key": birth_data.get("profiel_key"),
    }
    if email:
        data["email"] = email
    if zon_element:
        data["zon_element"] = zon_element
    if maan_element:
        data["maan_element"] = maan_element

    # Check of profiel al bestaat
    bestaand = zoek_profiel(
        data["naam"],
        data["geboorte_jaar"],
        data["geboorte_maand"],
        data["geboorte_dag"],
    )
    if bestaand:
        # Update met eventueel nieuwe email/elementen
        update = {}
        if email and not bestaand.get("email"):
            update["email"] = email
        if zon_element:
            update["zon_element"] = zon_element
        if maan_element:
            update["maan_element"] = maan_element
        if update:
            _sb_patch("dyaus_profielen", f"id=eq.{bestaand['id']}", update)
        return bestaand

    return _sb_post("dyaus_profielen", data)


# ══════════════════════════════════════════════════════════════════
# SESSIES
# ══════════════════════════════════════════════════════════════════

def maak_of_haal_sessie(sessie_id: str) -> Optional[dict]:
    """Haal bestaande sessie op of maak een nieuwe aan."""
    rows = _sb_get("dyaus_sessies", {
        "sessie_id": f"eq.{sessie_id}",
        "limit": "1",
    })
    if rows:
        return rows[0]

    return _sb_post("dyaus_sessies", {
        "sessie_id": sessie_id,
        "intake_fase": "start",
        "profiel_compleet": False,
    })


def update_sessie(sessie_id: str, data: dict) -> Optional[dict]:
    """Update sessie velden."""
    return _sb_patch("dyaus_sessies", f"sessie_id=eq.{sessie_id}", data)


def koppel_profiel_aan_sessie(sessie_id: str, profiel_id: str):
    """Koppel een profiel aan een sessie."""
    update_sessie(sessie_id, {
        "profiel_id": profiel_id,
        "profiel_compleet": True,
        "intake_fase": "compleet",
    })


# ══════════════════════════════════════════════════════════════════
# BERICHTEN
# ══════════════════════════════════════════════════════════════════

def sla_bericht_op(sessie_db_id: str, role: str, tekst: str,
                   tokens: int = None) -> Optional[dict]:
    """Sla een bericht op in de database."""
    data = {
        "sessie_id": sessie_db_id,
        "role": role,
        "tekst": tekst,
    }
    if tokens:
        data["tokens_gebruikt"] = tokens
    return _sb_post("dyaus_berichten", data)


def haal_berichten_op(sessie_db_id: str, limiet: int = 20) -> list:
    """Haal berichten op voor een sessie."""
    return _sb_get("dyaus_berichten", {
        "sessie_id": f"eq.{sessie_db_id}",
        "order": "created_at.asc",
        "limit": str(limiet),
    })


# ══════════════════════════════════════════════════════════════════
# OLIE-AANBEVELINGEN
# ══════════════════════════════════════════════════════════════════

def sla_olie_aanbeveling_op(profiel_id: str, sessie_db_id: str,
                            olie_naam: str, element: str = None,
                            trigger_type: str = None, context: str = None):
    """Log een olie-aanbeveling."""
    _sb_post("dyaus_olie_aanbevelingen", {
        "profiel_id": profiel_id,
        "sessie_id": sessie_db_id,
        "olie_naam": olie_naam,
        "element": element,
        "trigger_type": trigger_type,
        "context": context,
    })


def haal_olie_historie(profiel_id: str) -> list:
    """Haal alle olie-aanbevelingen op voor een profiel."""
    return _sb_get("dyaus_olie_aanbevelingen", {
        "profiel_id": f"eq.{profiel_id}",
        "order": "created_at.desc",
        "limit": "50",
    })


# ══════════════════════════════════════════════════════════════════
# EMAILS
# ══════════════════════════════════════════════════════════════════

def log_email(profiel_id: str = None, sessie_db_id: str = None,
              email_adres: str = "", type_email: str = "levensboek",
              status: str = "verstuurd", resend_id: str = None,
              fout_bericht: str = None, olieen: list = None) -> Optional[dict]:
    """Log een verstuurde email."""
    data = {
        "email_adres": email_adres,
        "type": type_email,
        "status": status,
    }
    if profiel_id:
        data["profiel_id"] = profiel_id
    if sessie_db_id:
        data["sessie_id"] = sessie_db_id
    if resend_id:
        data["resend_id"] = resend_id
    if fout_bericht:
        data["fout_bericht"] = fout_bericht
    if olieen:
        data["olieen"] = olieen
    return _sb_post("dyaus_emails", data)


# ══════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════

def log_event(event: str, sessie_db_id: str = None,
              profiel_id: str = None, metadata: dict = None):
    """Log een analytics event."""
    data = {"event": event}
    if sessie_db_id:
        data["sessie_id"] = sessie_db_id
    if profiel_id:
        data["profiel_id"] = profiel_id
    if metadata:
        data["metadata"] = metadata
    _sb_post("dyaus_analytics", data)


# ══════════════════════════════════════════════════════════════════
# STATS / DASHBOARD
# ══════════════════════════════════════════════════════════════════

def tel_profielen() -> int:
    """Tel totaal aantal profielen."""
    rows = _sb_get("dyaus_profielen", {"select": "id", "limit": "0"})
    # Use head request for count ideally; for now return len
    return len(_sb_get("dyaus_profielen", {"select": "id"}))


def tel_sessies_vandaag() -> int:
    """Tel sessies van vandaag."""
    vandaag = datetime.now().strftime("%Y-%m-%d")
    return len(_sb_get("dyaus_sessies", {
        "select": "id",
        "created_at": f"gte.{vandaag}T00:00:00",
    }))


def laatste_emails(limiet: int = 10) -> list:
    """Haal laatste verstuurde emails op."""
    return _sb_get("dyaus_emails", {
        "order": "created_at.desc",
        "limit": str(limiet),
    })


def is_actief() -> bool:
    """Check of de database verbinding geconfigureerd is."""
    return _DB_ACTIEF
