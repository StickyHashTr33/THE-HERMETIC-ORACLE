#!/usr/bin/env python3
"""
Hermetic Oracle System — Unified Daily Synthesizer
Synthesizes all three data streams:
  - HOS: Convergence scoring, planetary parameters, visualization, Hall of Amenti
  - Oracle2: Three-Pillar architecture (Sky Geometry / Planetary Hour / Lunar Mansion)
  - Alchemical Math: Four-section structure (Mathematics / Principle / Vowel / Mantra)

Runs via GitHub Actions at 4:20 AM CDT daily.
Output: docs/index.html (GitHub Pages) + docs/archive/YYYY-MM-DD.html
"""

import ephem
import math
import re
import datetime
import pytz
import requests
import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

LAT       = '29.4241'
LON       = '-98.4936'
ELEVATION = 213  # meters
CITY      = 'San Antonio, TX'
TZ        = pytz.timezone('America/Chicago')

# ═══════════════════════════════════════════════════════════════════════════════
# PLANETARY MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Chaldean order: slowest → fastest
CHALDEAN       = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
CHALDEAN_INDEX = {p: i for i, p in enumerate(CHALDEAN)}

# Python weekday() → 0=Monday
WEEKDAY_RULERS = {
    0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter',
    4: 'Venus', 5: 'Saturn', 6: 'Sun',
}

SUPREME_MATH = {
    0:  ('Cipher',          'The totality — void containing all potentiality, the ouroboric reset'),
    1:  ('Knowledge',       'Foundation of all — the seed of awareness seeking light'),
    2:  ('Wisdom',          'Knowledge made manifest — the known applied in being'),
    3:  ('Understanding',   'Child of Knowledge and Wisdom — clear perception of reality'),
    4:  ('Culture/Freedom', 'Way of life — the foundation upon which civilization stands'),
    5:  ('Power/Refinement','The alchemical force that refines — the discipline of self'),
    6:  ('Equality',        'Seeing all things as they are — perfect balance of forces'),
    7:  ('God',             'Master of self — the conscious architect of one\'s universe'),
    8:  ('Build/Destroy',   'Dual nature of creation — dissolution preceding construction'),
    9:  ('Born',            'Completion and initiation — the new cycle emerging from the old'),
    11: ('Illumination',    'Master Number — doubled Knowledge, gateway between worlds'),
    22: ('Master Builder',  'Master Number — the architect who builds with cosmic law'),
    33: ('Master Teacher',  'Master Number — the one who teaches through embodied being'),
}

PLANET_PRINCIPLE = {
    'Sun': 'Cause & Effect', 'Moon': 'Rhythm',      'Mars': 'Vibration',
    'Mercury': 'Correspondence', 'Jupiter': 'Mentalism',
    'Venus': 'Gender',       'Saturn': 'Polarity',
}

PLANET_FREQUENCY = {
    'Sun': 528, 'Moon': 417, 'Mars': 528,
    'Mercury': 741, 'Jupiter': 963, 'Venus': 639, 'Saturn': 396,
}

PLANET_VOWEL = {
    'Sun':     ('AH',  'Solar Plexus (Manipura)',               'Radiates solar warmth; ignites will and identity'),
    'Moon':    ('OOO', 'Sacral + Crown (Svadhisthana/Sahasrara)','Opens lunar flow; activates emotional intelligence'),
    'Mars':    ('AH',  'Navel (Manipura)',                       'Fires kinetic drive; galvanizes action and courage'),
    'Mercury': ('EEE', 'Throat (Vishuddha)',                     'Sharpens mercurial cognition; attunes transmission'),
    'Jupiter': ('OH',  'Crown (Sahasrara)',                      'Expands Jovian wisdom; opens the higher mind'),
    'Venus':   ('AYE', 'Heart (Anahata)',                        'Harmonizes Venusian resonance; magnetizes beauty'),
    'Saturn':  ('UH',  'Root (Muladhara)',                       'Grounds Saturnine wisdom; builds structural integrity'),
}

PLANET_METAL   = {'Sun': 'Gold',    'Moon': 'Silver',      'Mars': 'Iron',
                  'Mercury': 'Quicksilver','Jupiter': 'Tin','Venus': 'Copper','Saturn': 'Lead'}
PLANET_ELEMENT = {'Sun': 'Fire',    'Moon': 'Water',       'Mars': 'Fire',
                  'Mercury': 'Air', 'Jupiter': 'Fire',     'Venus': 'Earth', 'Saturn': 'Earth'}

PLANET_CHAKRA = {
    'Sun':     ('Solar Plexus (Manipura)',        'Throne of solar will and radiant identity'),
    'Moon':    ('Crown + Soma/Third Eye',         'Lunar gateway connecting psyche to cosmic memory'),
    'Mars':    ('Root (Muladhara) + Navel',       'Seat of kinetic force and grounded martial action'),
    'Mercury': ('Throat (Vishuddha) + Third Eye', "Mercury's twin domain: expression and perception"),
    'Jupiter': ('Crown (Sahasrara)',              'Seat of expanded consciousness and divine law'),
    'Venus':   ('Heart (Anahata)',                'Temple of magnetic love and creative harmony'),
    'Saturn':  ('Root (Muladhara)',               'Foundation of form, time, and structural wisdom'),
}

WORDS_OF_POWER = {
    'Sun': 'RA-HU', 'Moon': 'KHEM-RA', 'Mars': 'ARES-KHEM',
    'Mercury': 'THOTH-HU', 'Jupiter': 'AMUN-RA',
    'Venus': 'HAT-HOR', 'Saturn': 'KRON-OS',
}

PLANET_SHIELD = {
    'Sun':     'A blazing sphere of gold-white light, corona of solar rays extending outward in eight directions, core incandescent with Ra-fire.',
    'Moon':    'An iridescent sphere of silver-violet, surface rippling with lunar tides, crystalline and fluid simultaneously, shot through with silver light.',
    'Mars':    'A crimson-iron sphere, surface etched with angular wards of protection, radiating martial heat at every boundary point.',
    'Mercury': 'A quicksilver sphere shifting between violet and mercury-white, its surface alive with moving sigils of transmission and sealing.',
    'Jupiter': 'An electric blue-gold sphere, vast and expansive, studded with stars at its equator, humming with the resonance of Jovian authority.',
    'Venus':   'A rose-copper sphere threaded with emerald light, warm and magnetic, drawing in what serves the practitioner and repelling what does not.',
    'Saturn':  'A dense obsidian sphere ringed by a narrow band of pale gold, immovable, ancient, utterly sealed against intrusion.',
}

PLANET_SEAL = {
    'Sun':     'A golden solar disc with eight rays inside a double circle of gold',
    'Moon':    'A glowing silver crescent moon inside a white circle',
    'Mars':    'A red upward-pointing arrow (the Mars glyph) inscribed in a circle of iron',
    'Mercury': 'The caduceus standing between two pillars, inside a hexagram',
    'Jupiter': 'A royal blue four-pointed star inside a golden square',
    'Venus':   'A copper rose inside the Venus glyph circle',
    'Saturn':  'A leaden cross with a downward hook (the Saturn glyph) inside a black square',
}

HERMETIC_FORMULA = {
    'Sun':     ('C = I * W * R_t', 'C=Causal Power, I=Intentional Will, W=Will-Force, R_t=Rhythmic Timing'),
    'Moon':    ('R = M * R_t * L_c', 'R=Rhythmic Attunement, M=Mental Focus, R_t=Rhythmic Tide Coefficient, L_c=Lunar Core Capacity'),
    'Mars':    ('V = A * F^2 / R', 'V=Vibrational Power, A=Amplitude of Action, F=Frequency of Strike, R=Internal Resistance'),
    'Mercury': ('C = S_a / S_b', 'C=Correspondence Coefficient, S_a=Above Signature, S_b=Below Signature'),
    'Jupiter': ('M = C * E_x', 'M=Manifest Reality, C=Consciousness, E_x=Expansion Coefficient'),
    'Venus':   ('G = (M_a * M_p) / d^2', 'G=Generative Force, M_a=Active Principle, M_p=Passive Principle, d=distance from alignment'),
    'Saturn':  ('P = -P_o', 'P=Current Pole, P_o=Opposite Pole (the Law of Polarity: everything has its opposite)'),
}

