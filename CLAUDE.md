# CLAUDE.md - SonicSignal Project Instructions

> This file provides context and instructions for Claude Code when working on the SonicSignal project.

## Project Overview

SonicSignal is a concert discovery web app for NYC that aggregates events from multiple APIs, deduplicates them, enriches with Spotify data, and generates weekly playlists. See `SPEC.md` for full product specification.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Frontend:** React + Vite
- **Database:** Cloud Firestore
- **Compute:** Cloud Run (web app), Cloud Functions (scheduled jobs)
- **Cloud:** Google Cloud Platform

## Project Structure

```
sonic-signal/
├── functions/           # Cloud Functions (Python)
│   ├── harvester/       # Fetches from Ticketmaster, SeatGeek, Songkick
│   ├── deduper/         # RapidFuzz-based event merging
│   ├── enricher/        # Spotify metadata enrichment
│   └── playlister/      # Monday morning playlist refresh
├── backend/             # FastAPI application
│   └── app/
│       ├── routers/     # API endpoints
│       ├── models/      # Pydantic models
│       └── services/    # Firestore, Spotify clients
├── frontend/            # React application
│   └── src/
│       ├── components/  # UI components
│       ├── hooks/       # Custom React hooks
│       └── services/    # API client
└── terraform/           # Infrastructure as code (optional)
```

## Code Style & Conventions

### Python (Backend & Functions)

- Use **type hints** for all function signatures
- Use **Pydantic** models for request/response validation
- Use **async/await** for I/O-bound operations (API calls, Firestore)
- Follow **Google Python Style Guide**
- Use `httpx` for HTTP requests (async support)
- Use `loguru` or standard `logging` with structured logs

```python
# Example function signature
async def get_events(
    date_from: datetime,
    date_to: datetime,
    capacity_tier: str | None = None
) -> list[Event]:
    ...
```

### React (Frontend)

- Use **functional components** with hooks
- Use **TypeScript** if possible, otherwise PropTypes
- Use **Tailwind CSS** for styling following the **Swiss Indie** design system
- Component files: PascalCase (`EventCard.jsx`)
- Hook files: camelCase with `use` prefix (`useEvents.js`)

**Design System: Swiss Indie**
- Color palette: Off-white paper (`#F9F9F7`), Ink black (`#1A1A1A`), Signal green (`#2D5A27`)
- Typography: Playfair Display (headings), Inter (body), JetBrains Mono (data/scores)
- **No rounded corners** - Use sharp edges for editorial aesthetic
- **No drop shadows** - Flat, print-inspired hierarchy
- Grayscale images by default, color on hover

```jsx
// Example component structure - Swiss Indie style
export default function EventCard({ event }) {
  return (
    <div className="border-b border-ink hover:bg-gray-100 transition-colors">
      <div className="flex items-center justify-between p-6">
        <div>
          <h3 className="font-serif text-2xl text-ink">{event.artist}</h3>
          <p className="font-sans text-sm text-ink/70">{event.venue}</p>
        </div>
        <span className="font-mono text-xs text-signal">
          SCORE: {event.curation_score.toFixed(2)}
        </span>
      </div>
    </div>
  );
}
```

**Tailwind Config:**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        paper: '#F9F9F7',
        ink: '#1A1A1A',
        signal: '#2D5A27',
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
}
```

### Firestore

- Collection names: lowercase plural (`events`, `artists`, `venues`)
- Document IDs: use deterministic IDs where possible (e.g., `{artist_normalized}_{venue_id}_{date}`)
- Always include `created_at` and `updated_at` timestamps
- Use references for relationships (`artist_id`, `venue_id`)

## Key Implementation Details

### Deduplication Logic

Events are considered duplicates if they match on:
1. **Artist** (normalized name, 90%+ fuzzy match)
2. **Venue** (normalized name or alias match, 85%+ fuzzy match)  
3. **Date** (same calendar day)

Use RapidFuzz with `fuzz.token_sort_ratio` for artist matching.

```python
from rapidfuzz import fuzz

def is_duplicate(event1: Event, event2: Event) -> bool:
    artist_match = fuzz.token_sort_ratio(
        event1.artist_normalized, 
        event2.artist_normalized
    ) >= 90
    
    venue_match = (
        event1.venue_id == event2.venue_id or
        fuzz.token_sort_ratio(event1.venue_name, event2.venue_name) >= 85
    )
    
    date_match = event1.date.date() == event2.date.date()
    
    return artist_match and venue_match and date_match
