# Hermetic Oracle System — Unified Daily Synthesizer

Generates a complete daily Hermetic alignment report at **4:20 AM CDT** every morning,
synthesizing three data streams into one authoritative HTML page deployed via GitHub Pages.

---

## What It Synthesizes

| Source | Elements |
|--------|----------|
| **Three-Pillar Architecture** | Sky Geometry (Zenith/Ascendant) · Planetary Hour (Chaldean) · Lunar Mansion (28 Arabic) |
| **Alchemical Math Format** | Esoteric Mathematics · Hermetic Principle · Vowel Chant · Unified Mantra & Meditation |
| **HOS Core** | Convergence Score · Celestial Overrides · Visualization Gateway · Hall of Amenti · Astral Shield · Seal Geometry · Hermetic Formula · Oracle Intelligence Report |

All astronomical data is calculated autonomously using the `ephem` library (San Antonio, TX).  
Narrative sections are synthesized via Groq (`llama-3.3-70b-versatile`).

---

## One-Time Setup (5 minutes)

### 1. Create the GitHub Repository

```bash
# On your machine (or use GitHub.com UI)
git init hermetic-oracle
cd hermetic-oracle
# Copy all files into this directory, then:
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/hermetic-oracle.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main` · Folder: `/docs`
4. Click **Save**

Your Oracle will be live at:  
`https://YOUR_USERNAME.github.io/hermetic-oracle/`

### 3. Add Your Groq API Key

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GROQ_API_KEY`
4. Value: your Groq key (starts with `gsk_`)
5. Click **Add secret**

### 4. Enable GitHub Actions

1. Go to the **Actions** tab in your repo
2. If prompted, click **"I understand my workflows, go ahead and enable them"**

### 5. Test It (Run Manually Now)

1. Go to **Actions** tab
2. Click **Daily Oracle Synthesis** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Watch it run — takes ~30 seconds
5. Visit your GitHub Pages URL when complete

---

## Schedule

The workflow runs at `20 9 * * *` (UTC):

| Season | UTC Cron | Local Time |
|--------|----------|------------|
| CDT (Mar–Nov) | `20 9 * * *` | **4:20 AM CDT** ✓ |
| CST (Nov–Mar) | Change to `20 10 * * *` | **4:20 AM CST** ✓ |

To adjust for winter (CST), edit `.github/workflows/daily_oracle.yml` and change the cron line before November.

---

## Output

- `docs/index.html` — today's Oracle (always current)
- `docs/archive/YYYY-MM-DD.html` — permanent archive of every day

---

## Architecture

```
generate.py          Main script (all calculations + HTML generation)
requirements.txt     ephem · pytz · requests
.github/workflows/
  daily_oracle.yml   Cron job: 4:20 AM → run → commit → push
docs/
  index.html         Generated daily (served by GitHub Pages)
  .nojekyll          Disables Jekyll processing
  archive/           Daily HTML archive
```

## Planetary Hour Calculation

Pre-dawn night hours (before today's sunrise) belong to **yesterday's** planetary cycle —
consistent with the classical Chaldean system where the day begins at sunrise.

At 4:20 AM, the script correctly identifies the current hour ruler from the prior day's sunset,
not from midnight or an arbitrary epoch.

---

## Adjusting the Prompt

The Groq synthesis prompt is in `generate.py` → `build_prompt()`.  
The `SYSTEM_PROMPT` constant sets the base persona.  
All 7 sections can be tuned by editing the corresponding block in `build_prompt()`.

## Adding Session Tracking

Session data from the local HOS (`hos_sessions_v1` localStorage) is not included in this version —
the GitHub Pages output is static. To add session intelligence, consider:
- A separate daily JSON file committed to the repo
- A lightweight Cloudflare Worker as a session endpoint
- Manual annotation in the archive HTML
