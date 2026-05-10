"""
DYAUS API — Standalone Flask server voor Railway deployment.

Endpoints:
  POST /api/dyaus/chat     — Gesprek met Dyaus
  GET  /api/dyaus/health   — Health check
  GET  /                   — Redirect naar health

Gerard Vos / The Rock and the Eagle — Mei 2026
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from dyaus_bot import dyaus_antwoord

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

    if not sessie_id or not bericht:
        return jsonify({"error": "sessie_id en bericht zijn verplicht"}), 400

    try:
        result = dyaus_antwoord(
            sessie_id=sessie_id,
            bericht=bericht,
            profiel_key=profiel_key,
            profiel_code=profiel_code,
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