```

### Curation Score

```python
def calculate_curation_score(artist_popularity: int, venue_capacity: int) -> float:
    """
    Lower score = hidden gem (rising artist, small venue)
    Higher score = mainstream (popular artist, big venue)
    """
    if artist_popularity == 0 or venue_capacity == 0:
        return 0.0
    return (100 / artist_popularity) * (1000 / venue_capacity)
```

### Artist Name Normalization

```python
import re

def normalize_artist_name(name: str) -> str:
    """Normalize artist name for matching."""
    name = name.lower().strip()
    name = re.sub(r'^the\s+', '', name)  # Remove leading "The"
    name = re.sub(r'[^\w\s]', '', name)   # Remove special chars
    name = re.sub(r'\s+', ' ', name)      # Collapse whitespace
    return name
```

## Environment & Secrets

**Never commit secrets.** Use Secret Manager in GCP, or `.env` files locally (gitignored).

Required secrets:
- `TICKETMASTER_API_KEY`
- `SEATGEEK_CLIENT_ID`
- `SEATGEEK_CLIENT_SECRET`
- `SONGKICK_API_KEY`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REFRESH_TOKEN`
- `GCP_PROJECT_ID`

For local development:
```bash
# Create .env file (gitignored)
cp .env.example .env
# Fill in your keys
```

## Common Commands

### Backend

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000

# Run tests
pytest
```

### Frontend

```bash
# Install dependencies
cd frontend && npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

### Cloud Functions

```bash
# Test locally
cd functions/harvester
functions-framework --target=main --debug

# Deploy
gcloud functions deploy harvester \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated
```

### Firestore

```bash
# Start emulator for local dev
gcloud emulators firestore start --port=8080
```

## API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List events with filters |
| GET | `/events/{id}` | Get single event |
| GET | `/artists` | List artists |
| GET | `/artists/{id}` | Get artist with events |
| GET | `/venues` | List venues |
| GET | `/venues/{id}` | Get venue with events |
| GET | `/genres` | Get genre cloud data |

### Query Parameters for `/events`

- `date_from` (ISO date)
- `date_to` (ISO date)
- `capacity_tier` (intimate, club, hall, arena)
- `genre` (string)
- `min_score` / `max_score` (float)
- `limit` / `offset` (pagination)

## Testing Strategy

- **Unit tests:** Pure functions (normalization, scoring, deduplication)
- **Integration tests:** API endpoints with Firestore emulator
- **E2E tests:** Playwright for critical user flows

## Deployment

### Cloud Run (Backend + Frontend)

```bash
# Build and deploy
gcloud run deploy sonic-signal \
  --source . \
  --region us-east1 \
  --allow-unauthenticated
```

### Cloud Functions

Each function deploys independently from its directory.

### Cloud Scheduler

```bash
# Daily harvest at 3 AM EST
gcloud scheduler jobs create http daily-harvest \
  --schedule="0 3 * * *" \
  --uri="https://REGION-PROJECT.cloudfunctions.net/harvester" \
  --time-zone="America/New_York"

# Monday playlist at 8 AM EST
gcloud scheduler jobs create http monday-playlist \
  --schedule="0 8 * * 1" \
  --uri="https://REGION-PROJECT.cloudfunctions.net/playlister" \
  --time-zone="America/New_York"
```

## When Working on This Project

### Starting a New Feature

1. Check `SPEC.md` for requirements
2. Identify which component(s) need changes
3. Write tests first if adding business logic
4. Follow existing patterns in the codebase

### Common Tasks

**"Add a new data source"** → Create new file in `functions/harvester/`, follow existing pattern (ticketmaster.py, seatgeek.py)

**"Add a new filter"** → Update backend router, add Firestore index if needed, update frontend FilterSidebar

**"Change scoring logic"** → Update `calculate_curation_score()` in enricher, may need to reprocess existing events

**"Debug Cloud Function"** → Check Cloud Logging, filter by function name

### Things to Watch Out For

- **Rate limits:** All external APIs have limits. Use caching and backoff.
- **Firestore indexes:** Complex queries need composite indexes. Check console for index suggestions.
- **Cold starts:** First request to Cloud Run/Functions is slow. Consider min instances for user-facing services.
- **Spotify token expiry:** Refresh tokens last ~1 year but access tokens expire in 1 hour. Always refresh before playlist operations.

## Useful Links

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Cloud Functions Python](https://cloud.google.com/functions/docs/writing/write-python-functions)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Ticketmaster Discovery API](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/)
- [SeatGeek API](https://platform.seatgeek.com/)
- [Songkick API](https://www.songkick.com/developer)
