"""
DYAUS API — Standalone Flask server voor Railway deployment.

Endpoints:
  POST /api/dyaus/chat         — Gesprek met Dyaus
  POST /api/dyaus/email-lezing — Verstuur lezing per email
  GET  /api/dyaus/health       — Health check
  GET  /                       — Redirect naar health

Gerard Vos / The Rock and the Eagle — Mei 2026
"""

import os
import requests as http_requests
from flask import Flask, request, jsonify
from flask_cors import CORS

from dyaus_bot import dyaus_antwoord
import dyaus_db as db

RESEND_API_KEY = os.environ.get("RESEND_API_KEY_TRATE", "")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "service": "Dyaus API",
        "versie": "1.0.0",
    })


@app.route("/api/dyaus/health")
def health():
    return jsonify({"status": "ok", "service": "dyaus"})


@app.route("/api/dyaus/chat", methods=["POST"])
def dyaus_chat():
    """
    POST JSON:
      {
        "sessie_id": "uuid",
        "bericht": "tekst van gebruiker",
        "profiel_key": "optioneel",
        "profiel_code": "optioneel"
      }
    """
    data = request.get_json(force=True)
    sessie_id = data.get("sessie_id", "")
    bericht = data.get("bericht", "").strip()
    profiel_key = data.get("profiel_key")
    profiel_code = data.get("profiel_code")
    geboortedata = data.get("geboortedata")

    if not sessie_id or not bericht:
        return jsonify({"error": "sessie_id en bericht zijn verplicht"}), 400

    try:
        result = dyaus_antwoord(
            sessie_id=sessie_id,
            bericht=bericht,
            profiel_key=profiel_key,
            profiel_code=profiel_code,
            geboortedata=geboortedata,
        )
        return jsonify(result)
    except Exception as e:
        print(f"Dyaus fout: {e}")
        return jsonify({
            "antwoord": "Er ging iets mis in het veld. Probeer opnieuw.",
            "intake_fase": "error",
            "profiel_compleet": False,
            "naam": "",
        }), 500


@app.route("/api/dyaus/email-lezing", methods=["POST"])
def email_lezing():
    """
    POST JSON:
      {
        "email": "ontvanger@email.com",
        "naam": "naam van persoon",
        "gesprek": "volledige gesprekstekst",
        "olieen": ["pepermunt", "vetiver"]  (optioneel)
      }
    """
    if not RESEND_API_KEY:
        return jsonify({"error": "Email niet geconfigureerd"}), 503

    data = request.get_json(force=True)
    email = data.get("email", "").strip()
    naam = data.get("naam", "Onbekend")
    gesprek = data.get("gesprek", "")
    olieen = data.get("olieen", [])

    if not email or "@" not in email:
        return jsonify({"error": "Geldig e-mailadres vereist"}), 400
    if not gesprek:
        return jsonify({"error": "Geen gesprek om te versturen"}), 400

    # Bouw email HTML
    olie_sectie = ""
    if olieen:
        olie_items = "".join(f"<li>{o.capitalize()}</li>" for o in olieen)
        olie_sectie = f"""
        <div style="margin-top:24px;padding:16px;background:#1a1a25;border-left:3px solid #c9a84c;border-radius:4px;">
          <p style="color:#c9a84c;font-size:14px;margin:0 0 8px 0;font-weight:600;">Oliën die voor jou naar voren kwamen:</p>
          <ul style="color:#e0dcd4;font-size:14px;margin:0;padding-left:20px;">{olie_items}</ul>
          <p style="color:#9a958c;font-size:12px;margin:8px 0 0 0;font-style:italic;">
            Meer weten? Stuur een mailtje naar info@therockandtheeagle.com
          </p>
        </div>"""

    # Gesprek formatteren voor email
    gesprek_html = gesprek.replace("\n", "<br>")

    html_body = f"""
    <div style="max-width:600px;margin:0 auto;background:#0a0a0f;padding:32px;font-family:Georgia,serif;">
      <div style="text-align:center;border-bottom:1px solid rgba(201,168,76,0.2);padding-bottom:20px;margin-bottom:24px;">
        <h1 style="color:#c9a84c;font-size:20px;letter-spacing:3px;margin:0;">⚡ DYAUS</h1>
        <p style="color:#9a958c;font-size:12px;margin:4px 0 0 0;">The Rock &amp; The Eagle</p>
      </div>

      <p style="color:#e0dcd4;font-size:15px;line-height:1.7;">
        {naam},<br><br>
        Hier is het eerste hoofdstuk van je levensboek — je gesprek met het veld.
        Bewaar het. Lees het terug wanneer je lichaam erom vraagt.
      </p>

      <div style="margin-top:24px;padding:20px;background:#12121a;border-radius:6px;border:1px solid rgba(201,168,76,0.1);">
        <p style="color:#e0dcd4;font-size:14px;line-height:1.8;white-space:pre-wrap;">{gesprek_html}</p>
      </div>

      {olie_sectie}

      <div style="margin-top:32px;text-align:center;border-top:1px solid rgba(201,168,76,0.1);padding-top:20px;">
        <p style="color:#9a958c;font-size:11px;margin:0;">
          The Rock &amp; The Eagle — Het veld dat door alles stroomt<br>
          <a href="https://therockandtheeagle.com/dyaus" style="color:#c9a84c;text-decoration:none;">therockandtheeagle.com/dyaus</a>
        </p>
      </div>
    </div>
    """

    # Verstuur via Resend
    try:
        res = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "Dyaus <info@therockandtheeagle.com>",
                "to": [email],
                "subject": f"Je levensboek — Hoofdstuk 1",
                "html": html_body,
            },
            timeout=10,
        )

        if res.status_code in (200, 201):
            print(f"Email verstuurd naar {email}")
            resend_data = res.json() if res.text else {}
            resend_id = resend_data.get("id", "")

            # Update profiel met email + log in database
            profiel = db.zoek_profiel(naam)
            profiel_id = profiel["id"] if profiel else None
            if profiel and not profiel.get("email"):
                db.sla_profiel_op({"naam": naam, "year": profiel.get("geboorte_jaar"),
                                   "month": profiel.get("geboorte_maand"),
                                   "day": profiel.get("geboorte_dag")}, email=email)
            db.log_email(
                profiel_id=profiel_id,
                email_adres=email,
                status="verstuurd",
                resend_id=resend_id,
                olieen=olieen if olieen else None,
            )
            db.log_event("email_verstuurd", profiel_id=profiel_id,
                         metadata={"email": email, "type": "levensboek"})

            return jsonify({"status": "ok", "message": "Email verstuurd"})
        else:
            print(f"Resend fout: {res.status_code} — {res.text}")
            # Log gefaalde email
            db.log_email(email_adres=email, status="gefaald",
                         fout_bericht=f"{res.status_code}: {res.text[:200]}")
            return jsonify({"error": "Email versturen mislukt"}), 500

    except Exception as e:
        print(f"Email fout: {e}")
        db.log_email(email_adres=email, status="gefaald", fout_bericht=str(e)[:200])
        return jsonify({"error": "Email versturen mislukt"}), 500


@app.route("/api/dyaus/stats")
def dyaus_stats():
    """Basisstatistieken voor Dyaus."""
    return jsonify({
        "database_actief": db.is_actief(),
        "profielen_totaal": db.tel_profielen() if db.is_actief() else 0,
        "sessies_vandaag": db.tel_sessies_vandaag() if db.is_actief() else 0,
        "laatste_emails": db.laatste_emails(5) if db.is_actief() else [],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