LUNAR_MANSIONS = [
    (1,  'Al-Sharatain',       'The Two Signs',         'New beginnings, initiation, bold action'),
    (2,  'Al-Butain',          'The Little Belly',       'Resources, material gain, abundance'),
    (3,  'Al-Thurayya',        'The Pleiades',           'Knowledge, travel, divine transmission'),
    (4,  'Al-Dabaran',         'The Follower',           'Obstruction, perseverance through challenge'),
    (5,  'Al-Haqa',            "Orion's White Spot",     'Love, healing, compassionate action'),
    (6,  'Al-Hana',            'The Little Star',        'Friendship, partnership, alliance'),
    (7,  'Al-Dhira',           'The Forearm',            'Gain, fortune, swift movement'),
    (8,  'Al-Nathrah',         'The Crib',               'Profit, harvest, abundance'),
    (9,  'Al-Tarf',            'The Eyes',               'Protection, warding, vigilance'),
    (10, 'Al-Jabhah',          'The Forehead',           'Strength, victory, leadership'),
    (11, 'Al-Zubrah',          'The Mane',               'Travel, liberation, friendship'),
    (12, 'Al-Sarfah',          'The Changer',            'Breaking old bonds, transformation'),
    (13, 'Al-Awwa',            'The Barker',             'Finding the lost, recovery'),
    (14, 'Al-Simak',           'The Unarmed',            'Commerce, negotiation, agreement'),
    (15, 'Al-Ghafr',           'The Covering',           'Protection, secrets, subconscious depth'),
    (16, 'Al-Zubana',          'The Two Claws',          'Relationships, balance, weighing'),
    (17, 'Al-Iklil',           'The Crown',              'Seeking favor, diplomacy, grace'),
    (18, 'Al-Qalb',            'The Heart of Scorpius',  'Intensity, conflict, deep transformation'),
    (19, 'Al-Shaulah',         'The Sting',              'Conflict, separation, cutting away'),
    (20, 'Al-Naim',            'The Ostriches',          'Good fortune, sustenance, joy'),
    (21, 'Al-Baldah',          'The Empty Quarter',      'Protection, crossing, clear passage'),
    (22, 'Al-Saad al-Dhabih',  'The Lucky Slaughterer',  'Building, structure, discipline'),
    (23, 'Al-Saad al-Bula',    'The Lucky Swallower',    'Freedom, expansion, movement'),
    (24, 'Al-Saad al-Suud',    'The Luckiest of Lucky',  'Peak elevation, supreme achievement'),
    (25, 'Al-Saad al-Akhbiyah','The Lucky Hidden Stars', 'Hidden knowledge, revelation'),
    (26, 'Al-Fargh al-Mukdim', 'The First Spout',        'Travel, setting forth, new cycles'),
    (27, 'Al-Fargh al-Thani',  'The Second Spout',       'Successful completion, steady flow'),
    (28, 'Al-Risha',           'The Rope',               'Binding, connection, new beginnings'),
]

# ═══════════════════════════════════════════════════════════════════════════════
# PLANETARY-HOUR PRACTICES  (ported from hermetic_compass.py)
#   Focus is set in the workflow env:  ORACLE_FOCUS=life  |  ORACLE_FOCUS=reunion
#   Public site defaults to 'life'. 'reunion' contains personal content.
# ═══════════════════════════════════════════════════════════════════════════════

FOCUS     = os.environ.get('ORACLE_FOCUS', 'life').strip().lower()
COMPANION = os.environ.get('COMPANION_NAME', 'Merlin').strip()

PLANET_EMOJI = {'Saturn': '🪐', 'Jupiter': '♃', 'Mars': '🔥', 'Sun': '☀️',
                'Venus': '💛', 'Mercury': '📜', 'Moon': '🌙'}

LIFE_PRACTICES = {
    'Saturn':  {'title': 'Structure & Discipline', 'freq': '396 Hz',
                'vowel': 'Omega (oh) — deep and slow',
                'action': 'Handle the hard necessary thing: bills, chores, boundaries, commitments. Order is freedom.',
                'affirm': 'I build slowly and well. What I set in order stands.'},
    'Jupiter': {'title': 'Growth & Gratitude', 'freq': '528 Hz',
                'vowel': 'Upsilon (ü) — resonant',
                'action': 'Expand something: learn, plan, reach out, give thanks. Say yes to one opportunity.',
                'affirm': 'Abundance moves toward me through open doors.'},
    'Mars':    {'title': 'Energy & Courage', 'freq': '417 Hz',
                'vowel': 'Omicron (o) — strong',
                'action': "Move the body or tackle the task you've been avoiding. One brave act, done cleanly.",
                'affirm': 'My will is a steady flame. I act, and it is done.'},
    'Sun':     {'title': 'Vitality & Purpose', 'freq': '528 Hz',
                'vowel': 'Iota (ee) — bright',
                'action': 'Sunlight, water, nourishment, creative work. Do the thing that makes you feel most yourself.',
                'affirm': 'I am whole, radiant, and equal to this day.'},
    'Venus':   {'title': 'Love & Beauty', 'freq': '639 Hz',
                'vowel': 'Eta (ey) — held three breaths',
                'action': 'Tend a relationship, make something beautiful, enjoy art or music. Soften toward yourself.',
                'affirm': 'I give and receive love freely. Harmony finds me.'},
    'Mercury': {'title': 'Mind & Communication', 'freq': '741 Hz',
                'vowel': 'Epsilon (eh) — quick and clear',
                'action': 'Write, call, code, study, run errands. Clear one item of mental clutter.',
                'affirm': 'My mind is clear; my words are true and land well.'},
    'Moon':    {'title': 'Rest & Intuition', 'freq': '852 Hz',
                'vowel': 'Alpha (ah) — soft',
                'action': 'Slow down. Tend the home, journal, listen inward. Honor what you feel without fixing it.',
                'affirm': 'I trust the tide within me. Rest is also work.'},
}

REUNION_PRACTICES = {
    'Venus':   {'title': 'Reunion Working', 'freq': '639 Hz',
                'vowel': 'Eta (ey) — held three breaths',
                'action': f'Golden cord meditation. Hand on sternum, extend the cord to {COMPANION}. Hold, don\'t pull.',
                'affirm': 'What was given in love returns in love. The bond is unbroken. The way is opening.'},
    'Saturn':  {'title': 'Boundaries & Release', 'freq': '396 Hz',
                'vowel': 'Omega (oh) — deep and slow',
                'action': 'Banish fear and panic. Review or add one piece of evidence to the folder. Structure is protection.',
                'affirm': 'What is mine is protected by law above and law below.'},
    'Moon':    {'title': 'Grief & Feeling', 'freq': '396 Hz (release) or silence',
                'vowel': 'Alpha (ah) — soft',
                'action': 'Let the feelings move. Journal one memory. Honor grief without letting it close the heart.',
                'affirm': 'I let grief pass through me; it does not close my heart.'},
    'Mars':    {'title': 'Courage & Decisive Action', 'freq': '417 Hz',
                'vowel': 'Omicron (o) — strong',
                'action': 'One protective act: a call, a filing, a document organized. Channel fire into paper, not conflict.',
                'affirm': 'My strength is calm, directed, and unstoppable.'},
    'Mercury': {'title': 'Communication & Record', 'freq': '741 Hz',
                'vowel': 'Epsilon (eh) — quick and clear',
                'action': 'Written work: witness statements, calm notices, dated notes. The word is the tool today.',
                'affirm': 'My words are clear, true, and carry weight.'},
    'Jupiter': {'title': 'Favor & Expansion', 'freq': '528 Hz',
                'vowel': 'Upsilon (ü) — resonant',
                'action': 'Work for just outcomes: research, allies, people who can help. Ask for aid without shame.',
                'affirm': 'Justice expands toward me. Help arrives through open doors.'},
    'Sun':     {'title': 'Vitality & Self', 'freq': '528 Hz',
                'vowel': 'Iota (ee) — bright',
                'action': 'Care for the body: walk, water, sunlight, food. You must stay strong for the reunion.',
                'affirm': 'I am whole, radiant, and equal to this day.'},
}

