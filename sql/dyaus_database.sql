-- ══════════════════════════════════════════════════════════════════
-- DYAUS DATABASE — Supabase schema
-- Gerard Vos / The Rock and the Eagle — Mei 2026
--
-- Draai dit in je Supabase SQL Editor (nieuw project).
-- ══════════════════════════════════════════════════════════════════


-- ────────────────────────────────────────
-- 1. PROFIELEN — personen met geboortedata
-- ────────────────────────────────────────
CREATE TABLE dyaus_profielen (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  naam TEXT NOT NULL,
  email TEXT,
  geboorte_jaar INT,
  geboorte_maand INT,
  geboorte_dag INT,
  geboorte_uur INT DEFAULT 12,
  geboorte_minuut INT DEFAULT 0,
  geboorte_lat FLOAT,
  geboorte_lon FLOAT,
  geboorte_plaats TEXT,
  profiel_key TEXT,              -- link naar CHARTS dict (optioneel)
  zon_element TEXT,              -- fire/earth/air/water
  maan_element TEXT,             -- fire/earth/air/water
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Unieke index op naam+datum om duplicaten te voorkomen
CREATE UNIQUE INDEX idx_profielen_uniek
  ON dyaus_profielen (naam, geboorte_jaar, geboorte_maand, geboorte_dag)
  WHERE naam IS NOT NULL AND geboorte_jaar IS NOT NULL;

-- Index op email voor snelle lookup
CREATE INDEX idx_profielen_email ON dyaus_profielen (email) WHERE email IS NOT NULL;


-- ────────────────────────────────────────
-- 2. SESSIES — gesprekssessies
-- ────────────────────────────────────────
CREATE TABLE dyaus_sessies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sessie_id TEXT UNIQUE NOT NULL,    -- extern ID vanuit frontend
  profiel_id UUID REFERENCES dyaus_profielen(id) ON DELETE SET NULL,
  intake_fase TEXT DEFAULT 'start',
  profiel_compleet BOOLEAN DEFAULT false,
  bron TEXT DEFAULT 'web',           -- web, api, widget
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ────────────────────────────────────────
-- 3. BERICHTEN — chatgeschiedenis
-- ────────────────────────────────────────
CREATE TABLE dyaus_berichten (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sessie_id UUID NOT NULL REFERENCES dyaus_sessies(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  tekst TEXT NOT NULL,
  tokens_gebruikt INT,              -- voor kostentracking
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_berichten_sessie ON dyaus_berichten (sessie_id, created_at);


-- ────────────────────────────────────────
-- 4. OLIE-AANBEVELINGEN — getracked per sessie
-- ────────────────────────────────────────
CREATE TABLE dyaus_olie_aanbevelingen (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profiel_id UUID REFERENCES dyaus_profielen(id) ON DELETE SET NULL,
  sessie_id UUID REFERENCES dyaus_sessies(id) ON DELETE CASCADE,
  olie_naam TEXT NOT NULL,
  element TEXT,                     -- fire/earth/air/water
  trigger_type TEXT,                -- klacht, transit, veld, expliciet
  context TEXT,                     -- welke klacht/trigger leidde hiertoe
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_olie_profiel ON dyaus_olie_aanbevelingen (profiel_id);


-- ────────────────────────────────────────
-- 5. EMAILS — verstuurde levensboeken
-- ────────────────────────────────────────
CREATE TABLE dyaus_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profiel_id UUID REFERENCES dyaus_profielen(id) ON DELETE SET NULL,
  sessie_id UUID REFERENCES dyaus_sessies(id) ON DELETE SET NULL,
  email_adres TEXT NOT NULL,
  type TEXT DEFAULT 'levensboek',   -- levensboek, followup, etc
  status TEXT DEFAULT 'verstuurd',  -- verstuurd, gefaald
  resend_id TEXT,                   -- Resend API response ID
  fout_bericht TEXT,                -- bij gefaald: wat ging mis
  olieen TEXT[],                    -- welke oliën in de email stonden
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_emails_profiel ON dyaus_emails (profiel_id);
CREATE INDEX idx_emails_adres ON dyaus_emails (email_adres);


-- ────────────────────────────────────────
-- 6. ANALYTICS — events voor inzicht
-- ────────────────────────────────────────
CREATE TABLE dyaus_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event TEXT NOT NULL,              -- sessie_start, intake_compleet, lezing,
                                    -- olie_vraag, email_verstuurd, share_whatsapp,
                                    -- share_kopieer, begroeting, gesprek
  sessie_id UUID REFERENCES dyaus_sessies(id) ON DELETE SET NULL,
  profiel_id UUID REFERENCES dyaus_profielen(id) ON DELETE SET NULL,
  metadata JSONB DEFAULT '{}',      -- extra data per event
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_analytics_event ON dyaus_analytics (event, created_at);
CREATE INDEX idx_analytics_sessie ON dyaus_analytics (sessie_id);


-- ────────────────────────────────────────
-- RLS POLICIES — API key (service_role) bypass
-- ────────────────────────────────────────
-- Dyaus API gebruikt de service_role key, dus RLS is niet strikt nodig.
-- Maar voor veiligheid: enable RLS en maak service_role policies.

ALTER TABLE dyaus_profielen ENABLE ROW LEVEL SECURITY;
ALTER TABLE dyaus_sessies ENABLE ROW LEVEL SECURITY;
ALTER TABLE dyaus_berichten ENABLE ROW LEVEL SECURITY;
ALTER TABLE dyaus_olie_aanbevelingen ENABLE ROW LEVEL SECURITY;
ALTER TABLE dyaus_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE dyaus_analytics ENABLE ROW LEVEL SECURITY;

-- Service role kan alles (Railway API draait met service_role key)
CREATE POLICY "service_all" ON dyaus_profielen FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON dyaus_sessies FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON dyaus_berichten FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON dyaus_olie_aanbevelingen FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON dyaus_emails FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON dyaus_analytics FOR ALL TO service_role USING (true) WITH CHECK (true);


-- ────────────────────────────────────────
-- UPDATED_AT TRIGGER
-- ────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_profielen_updated
  BEFORE UPDATE ON dyaus_profielen
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_sessies_updated
  BEFORE UPDATE ON dyaus_sessies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
