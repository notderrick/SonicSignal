# 📡 SonicSignal

**A Sonic Discovery Engine for NYC Concert Enthusiasts**

SonicSignal aggregates concerts from across NYC, surfaces hidden gems using a proprietary curation algorithm, and automatically generates weekly Spotify playlists so you never miss a great show.

## Features

- 🎵 **Unified Concert Feed** — Aggregates Ticketmaster, SeatGeek, and Songkick into one deduplicated stream
- 💎 **Curation Score** — Surfaces rising artists in intimate venues before they blow up
- 🎧 **Monday Morning Briefing** — Auto-generated Spotify playlist of upcoming shows, refreshed weekly
- 🔍 **Smart Filters** — Filter by venue size, date range, and genre
- 📰 **Swiss Indie Design** — High-contrast editorial aesthetic inspired by archival print design

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Backend | FastAPI (Python 3.11+) |
| Database | Cloud Firestore |
| Compute | Cloud Run + Cloud Functions |
| Platform | Google Cloud |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud SDK
- API keys for Ticketmaster, SeatGeek, Songkick, and Spotify

### Local Development

```bash
# Clone the repo
git clone https://github.com/yourusername/sonic-signal.git
cd sonic-signal

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Running with Firestore Emulator

```bash
# Start emulator
gcloud emulators firestore start --port=8080

# In another terminal, set env var
export FIRESTORE_EMULATOR_HOST=localhost:8080

# Then run backend
uvicorn app.main:app --reload
```

## Project Structure

```
sonic-signal/
├── functions/           # Cloud Functions
│   ├── harvester/       # API scrapers
│   ├── deduper/         # Event deduplication
│   ├── enricher/        # Spotify enrichment
│   └── playlister/      # Playlist automation
├── backend/             # FastAPI app
├── frontend/            # React app
├── SPEC.md              # Product specification
├── CLAUDE.md            # Claude Code instructions
└── README.md            # You are here
```

## Documentation

- **[SPEC.md](./SPEC.md)** — Full product specification with architecture, data models, and roadmap
- **[CLAUDE.md](./CLAUDE.md)** — Development guidelines and Claude Code instructions

## Design System

SonicSignal follows a **Swiss Indie** aesthetic: high-impact typography, clean lines, and a print-inspired editorial layout.

**Core Principles:**
- Off-white paper background (`#F9F9F7`)
- Ink black text (`#1A1A1A`)
- Signal green accents (`#2D5A27`)
- No rounded corners, no drop shadows
- Grayscale images that reveal color on hover
- Monospaced "archival stamps" for curation scores

**Typography:**
- Headings: Playfair Display (Serif)
- Body: Inter (Sans-serif)
- Data: JetBrains Mono (Monospace)

See [SPEC.md Section 4](./SPEC.md#4-design-system-swiss-indie) for full design tokens.

## The Curation Score

SonicSignal calculates a "Curation Score" for every show:

```
Score = (100 ÷ Artist Popularity) × (1000 ÷ Venue Capacity)
```

| Score | Category | What It Means |
|-------|----------|---------------|
| < 0.5 | 💎 Gem | Rising star in an intimate room |
| 0.5–5.0 | 🎤 Sweet Spot | Quality show at a mid-sized venue |
| > 5.0 | 🏟️ Blockbuster | Major act at a big venue |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /events` | List events with filters |
| `GET /events/{id}` | Get event details |
| `GET /artists` | List artists |
| `GET /venues` | List venues |
| `GET /genres` | Get genre cloud |

## Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy sonic-signal \
  --source . \
  --region us-east1 \
  --allow-unauthenticated

# Set up scheduled jobs
gcloud scheduler jobs create http daily-harvest \
  --schedule="0 3 * * *" \
  --uri="https://..." \
  --time-zone="America/New_York"
```

## Contributing

1. Check `SPEC.md` for product requirements
2. Read `CLAUDE.md` for code conventions
3. Create a feature branch
4. Submit a PR

## License

MIT

---

Built with 🎵 in NYC