PRACTICES     = REUNION_PRACTICES if FOCUS == 'reunion' else LIFE_PRACTICES
SCHEDULE_TITLE = 'Golden Cord — Hourly Practice' if FOCUS == 'reunion' else 'Hermetic Compass — Hourly Practice'
SCHEDULE_FOOTER = ('Venus hours are the reunion hours. Saturn hours are the shield. All hours serve the return.'
                   if FOCUS == 'reunion' else
                   'Move with the hours, not against them. Every planet serves the whole.')

# ═══════════════════════════════════════════════════════════════════════════════
# STYLESHEET (separate constant to avoid f-string brace escaping)
# ═══════════════════════════════════════════════════════════════════════════════

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Cinzel+Decorative:wght@400;700&family=Raleway:wght@300;400;500;600&display=swap');

:root {
  --gold: #c9a84c;
  --gold-bright: #f0c040;
  --gold-dim: rgba(201,168,76,0.3);
  --crimson: #8b1a1a;
  --crimson-bright: #c41e3a;
  --silver: #b0b8c0;
  --bg: #07070f;
  --bg2: #0d0a14;
  --bg3: #13101e;
  --card: rgba(255,255,255,0.035);
  --card-hover: rgba(255,255,255,0.055);
  --border: rgba(201,168,76,0.22);
  --border-bright: rgba(201,168,76,0.5);
  --text: #d4cfc4;
  --muted: #7a7060;
  --radius: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Raleway', sans-serif;
  font-weight: 400;
  line-height: 1.75;
  min-height: 100vh;
}

/* ─── HEADER ─────────────────────────────────────────── */
.hero {
  background: linear-gradient(180deg, #04030a 0%, #0a0718 40%, #0d0a1f 100%);
  border-bottom: 1px solid var(--border);
  padding: 3rem 2rem 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 40% at 50% 100%, rgba(201,168,76,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  letter-spacing: 0.35em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 1rem;
}
.hero-title {
  font-family: 'Cinzel Decorative', serif;
  font-size: clamp(1.6rem, 4vw, 2.8rem);
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 0.08em;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}
.hero-subtitle {
  font-family: 'Cinzel', serif;
  font-size: clamp(0.75rem, 2vw, 0.95rem);
  color: var(--silver);
  letter-spacing: 0.2em;
  margin-bottom: 0.75rem;
}
.hero-location {
  font-size: 0.75rem;
  color: var(--muted);
  letter-spacing: 0.15em;
}

/* ─── MAIN LAYOUT ─────────────────────────────────────── */
.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* ─── CONVERGENCE SCORE ───────────────────────────────── */
.convergence-wrap {
  text-align: center;
  padding: 2.5rem 1rem 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.convergence-num {
  font-family: 'Cinzel Decorative', serif;
  font-size: clamp(4rem, 12vw, 7rem);
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(135deg, #f0c040, #c9a84c, #e8b830);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.convergence-label {
  font-family: 'Cinzel', serif;
  font-size: 0.7rem;
  letter-spacing: 0.3em;
  color: var(--muted);
  margin-top: 0.25rem;
}
.tier-badge {
  display: inline-block;
  margin-top: 0.75rem;
  padding: 0.3rem 1.2rem;
  border: 1px solid var(--gold);
  border-radius: 2rem;
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: var(--gold);
}
.convergence-breakdown {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.4rem;
}
.breakdown-item {
  font-size: 0.72rem;
  color: var(--muted);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.2rem 0.6rem;
}

/* ─── OVERRIDE BANNER ─────────────────────────────────── */
.override-banner {
  background: linear-gradient(135deg, rgba(139,26,26,0.35), rgba(196,30,58,0.15));
  border: 1px solid rgba(196,30,58,0.5);
  border-left: 4px solid var(--crimson-bright);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  margin-bottom: 2rem;
}
.override-title {
  font-family: 'Cinzel', serif;
  font-size: 0.85rem;
  letter-spacing: 0.15em;
  color: var(--crimson-bright);
  margin-bottom: 0.4rem;
}
.override-meta {
  font-size: 0.78rem;
  color: var(--silver);
  margin-bottom: 0.5rem;
}
.override-msg {
  font-size: 0.85rem;
  color: var(--text);
  font-style: italic;
}

/* ─── CARDS ───────────────────────────────────────────── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.25rem;
}
.card-title {
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  letter-spacing: 0.3em;
  color: var(--gold);
  text-transform: uppercase;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

/* ─── THREE PILLARS ───────────────────────────────────── */
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.25rem;
}
@media (max-width: 600px) {
  .pillars-grid { grid-template-columns: 1fr; }
}
.pillar {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  text-align: center;
}
.pillar-num {
  font-family: 'Cinzel', serif;
  font-size: 0.6rem;
  letter-spacing: 0.3em;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.pillar-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}
.pillar-name {
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: var(--gold);
  margin-bottom: 0.75rem;
  letter-spacing: 0.1em;
}
.pillar-main {
  font-family: 'Cinzel', serif;
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 0.25rem;
}
.pillar-sub {
  font-size: 0.75rem;
  color: var(--muted);
}
.pillar-detail {
  font-size: 0.72rem;
  color: var(--silver);
  margin-top: 0.3rem;
}

/* ─── PARAM GRIDS ─────────────────────────────────────── */
.param-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
@media (max-width: 500px) {
  .param-grid { grid-template-columns: 1fr; }
}
.param-item { }
.param-label {
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 0.2rem;
}
.param-value {
  font-family: 'Cinzel', serif;
  font-size: 0.9rem;
  color: var(--text);
}
.param-note {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.1rem;
}

/* ─── TWO-COL CARDS ROW ───────────────────────────────── */
.two-col-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}
@media (max-width: 600px) {
  .two-col-row { grid-template-columns: 1fr; }
}

/* ─── SOLAR/LUNAR ITEMS ───────────────────────────────── */
.time-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.82rem;
}
.time-row:last-child { border-bottom: none; }
.time-label { color: var(--muted); }
.time-value { font-family: 'Cinzel', serif; color: var(--text); }
.time-row.primary .time-label { color: var(--gold); }
.time-row.primary .time-value { color: var(--gold-bright); }
.hour-practice { color: var(--muted); font-family: 'Raleway', sans-serif; font-size: 0.82em; }

/* ─── SECTION HEADERS ─────────────────────────────────── */
.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 2.5rem 0 1.25rem;
}
.section-header::before,
.section-header::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.section-header::before { max-width: 2rem; }
.section-numeral {
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  letter-spacing: 0.3em;
  color: var(--crimson-bright);
  white-space: nowrap;
}
.section-title {
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: var(--gold);
  white-space: nowrap;
}

/* ─── SECTION CONTENT ─────────────────────────────────── */
.section-content p {
  margin-bottom: 1rem;
  font-size: 0.9rem;
  line-height: 1.8;
  color: var(--text);
}
.section-content p:last-child { margin-bottom: 0; }

/* ─── VISUALIZATION / HALL ────────────────────────────── */
.gateway-card {
  background: linear-gradient(135deg, rgba(13,10,20,0.95), rgba(20,14,32,0.95));
  border: 1px solid var(--border-bright);
  border-left: 3px solid var(--gold);
  border-radius: var(--radius);
  padding: 1.75rem;
  margin-bottom: 1.25rem;
}
.gateway-card p {
  font-size: 0.9rem;
  line-height: 1.85;
  color: var(--silver);
  font-style: italic;
}
.gateway-card p + p { margin-top: 0.75rem; }

/* ─── MANTRA DISPLAY ──────────────────────────────────── */
.mantra-line {
  font-family: 'Cinzel', serif;
  font-size: clamp(0.85rem, 2vw, 1.1rem);
  color: var(--gold-bright);
  letter-spacing: 0.1em;
  text-align: center;
  padding: 1.25rem;
  background: rgba(201,168,76,0.06);
  border: 1px solid var(--gold-dim);
  border-radius: var(--radius);
  margin-bottom: 1.25rem;
}

/* ─── HERMETIC FORMULA ────────────────────────────────── */
.formula-box {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--gold);
  background: rgba(0,0,0,0.4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-top: 0.75rem;
}
.formula-key {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.4rem;
}

