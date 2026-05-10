"""
CLOUD CLIENT — Standalone versie voor Dyaus API deployment.
Alleen Claude (Anthropic) — geen Gemini fallback nodig.
"""

import os
import time

import anthropic

_client_cache = {}


def _get_client():
    """Haal of maak Anthropic client (gecached)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if _client_cache.get("key") != api_key:
        _client_cache.clear()
    if "client" not in _client_cache:
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY niet gevonden. "
                "Stel in als environment variable op Railway."
            )
        _client_cache["client"] = anthropic.Anthropic(api_key=api_key)
        _client_cache["key"] = api_key
    return _client_cache["client"]


def run_cloud_model(
    prompt: str,
    model: str | None = None,
    temperatuur: float = 0.85,
    max_tokens: int = 8192,
    max_pogingen: int = 3,
    system_instruction: str | None = None,
    history: list[dict] | None = None,
    **kwargs,
) -> str:
    """
    Roep Claude API aan met retry logic.

    Args:
        prompt:             Laatste user bericht
        model:              Model naam (default: claude-sonnet-4-20250514)
        temperatuur:        0.0-1.0
        max_tokens:         Maximum output lengte
        max_pogingen:       Aantal retries bij fout
        system_instruction: Optioneel system prompt
        history:            Eerdere berichten als [{"role": ..., "text": ...}]
    """
    if model is None:
        model = "claude-sonnet-4-20250514"

    client = _get_client()
    laatste_fout = None

    for poging in range(max_pogingen):
        try:
            messages = []
            if history:
                for m in history:
                    rol = m["role"]
                    if rol == "model":
                        rol = "assistant"
                    messages.append({"role": rol, "content": m["text"]})

            messages.append({"role": "user", "content": prompt})

            kwargs_api = dict(
                model=model,
                max_tokens=max_tokens,
                temperature=temperatuur,
                messages=messages,
            )
            if system_instruction:
                kwargs_api["system"] = system_instruction

            with client.messages.stream(**kwargs_api) as stream:
                return stream.get_final_text().strip()

        except Exception as e:
            laatste_fout = e
            if poging < max_pogingen - 1:
                wacht = 2 ** poging
                print(f"  Claude fout (poging {poging + 1}/{max_pogingen}): {e}")
                print(f"  Wacht {wacht}s...")
                time.sleep(wacht)

    raise RuntimeError(
        f"Claude mislukt na {max_pogingen} pogingen. Laatste fout: {laatste_fout}"
    )