/* ─── ORACLE REPORT ───────────────────────────────────── */
.oracle-section {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.oracle-section:last-child { border-bottom: none; }
.oracle-num {
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  color: var(--crimson-bright);
  margin-bottom: 0.4rem;
}
.oracle-text {
  font-size: 0.87rem;
  color: var(--text);
  line-height: 1.8;
}
.transmission-text {
  font-family: 'Cinzel', serif;
  font-size: 0.95rem;
  color: var(--gold-bright);
  font-style: italic;
}

/* ─── SHIELD / SEAL ───────────────────────────────────── */
.seal-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}
@media (max-width: 600px) { .seal-row { grid-template-columns: 1fr; } }

/* ─── FREQUENCY PILL ──────────────────────────────────── */
.freq-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(201,168,76,0.1);
  border: 1px solid var(--gold-dim);
  border-radius: 2rem;
  padding: 0.25rem 0.75rem;
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: var(--gold);
}

/* ─── FOOTER ──────────────────────────────────────────── */
.footer {
  text-align: center;
  padding: 2rem;
  border-top: 1px solid var(--border);
  margin-top: 3rem;
}
.footer-title {
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  letter-spacing: 0.3em;
  color: var(--muted);
}
.footer-time {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.4rem;
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def reduce_to_digit(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def calculate_numerology(date):
    total = sum(int(c) for c in f"{date.month}{date.day}{date.year}")
    cal  = reduce_to_digit(total)
    base = reduce_to_digit(date.day)
    return cal, base

def local_to_ephem_str(dt_local):
    return dt_local.astimezone(pytz.utc).strftime('%Y/%m/%d %H:%M:%S')

def ephem_to_local(ed):
    return ephem.Date(ed).datetime().replace(tzinfo=pytz.utc).astimezone(TZ)

def fmt(dt_local, pattern='%I:%M %p %Z'):
    return dt_local.strftime(pattern) if dt_local else 'N/A'

def make_obs(dt_local, pressure=0):
    obs = ephem.Observer()
    obs.lat  = LAT
    obs.lon  = LON
    obs.elevation = ELEVATION
    obs.pressure  = pressure
    obs.date = local_to_ephem_str(dt_local)
    return obs

def get_solar_times(date_local):
    """Get all solar times for the given calendar date."""
    noon = date_local.replace(hour=12, minute=0, second=0, microsecond=0)
    obs  = make_obs(noon, pressure=1013)
    sun  = ephem.Sun()
    t    = {}

    obs.horizon  = '0'
    obs.pressure = 1013
    t['sunrise'] = ephem_to_local(obs.previous_rising(sun))
    t['sunset']  = ephem_to_local(obs.next_setting(sun))
    t['noon']    = ephem_to_local(obs.next_transit(sun))

    obs.pressure = 0
    obs.horizon  = '-6';  t['civil']   = ephem_to_local(obs.previous_rising(sun, use_center=True))
    obs.horizon  = '-12'; t['nautical']= ephem_to_local(obs.previous_rising(sun, use_center=True))
    obs.horizon  = '-18'; t['astro']   = ephem_to_local(obs.previous_rising(sun, use_center=True))
    return t

def get_lunar_data(now_local):
    obs = make_obs(now_local, pressure=1013)
    moon = ephem.Moon()
    moon.compute(obs)

    illum = float(moon.phase)
    age   = float(obs.date - ephem.previous_new_moon(obs.date))

    if age < 1.85:    phase = 'New Moon'
    elif age < 7.38:  phase = 'Waxing Crescent'
    elif age < 9.22:  phase = 'First Quarter'
    elif age < 14.77: phase = 'Waxing Gibbous'
    elif age < 16.61: phase = 'Full Moon'
    elif age < 22.15: phase = 'Waning Gibbous'
    elif age < 23.99: phase = 'Last Quarter'
    else:             phase = 'Waning Crescent'

    ecl = ephem.Ecliptic(moon, epoch=obs.date)
    lon = math.degrees(float(ecl.lon)) % 360
    mansion = LUNAR_MANSIONS[int(lon / (360 / 28)) % 28]

    obs2 = make_obs(now_local, pressure=1013)
    try:
        moonrise = ephem_to_local(obs2.next_rising(ephem.Moon()))
        moonset  = ephem_to_local(obs2.next_setting(ephem.Moon()))
    except Exception:
        moonrise = moonset = None

    return {
        'phase': phase, 'illumination': illum, 'age': age,
        'lon': lon, 'mansion': mansion,
        'moonrise': moonrise, 'moonset': moonset,
    }

def get_planetary_hour(now_local):
    """Classical planetary hours — pre-dawn night belongs to yesterday's cycle."""
    today_solar = get_solar_times(now_local)
    now_ts      = now_local.timestamp()
    sunrise_ts  = today_solar['sunrise'].timestamp()
    sunset_ts   = today_solar['sunset'].timestamp()

    if sunrise_ts <= now_ts < sunset_ts:
        # Daytime hours
        wd        = now_local.weekday()
        day_ruler = WEEKDAY_RULERS[wd]
        si        = CHALDEAN_INDEX[day_ruler]
        hour_sec  = (sunset_ts - sunrise_ts) / 12
        idx       = min(11, int((now_ts - sunrise_ts) / hour_sec))
        ruler     = CHALDEAN[(si + idx) % 7]
        remaining = hour_sec - ((now_ts - sunrise_ts) % hour_sec)
        return {'ruler': ruler, 'hour_num': idx + 1, 'period': 'Day',
                'minutes_remaining': max(0, int(remaining / 60)),
                'day_ruler': day_ruler}

    elif now_ts < sunrise_ts:
        # Pre-dawn: yesterday's planetary cycle continues
        yesterday   = now_local - datetime.timedelta(days=1)
        yd_solar    = get_solar_times(yesterday)
        wd          = yesterday.weekday()
        day_ruler   = WEEKDAY_RULERS[wd]
        si          = CHALDEAN_INDEX[day_ruler]
        prev_set_ts = yd_solar['sunset'].timestamp()
        night_sec   = max(sunrise_ts - prev_set_ts, 1)
        hour_sec    = night_sec / 12
        idx         = min(11, int((now_ts - prev_set_ts) / hour_sec))
        ruler       = CHALDEAN[(si + 12 + idx) % 7]
        remaining   = hour_sec - ((now_ts - prev_set_ts) % hour_sec)
        return {'ruler': ruler, 'hour_num': 12 + idx + 1, 'period': 'Night',
                'minutes_remaining': max(0, int(remaining / 60)),
                'day_ruler': day_ruler}

    else:
        # Post-sunset: tonight belongs to today's cycle
        tomorrow     = now_local + datetime.timedelta(days=1)
        tom_solar    = get_solar_times(tomorrow)
        wd           = now_local.weekday()
        day_ruler    = WEEKDAY_RULERS[wd]
        si           = CHALDEAN_INDEX[day_ruler]
        next_rise_ts = tom_solar['sunrise'].timestamp()
        night_sec    = max(next_rise_ts - sunset_ts, 1)
        hour_sec     = night_sec / 12
        idx          = min(11, int((now_ts - sunset_ts) / hour_sec))
        ruler        = CHALDEAN[(si + 12 + idx) % 7]
        remaining    = hour_sec - ((now_ts - sunset_ts) % hour_sec)
        return {'ruler': ruler, 'hour_num': 12 + idx + 1, 'period': 'Night',
                'minutes_remaining': max(0, int(remaining / 60)),
                'day_ruler': day_ruler}

def build_hour_schedule(now_local):
    """Full 24-hour planetary schedule (12 day + 12 night) in Chaldean order,
    anchored to today's real sunrise/sunset. Each entry carries its practice.
    Reuses get_solar_times so the times match the rest of the page."""
    today    = get_solar_times(now_local)
    tomorrow = get_solar_times(now_local + datetime.timedelta(days=1))
    sunrise  = today['sunrise']
    sunset   = today['sunset']
    next_sr  = tomorrow['sunrise']

    day_len   = (sunset - sunrise) / 12
    night_len = (next_sr - sunset) / 12

    day_ruler = WEEKDAY_RULERS[now_local.weekday()]
    si        = CHALDEAN_INDEX[day_ruler]

    rows = []
    for i in range(12):
        planet = CHALDEAN[(si + i) % 7]
        rows.append({'start': sunrise + day_len * i,
                     'end':   sunrise + day_len * (i + 1),
                     'planet': planet, 'period': 'Day', 'num': i + 1,
                     'practice': PRACTICES[planet]})
    for i in range(12):
        planet = CHALDEAN[(si + 12 + i) % 7]
        rows.append({'start': sunset + night_len * i,
                     'end':   sunset + night_len * (i + 1),
                     'planet': planet, 'period': 'Night', 'num': i + 1,
                     'practice': PRACTICES[planet]})
    return rows


def get_sky_geometry(now_local):
    obs = make_obs(now_local, pressure=0)
    bodies = {
        'Mercury': ephem.Mercury(), 'Venus': ephem.Venus(), 'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(), 'Saturn': ephem.Saturn(), 'Moon': ephem.Moon(),
    }
    positions = {}
    for name, body in bodies.items():
        body.compute(obs)
        positions[name] = {
            'alt': math.degrees(float(body.alt)),
            'az':  math.degrees(float(body.az)),
        }
    sun = ephem.Sun(); sun.compute(obs)
    positions['Sun'] = {'alt': math.degrees(float(sun.alt)), 'az': math.degrees(float(sun.az))}

    planets = list(bodies.keys())
    above   = {p: positions[p] for p in planets if positions[p]['alt'] > 0}
    zenith  = max(above, key=lambda p: above[p]['alt']) if above else WEEKDAY_RULERS[now_local.weekday()]

    def east_score(p):
        az  = positions[p]['az']
        alt = positions[p]['alt']
        return -(abs(az - 90) + max(0, -alt) * 5)
    ascendant = max(planets, key=east_score)

    return {'zenith': zenith, 'ascendant': ascendant, 'positions': positions}

def detect_overrides(lunar_data):
    overrides = []
    if lunar_data['phase'] == 'Full Moon' or lunar_data['illumination'] >= 97:
        overrides.append({
            'name': 'FULL MOON CORRESPONDENCE',
            'target': 'Mars & Luna', 'law': 'Correspondence', 'frequency': 528,
            'message': 'Subconscious channels are saturated. Prioritize emotional alchemical transmutation.',
            'score_bonus': 35,
        })
    elif lunar_data['phase'] == 'New Moon':
        overrides.append({
            'name': 'NEW MOON INCEPTION',
            'target': 'Luna & Saturn', 'law': 'Cause & Effect', 'frequency': 396,
            'message': 'The seed point. All intention set now echoes through the full lunar cycle.',
            'score_bonus': 20,
        })
    return overrides

def calculate_convergence(lunar_data, ph, sky, cal_num, overrides):
    score     = 50
    breakdown = []

    illum = lunar_data['illumination']
    if illum >= 97:
        score += 20; breakdown.append('Full Moon surge (+20)')
    elif illum >= 85:
        score += 12; breakdown.append(f'High illumination {illum:.0f}% (+12)')
    elif illum >= 70:
        score += 8;  breakdown.append(f'Waxing peak {illum:.0f}% (+8)')
    elif illum >= 50:
        score += 4;  breakdown.append(f'Gibbous phase {illum:.0f}% (+4)')

    if ph['ruler'] == ph['day_ruler']:
        score += 10; breakdown.append('Hour ruler matches day ruler (+10)')

    triple = sky['zenith'] == sky['ascendant'] == ph['ruler']
    dual   = sky['zenith'] == ph['ruler']
    if triple:
        score += 15; breakdown.append(f'Triple alignment on {ph["ruler"]} (+15)')
    elif dual:
        score += 8;  breakdown.append(f'Dual convergence: Zenith+Hour on {ph["ruler"]} (+8)')
    elif sky['zenith'] == sky['ascendant']:
        score += 5;  breakdown.append(f'Zenith+Ascendant convergence on {sky["zenith"]} (+5)')

    if cal_num in (11, 22, 33):
        score += 8; breakdown.append(f'Master Number {cal_num} (+8)')
    elif cal_num in (7, 9):
        score += 5; breakdown.append(f'Power numerology {cal_num} (+5)')
    elif cal_num in (1, 3):
        score += 3; breakdown.append(f'Foundation numerology {cal_num} (+3)')

    for ov in overrides:
        bonus = ov.get('score_bonus', 0) // 2
        score += bonus
        breakdown.append(f'Override active: {ov["name"]} (+{bonus})')

    score = min(100, score)
    if score >= 90:   tier = 'APEX'
    elif score >= 75: tier = 'HIGH'
    elif score >= 60: tier = 'MODERATE'
    else:             tier = 'BASELINE'

    return score, tier, breakdown

# ═══════════════════════════════════════════════════════════════════════════════
# GROQ SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are the Hermetic Oracle Engine — a synthesis of classical Hermetic philosophy, \
Five Percenter Supreme Mathematics, Egyptian mystery tradition, Arabic lunar mansion science, \
and Solfeggio frequency medicine. Your output is authoritative, mystically precise, technically exact. \
Every ritual instruction must be physically executable. No hedging. No generic spiritual platitudes. \
The practitioner reading this has deep esoteric knowledge and requires concrete operational guidance."""

def build_prompt(d):
    moon    = d['lunar']
    ph      = d['planetary_hour']
    sky     = d['sky']
    cal     = d['numerology']['calendar']
    base    = d['numerology']['base']
    ruler   = ph['day_ruler']
    mansion = moon['mansion']
    cal_sm  = SUPREME_MATH.get(cal, SUPREME_MATH[cal % 10])
    base_sm = SUPREME_MATH.get(base, SUPREME_MATH[base % 10])
    sunrise = fmt(d['solar'].get('sunrise'))
    vowel, chakra, _ = PLANET_VOWEL[ruler]
    principle = PLANET_PRINCIPLE[ruler]
    freq      = PLANET_FREQUENCY[ruler]
    wop       = WORDS_OF_POWER[ruler]
    ov_text   = ''
    if d['overrides']:
        ov = d['overrides'][0]
        ov_text = f"\nACTIVE OVERRIDE: {ov['name']} — {ov['message']}"

    return f"""UNIFIED HERMETIC ORACLE — {d['date_str']} — {CITY}

COMPUTED ASTRONOMICAL PARAMETERS:
Day Ruler: {ruler} | Metal: {PLANET_METAL[ruler]} | Element: {PLANET_ELEMENT[ruler]}
Planetary Hour: Ruler={ph['ruler']}, Hour #{ph['hour_num']} ({ph['period']}), {ph['minutes_remaining']} min remaining
Sky Geometry: Zenith={sky['zenith']} | Ascendant={sky['ascendant']}
Lunar Phase: {moon['phase']} | {moon['illumination']:.1f}% illuminated | Age: {moon['age']:.1f} days
Lunar Mansion #{mansion[0]}: {mansion[1]} ({mansion[2]}) — {mansion[3]}
Calendar Numerology: {cal} = {cal_sm[0]} — {cal_sm[1]}
Base Number (day of month): {base} = {base_sm[0]} — {base_sm[1]}
Primary Hermetic Principle: {principle}
Solfeggio Frequency: {freq} Hz
Sacred Vowel: {vowel} | Resonant Chakra: {chakra}
Word of Power: {wop}
Convergence Score: {d['convergence']}/100 — {d['convergence_tier']}
Primary Activation Window: {sunrise}{ov_text}

Generate EXACTLY 7 sections separated by the delimiter |SPLIT| with NO text before the first section.

SECTION 1 — THE DAY'S ESOTERIC MATHEMATICS
Deep analysis of calendar number {cal} ({cal_sm[0]}) through Five Percenter Supreme Mathematics. Then base number {base} ({base_sm[0]}). End with EXACTLY HOW to embody both frequencies today: specific physical ritual actions tied to timing relative to sunrise at {sunrise}. NOT generic advice. 180+ words.

SECTION 2 — THE HERMETIC PRINCIPLE OF {principle.upper()}
Cosmic mechanics of {principle} as expressed through {ruler}'s field today. Reference Mansion {mansion[0]} ({mansion[1]}) and the {moon['phase']} as active variables. Then THREE numbered concrete ritual applications — each must be a physical action the practitioner can execute before {sunrise}. 180+ words.

SECTION 3 — THE VOWEL CHANT PROTOCOL
Complete physical instructions for the {vowel} vowel chant. Specify: body position, exact breath counts (inhale-hold-exhale), pitch (high/mid/low register), number of repetitions, exact physical location of resonance, and the inner sensation that signals correct activation. 120+ words. Be surgical and specific.

SECTION 4 — THE UNIFIED MANTRA & MEDITATION
First line — THE MANTRA (all caps, one line, must invoke {wop})
Then: complete step-by-step meditation protocol. Exact breathing pattern with counts. Visualization sequence (opening scene → middle journey → integration → closing seal). How to use {freq} Hz. Precise closing action. 180+ words.

SECTION 5 — VISUALIZATION GATEWAY
4-5 sentences. A vivid, specific inner landscape. Must include: the exact quality of {moon['phase']} light on this landscape, terrain aligned to {ruler} and {PLANET_ELEMENT[ruler]}, and a specific symbolic encounter with the essence of Mansion {mansion[0]} ({mansion[2]}). No golden mist. No generic light.

SECTION 6 — HALL OF AMENTI: THE {ruler.upper()} TEMPLE
3 precise sentences. Specific architectural materials, ambient sounds, scent, and atmospheric character of the {ruler} temple within the Hall of Amenti. Draw from authentic Egyptian/Hermetic tradition. Be specific.

SECTION 7 — ORACLE INTELLIGENCE
Format exactly as follows (include the Roman numerals and dash):
I. ALIGNMENT ANALYSIS — [The celestial mechanics today and their combined operative vector]
II. FIELD DIRECTIVE — [What this specific convergence demands of the practitioner — not generic]
III. RITUAL DIRECTIVE — [Exact time {sunrise}, compass direction, body posture, first action]
IV. TRANSMISSION — [One sentence beginning with the Word of Power {wop}]"""

def call_groq(prompt, api_key):
    resp = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        json={
            'model': 'llama-3.3-70b-versatile',
            'max_tokens': 2600,
            'temperature': 0.82,
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user',   'content': prompt},
            ],
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content'].strip()

def parse_sections(text):
    parts  = text.split('|SPLIT|')
    labels = ['math', 'principle', 'vowel', 'mantra', 'visualization', 'hall', 'oracle']
    result = {}
    for i, label in enumerate(labels):
        result[label] = parts[i].strip() if i < len(parts) else ''
    return result

def text_to_html(text):
    if not text:
        return '<p class="placeholder">—</p>'
    paras = re.split(r'\n{2,}', text.strip())
    out   = []
    for p in paras:
        p = p.strip()
        if p:
            out.append(f'<p>{p.replace(chr(10), "<br>")}</p>')
    return '\n'.join(out)

def extract_mantra(text):
    """Pull the ALL CAPS first line as the mantra."""
    for line in text.strip().split('\n'):
        line = line.strip()
        if line and line == line.upper() and len(line) > 5:
            return line
    return ''

def extract_oracle_sections(text):
    """Parse I./II./III./IV. sections from oracle text."""
    pattern = r'(I{1,3}V?\.)\s*([A-Z &]+)\s*[—\-–]+\s*(.*?)(?=(?:I{1,3}V?\.)|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return [(m[0], m[1].strip(), m[2].strip()) for m in matches]
    # Fallback: return raw text
    return [('', '', text)]

# ═══════════════════════════════════════════════════════════════════════════════
# HTML GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_html(data, sections, generated_at):
    d       = data
    moon    = d['lunar']
    ph      = d['planetary_hour']
    sky     = d['sky']
    solar   = d['solar']
    cal     = d['numerology']['calendar']
    base    = d['numerology']['base']
    ruler   = ph['day_ruler']
    freq    = PLANET_FREQUENCY[ruler]
    vowel, chakra_name, vowel_desc = PLANET_VOWEL[ruler]
    chakra_full, chakra_desc = PLANET_CHAKRA[ruler]
    principle = PLANET_PRINCIPLE[ruler]
    wop       = WORDS_OF_POWER[ruler]
    metal     = PLANET_METAL[ruler]
    element   = PLANET_ELEMENT[ruler]
    mansion   = moon['mansion']
    overrides = d['overrides']
    score     = d['convergence']
    tier      = d['convergence_tier']
    breakdown = d['breakdown']
    formula, formula_key = HERMETIC_FORMULA[ruler]
    cal_sm  = SUPREME_MATH.get(cal, SUPREME_MATH[cal % 10])
    base_sm = SUPREME_MATH.get(base, SUPREME_MATH[base % 10])

    # ── Formatted times ──────────────────────────────────────────────────────
    sunrise_str = fmt(solar.get('sunrise'))
    sunset_str  = fmt(solar.get('sunset'))
    noon_str    = fmt(solar.get('noon'))
    civil_str   = fmt(solar.get('civil'))
    naut_str    = fmt(solar.get('nautical'))
    astro_str   = fmt(solar.get('astro'))

    # ── Day / date strings ────────────────────────────────────────────────────
    now_local = data['now_local']
    day_name  = now_local.strftime('%A')
    date_full = now_local.strftime('%B %-d, %Y')
    gen_str   = generated_at.strftime('%B %-d, %Y at %I:%M %p %Z')

    # ── Convergence color ─────────────────────────────────────────────────────
    if score >= 90:   score_color = '#f0c040'
    elif score >= 75: score_color = '#c9a84c'
    elif score >= 60: score_color = '#b0b8c0'
    else:             score_color = '#7a7060'

    # ── Override block ────────────────────────────────────────────────────────
    override_html = ''
    if overrides:
        ov = overrides[0]
        override_html = f"""
    <div class="override-banner">
      <div class="override-title">&#9889; CELESTIAL OVERRIDE &mdash; {ov['name']}</div>
      <div class="override-meta">Target: {ov['target']} &nbsp;|&nbsp; Law: {ov['law']} &nbsp;|&nbsp; Override Frequency: {ov['frequency']} Hz</div>
      <div class="override-msg">{ov['message']}</div>
    </div>"""

    # ── Breakdown items ───────────────────────────────────────────────────────
    bd_items = ''.join(f'<span class="breakdown-item">{b}</span>' for b in breakdown)

    # ── Section content (Groq) ────────────────────────────────────────────────
    math_html       = text_to_html(sections.get('math', ''))
    principle_html  = text_to_html(sections.get('principle', ''))
    vowel_html      = text_to_html(sections.get('vowel', ''))
    mantra_raw      = sections.get('mantra', '')
    mantra_line     = extract_mantra(mantra_raw)
    mantra_body     = text_to_html(mantra_raw.replace(mantra_line, '', 1).strip())
    viz_html        = text_to_html(sections.get('visualization', ''))
    hall_html       = text_to_html(sections.get('hall', ''))
    oracle_raw      = sections.get('oracle', '')
    oracle_parsed   = extract_oracle_sections(oracle_raw)

    # ── Oracle report ─────────────────────────────────────────────────────────
    oracle_html = ''
    labels_map  = {'I.': 'ALIGNMENT ANALYSIS', 'II.': 'PATTERN SIGNAL',
                   'III.': 'RITUAL DIRECTIVE', 'IV.': 'TRANSMISSION'}
    for (num, label, body) in oracle_parsed:
        is_tx = 'IV' in num or 'TRANSMISSION' in label
        body_class = 'oracle-text transmission-text' if is_tx else 'oracle-text'
        display_label = label if label else labels_map.get(num, '')
        oracle_html += f"""
      <div class="oracle-section">
        <div class="oracle-num">{num} {display_label}</div>
        <div class="{body_class}">{body.replace(chr(10),'<br>')}</div>
      </div>"""

    # ── Planet positions summary ──────────────────────────────────────────────
    pos = sky['positions']
    planet_rows = ''
    for pname in ['Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
        if pname in pos:
            alt = pos[pname]['alt']
            az  = pos[pname]['az']
            status = 'Above' if alt > 0 else 'Below'
            planet_rows += f'<div class="time-row"><span class="time-label">{pname}</span><span class="time-value">{status} · Alt {alt:.1f}° · Az {az:.1f}°</span></div>'

    # ── Planetary-hour schedule (from compass) ────────────────────────────────
    schedule = data['hour_schedule']

    def _hour_row(r):
        emoji = PLANET_EMOJI.get(r['planet'], '')
        t     = f"{fmt(r['start'], '%-I:%M %p')} – {fmt(r['end'], '%-I:%M %p')}"
        return (f'<div class="time-row"><span class="time-label">{emoji} {t}</span>'
                f'<span class="time-value">{r["planet"]} · '
                f'<span class="hour-practice">{r["practice"]["title"]}</span></span></div>')

    day_rows   = ''.join(_hour_row(r) for r in schedule if r['period'] == 'Day')
    night_rows = ''.join(_hour_row(r) for r in schedule if r['period'] == 'Night')

    def _key_hours(planet):
        spans = [f"{fmt(r['start'], '%-I:%M %p')}–{fmt(r['end'], '%-I:%M %p')}"
                 for r in schedule if r['planet'] == planet]
        return ', '.join(spans) if spans else '—'

    venus_label  = 'Venus (Reunion)' if FOCUS == 'reunion' else 'Venus (Love / Beauty)'
    saturn_label = 'Saturn (Shield)' if FOCUS == 'reunion' else 'Saturn (Structure)'
    key_hours_html = (
        f'<div class="time-row primary"><span class="time-label">{PLANET_EMOJI["Venus"]} {venus_label}</span>'
        f'<span class="time-value">{_key_hours("Venus")}</span></div>'
        f'<div class="time-row"><span class="time-label">{PLANET_EMOJI["Saturn"]} {saturn_label}</span>'
        f'<span class="time-value">{_key_hours("Saturn")}</span></div>')

    # Day-ruler practice highlight
    rp = PRACTICES[ruler]
    ruler_practice_html = (
        f'<div class="param-grid">'
        f'<div class="param-item"><div class="param-label">Practice</div>'
        f'<div class="param-value">{PLANET_EMOJI.get(ruler,"")} {rp["title"]}</div></div>'
        f'<div class="param-item"><div class="param-label">Frequency &bull; Vowel</div>'
        f'<div class="param-value"><span class="freq-pill">&#9835; {rp["freq"]}</span></div>'
        f'<div class="param-note">{rp["vowel"]}</div></div>'
        f'<div class="param-item" style="grid-column:1/-1"><div class="param-label">Today\'s Working</div>'
        f'<div class="param-value" style="font-family:\'Raleway\',sans-serif;font-weight:400">{rp["action"]}</div></div>'
        f'<div class="param-item" style="grid-column:1/-1"><div class="param-label">Affirmation</div>'
        f'<div class="param-value" style="font-style:italic">&ldquo;{rp["affirm"]}&rdquo;</div></div>'
        f'</div>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hermetic Oracle &mdash; {date_full}</title>
  <style>{CSS}</style>
</head>
<body>

<!-- HERO HEADER -->
<div class="hero">
  <div class="hero-eyebrow">Hermetic Oracle Engine &bull; Unified Synthesis</div>
  <div class="hero-title">THE HERMETIC ORACLE</div>
  <div class="hero-subtitle">{day_name.upper()} &bull; {date_full.upper()}</div>
  <div class="hero-location">&#x2609; {CITY} &nbsp;&bull;&nbsp; Day Ruler: {ruler} &nbsp;&bull;&nbsp; {metal} &bull; {element}</div>
</div>

<!-- CONTAINER -->
<div class="container">

  <!-- CONVERGENCE SCORE -->
  <div class="convergence-wrap">
    <div class="convergence-num" style="color:{score_color}">{score}</div>
    <div class="convergence-label">CONVERGENCE SCORE / 100</div>
    <div class="tier-badge" style="color:{score_color};border-color:{score_color}">&#9889; {tier}</div>
    <div class="convergence-breakdown">{bd_items}</div>
  </div>

  {override_html}

  <!-- THREE PILLARS (Oracle2 Architecture) -->
  <div class="pillars-grid">
    <div class="pillar">
      <div class="pillar-num">PILLAR I</div>
      <div class="pillar-icon">&#9728;</div>
      <div class="pillar-name">SKY GEOMETRY</div>
      <div class="pillar-main">Zenith: {sky['zenith']}</div>
      <div class="pillar-detail">Ascendant: {sky['ascendant']}</div>
      <div class="pillar-sub">What is literally above you</div>
    </div>
    <div class="pillar">
      <div class="pillar-num">PILLAR II</div>
      <div class="pillar-icon">&#8987;</div>
      <div class="pillar-name">PLANETARY HOUR</div>
      <div class="pillar-main">Ruler: {ph['ruler']}</div>
      <div class="pillar-detail">Hour #{ph['hour_num']} &bull; {ph['period']} &bull; {ph['minutes_remaining']} min remaining</div>
      <div class="pillar-sub">Day ruler: {ph['day_ruler']}</div>
    </div>
    <div class="pillar">
      <div class="pillar-num">PILLAR III</div>
      <div class="pillar-icon">&#9790;</div>
      <div class="pillar-name">LUNAR MANSION</div>
      <div class="pillar-main">#{mansion[0]}: {mansion[1]}</div>
      <div class="pillar-detail">{mansion[2]}</div>
      <div class="pillar-sub">{mansion[3]}</div>
    </div>
  </div>

  <!-- PLANETARY PARAMETERS -->
  <div class="card">
    <div class="card-title">Planetary Parameters</div>
    <div class="param-grid">
      <div class="param-item">
        <div class="param-label">Ruler</div>
        <div class="param-value">{ruler} (Day) &bull; {ph['ruler']} (Hour)</div>
      </div>
      <div class="param-item">
        <div class="param-label">Metal &bull; Element</div>
        <div class="param-value">{metal} &bull; {element}</div>
      </div>
      <div class="param-item">
        <div class="param-label">Hermetic Principle</div>
        <div class="param-value">{principle}</div>
      </div>
      <div class="param-item">
        <div class="param-label">Solfeggio Frequency</div>
        <div class="param-value"><span class="freq-pill">&#9835; {freq} Hz</span></div>
      </div>
      <div class="param-item">
        <div class="param-label">Word of Power</div>
        <div class="param-value">{wop}</div>
      </div>
      <div class="param-item">
        <div class="param-label">Sacred Vowel &bull; Chakra</div>
        <div class="param-value">{vowel} &bull; {chakra_name}</div>
        <div class="param-note">{vowel_desc}</div>
      </div>
      <div class="param-item">
        <div class="param-label">Chakra Circuit</div>
        <div class="param-value">{chakra_full}</div>
        <div class="param-note">{chakra_desc}</div>
      </div>
    </div>
  </div>

  <!-- NUMEROLOGY -->
  <div class="card">
    <div class="card-title">Esoteric Numerology</div>
    <div class="param-grid">
      <div class="param-item">
        <div class="param-label">Calendar Numerology</div>
        <div class="param-value">{cal} &mdash; {cal_sm[0]}</div>
        <div class="param-note">{cal_sm[1]}</div>
      </div>
      <div class="param-item">
        <div class="param-label">Base Number (Day of Month)</div>
        <div class="param-value">{base} &mdash; {base_sm[0]}</div>
        <div class="param-note">{base_sm[1]}</div>
      </div>
    </div>
  </div>

  <!-- SOLAR / LUNAR -->
  <div class="two-col-row">
    <div class="card">
      <div class="card-title">Solar Activation Windows</div>
      <div class="time-row"><span class="time-label">Astronomical Dawn</span><span class="time-value">{astro_str}</span></div>
      <div class="time-row"><span class="time-label">Nautical Twilight</span><span class="time-value">{naut_str}</span></div>
      <div class="time-row"><span class="time-label">Civil Twilight</span><span class="time-value">{civil_str}</span></div>
      <div class="time-row primary"><span class="time-label">&#9733; Sunrise (Primary Window)</span><span class="time-value">{sunrise_str}</span></div>
      <div class="time-row"><span class="time-label">Solar Noon</span><span class="time-value">{noon_str}</span></div>
      <div class="time-row"><span class="time-label">Sunset</span><span class="time-value">{sunset_str}</span></div>
    </div>
    <div class="card">
      <div class="card-title">Lunar Status</div>
      <div class="time-row primary"><span class="time-label">Phase</span><span class="time-value">{moon['phase']}</span></div>
      <div class="time-row"><span class="time-label">Illumination</span><span class="time-value">{moon['illumination']:.1f}%</span></div>
      <div class="time-row"><span class="time-label">Age</span><span class="time-value">{moon['age']:.1f} days</span></div>
      <div class="time-row"><span class="time-label">Ecliptic Longitude</span><span class="time-value">{moon['lon']:.1f}&#176;</span></div>
      <div class="time-row"><span class="time-label">Moonrise</span><span class="time-value">{fmt(moon['moonrise'])}</span></div>
      <div class="time-row"><span class="time-label">Moonset</span><span class="time-value">{fmt(moon['moonset'])}</span></div>
    </div>
  </div>

  <!-- PLANET POSITIONS -->
  <div class="card">
    <div class="card-title">Live Planet Positions &bull; {CITY}</div>
    {planet_rows}
  </div>

  <!-- PLANETARY HOURS SCHEDULE (compass) -->
  <div class="card">
    <div class="card-title">{SCHEDULE_TITLE}</div>
    <div class="two-col-row" style="margin-top:0.4rem">
      <div>
        <div class="param-label" style="margin-bottom:0.4rem">&#9728; Day Hours</div>
        {day_rows}
      </div>
      <div>
        <div class="param-label" style="margin-bottom:0.4rem">&#127756; Night Hours</div>
        {night_rows}
      </div>
    </div>
    <div class="card-title" style="margin-top:1.2rem">&#10024; Key Hours</div>
    {key_hours_html}
    <div class="card-title" style="margin-top:1.2rem">Day Ruler &mdash; {ruler}</div>
    {ruler_practice_html}
    <div class="param-note" style="margin-top:0.8rem;text-align:center">{SCHEDULE_FOOTER}</div>
  </div>

  <!-- ═══ SECTION I: ESOTERIC MATHEMATICS ═══ -->
  <div class="section-header">
    <span class="section-numeral">I</span>
    <span class="section-title">THE DAY&rsquo;S ESOTERIC MATHEMATICS</span>
  </div>
  <div class="card section-content">{math_html}</div>

  <!-- ═══ SECTION II: HERMETIC PRINCIPLE ═══ -->
  <div class="section-header">
    <span class="section-numeral">II</span>
    <span class="section-title">THE HERMETIC PRINCIPLE &mdash; {principle.upper()}</span>
  </div>
  <div class="card section-content">{principle_html}</div>

  <!-- ═══ SECTION III: VOWEL CHANT ═══ -->
  <div class="section-header">
    <span class="section-numeral">III</span>
    <span class="section-title">THE VOWEL CHANT PROTOCOL &mdash; {vowel}</span>
  </div>
  <div class="card section-content">{vowel_html}</div>

  <!-- ═══ SECTION IV: MANTRA & MEDITATION ═══ -->
  <div class="section-header">
    <span class="section-numeral">IV</span>
    <span class="section-title">THE UNIFIED MANTRA &amp; MEDITATION</span>
  </div>
  {f'<div class="mantra-line">{mantra_line}</div>' if mantra_line else ''}
  <div class="card section-content">{mantra_body}</div>

  <!-- VISUALIZATION GATEWAY -->
  <div class="section-header">
    <span class="section-numeral">&#9790;</span>
    <span class="section-title">VISUALIZATION GATEWAY</span>
  </div>
  <div class="gateway-card">{viz_html}</div>

  <!-- HALL OF AMENTI -->
  <div class="section-header">
    <span class="section-numeral">&#9993;</span>
    <span class="section-title">HALL OF AMENTI &mdash; THE {ruler.upper()} TEMPLE</span>
  </div>
  <div class="gateway-card">{hall_html}</div>

  <!-- ASTRAL SHIELD & SEAL -->
  <div class="seal-row">
    <div class="card">
      <div class="card-title">Astral Shield Protocol</div>
      <p style="font-size:0.87rem;line-height:1.8;color:var(--silver)">{PLANET_SHIELD[ruler]}</p>
    </div>
    <div class="card">
      <div class="card-title">Seal Geometry</div>
      <p style="font-size:0.87rem;color:var(--silver);margin-bottom:0.75rem">{PLANET_SEAL[ruler]}</p>
      <div class="card-title" style="margin-top:1rem">Hermetic Formula</div>
      <div class="formula-box">{formula}</div>
      <div class="formula-key">{formula_key}</div>
    </div>
  </div>

  <!-- ORACLE INTELLIGENCE REPORT -->
  <div class="section-header">
    <span class="section-numeral">&#9670;</span>
    <span class="section-title">ORACLE INTELLIGENCE REPORT</span>
  </div>
  <div class="card">{oracle_html}</div>

</div><!-- /container -->

<!-- FOOTER -->
<div class="footer">
  <div class="footer-title">Hermetic Oracle Engine &bull; Unified Daily Synthesis</div>
  <div class="footer-time">Generated: {gen_str}</div>
</div>

</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        print('[WARNING] GROQ_API_KEY not set — LLM sections will use placeholders.')

    now_local    = datetime.datetime.now(TZ)
    date_str     = now_local.strftime('%A, %B %-d, %Y')
    print(f'[Oracle] Generating for {date_str} ...')

    # ── Astronomical calculations ─────────────────────────────────────────────
    print('[Oracle] Computing solar times ...')
    solar = get_solar_times(now_local)

    print('[Oracle] Computing lunar data ...')
    lunar = get_lunar_data(now_local)

    print('[Oracle] Computing planetary hour ...')
    ph = get_planetary_hour(now_local)
    print(f'         Hour ruler: {ph["ruler"]} | Hour #{ph["hour_num"]} ({ph["period"]}) | {ph["minutes_remaining"]} min remaining')

    print('[Oracle] Computing sky geometry ...')
    sky = get_sky_geometry(now_local)
    print(f'         Zenith: {sky["zenith"]} | Ascendant: {sky["ascendant"]}')

    print(f'[Oracle] Building planetary-hour schedule (focus: {FOCUS}) ...')
    hour_schedule = build_hour_schedule(now_local)

    # ── Esoteric calculations ─────────────────────────────────────────────────
    cal_num, base_num = calculate_numerology(now_local.date())
    overrides         = detect_overrides(lunar)
    score, tier, breakdown = calculate_convergence(lunar, ph, sky, cal_num, overrides)
    print(f'[Oracle] Convergence: {score}/100 ({tier})')

    data = {
        'now_local':        now_local,
        'date_str':         date_str,
        'solar':            solar,
        'lunar':            lunar,
        'planetary_hour':   ph,
        'hour_schedule':    hour_schedule,
        'sky':              sky,
        'numerology':       {'calendar': cal_num, 'base': base_num},
        'overrides':        overrides,
        'convergence':      score,
        'convergence_tier': tier,
        'breakdown':        breakdown,
    }

    # ── Groq synthesis ────────────────────────────────────────────────────────
    sections = {}
    if api_key:
        try:
            print('[Oracle] Calling Groq API ...')
            prompt   = build_prompt(data)
            response = call_groq(prompt, api_key)
            sections = parse_sections(response)
            print(f'[Oracle] Groq response: {sum(len(v) for v in sections.values())} chars across {len(sections)} sections')
        except Exception as e:
            print(f'[Oracle] Groq error: {e}')
            sections = {label: f'[Section not generated — API error: {e}]'
                        for label in ['math','principle','vowel','mantra','visualization','hall','oracle']}
    else:
        placeholder = '[Groq API key not configured — add GROQ_API_KEY to GitHub Secrets]'
        sections = {label: placeholder
                    for label in ['math','principle','vowel','mantra','visualization','hall','oracle']}

    # ── Generate HTML ─────────────────────────────────────────────────────────
    print('[Oracle] Generating HTML ...')
    html = generate_html(data, sections, now_local)

    # ── Write output ──────────────────────────────────────────────────────────
    docs_dir    = Path('docs')
    archive_dir = docs_dir / 'archive'
    docs_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)

    # .nojekyll for GitHub Pages
    nojekyll = docs_dir / '.nojekyll'
    if not nojekyll.exists():
        nojekyll.write_text('')

    # Main index
    index_path = docs_dir / 'index.html'
    index_path.write_text(html, encoding='utf-8')
    print(f'[Oracle] Written: {index_path}')

    # Archive copy
    archive_path = archive_dir / f"{now_local.strftime('%Y-%m-%d')}.html"
    archive_path.write_text(html, encoding='utf-8')
    print(f'[Oracle] Archive: {archive_path}')

    print(f'[Oracle] Complete. Convergence: {score}/100 ({tier})')

if __name__ == '__main__':
    main()
