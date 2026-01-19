# SonicSignal Implementation Plan

> **Status:** Phase 0 - Validation Sprint
> **Last Updated:** January 2026
> **Decisions Made:**
> - Single user initially (may expand later)
> - Weekly harvesting (Sunday 3 AM EST)
> - Unmatched artists: Include in UI, exclude from playlists

---

## Phase 0: Validation Sprint

**Timeline:** Week 1
**Goal:** Prove the data pipeline approach works before building infrastructure

### Tasks

#### 1. Project Setup

- [x] Initialize Git repository
- [x] Push to GitHub (https://github.com/notderrick/sonicsignal)
- [x] Update SPEC.md with phased approach
- [ ] Create validation directory structure
- [ ] Set up Python virtual environment
- [ ] Install core dependencies (httpx, rapidfuzz, spotipy)

#### 2. API Key Setup

- [ ] Register for Ticketmaster API key
- [ ] Register for SeatGeek API credentials
- [ ] Register for Songkick API key
- [ ] Create Spotify Developer app
- [ ] Configure `.env` file with all keys

#### 3. API Exploration Script (`validation/explore_apis.py`)

**Objective:** Fetch 1 week of NYC events from each source

**Tasks:**
- [ ] Implement Ticketmaster fetcher
  - Endpoint: `/discovery/v2/events`
  - Query: `city=New York, NY`, `startDateTime` (next 7 days)
  - Parse response, extract: artist, venue, date, ticket_url
- [ ] Implement SeatGeek fetcher
  - Endpoint: `/2/events`
  - Query: `venue.city=New York`, `datetime_utc.gte` (next 7 days)
  - Extract: performer, venue (with capacity!), datetime
- [ ] Implement Songkick fetcher
  - Endpoint: `/metro_areas/7644/calendar.json` (NYC metro ID)
  - Filter to next 7 days
  - Extract: artist, venue, date
- [ ] Export raw data to `validation/sample_data/raw_events.json`
- [ ] Generate summary report (events per source, overlap analysis)

**Success Criteria:**
- Fetch >100 events from each source
- No rate limit errors
- Data structure is consistent

#### 4. Deduplication POC (`validation/test_dedup.py`)

**Objective:** Test fuzzy matching logic with real data

**Tasks:**
- [ ] Implement artist name normalization
  - Strip "The" prefix
  - Lowercase, remove special chars
  - Collapse whitespace
- [ ] Implement venue name normalization
  - Similar to artist (handle "Music Hall", "Hall", etc.)
- [ ] Implement fuzzy matching with RapidFuzz
  - Artist: 90%+ threshold
  - Venue: 85%+ threshold
  - Date: Exact match (same calendar day)
- [ ] Run on sample data, identify duplicates
- [ ] Export to CSV with columns:
  - Event 1 (source, artist, venue, date)
  - Event 2 (source, artist, venue, date)
  - Artist Match %
  - Venue Match %
  - Confidence (high/medium/low)
- [ ] Manual review: Check 50 duplicate pairs, calculate accuracy

**Success Criteria:**
- >90% accuracy on manual review
- <5% false positives (incorrectly matched)
- Identify edge cases (similar band names, venue aliases)

#### 5. Spotify Match Test (`validation/test_spotify.py`)

**Objective:** Measure Spotify artist match rate

**Tasks:**
- [ ] Extract unique artists from sample data (50-100 artists)
- [ ] Implement Spotify search via `spotipy`
  - Query: artist name
  - Handle pagination if needed
- [ ] Match artists, record:
  - Artist name
  - Spotify ID (if found)
  - Popularity score
  - Genres
  - Match confidence (exact vs fuzzy)
- [ ] Export to CSV: `validation/sample_data/spotify_matches.csv`
- [ ] Calculate metrics:
  - Match rate (%)
  - Average popularity of matched artists
  - Most common genres
  - List unmatched artists for review

**Success Criteria:**
- >70% match rate
- Understand why artists don't match (local bands, misspellings, etc.)

#### 6. Venue Capacity Analysis

**Objective:** Understand venue data quality

**Tasks:**
- [ ] Extract unique venues from sample data
- [ ] Check which sources provide capacity
  - SeatGeek: Usually yes
  - Ticketmaster: Sometimes
  - Songkick: Rarely
- [ ] Create seed list for top 20 NYC venues with manual research:
  - Venue name
  - Capacity
  - Capacity tier (intimate/club/hall/arena)
  - Address
  - Aliases (if known)
- [ ] Save to `validation/sample_data/nyc_venues_seed.csv`

**Success Criteria:**
- Identify top 20 most frequent venues
- Have accurate capacity for at least 15 of them

#### 7. Validation Report

**Objective:** Decision point to proceed or pivot

**Deliverable:** `validation/VALIDATION_REPORT.md` with:
- API fetch success rates
- Sample event counts per source
- Deduplication accuracy metrics
- Spotify match rate and edge cases
- Venue capacity data quality assessment
- **Recommendation:** Proceed to Phase 1 or adjust approach

---

## Phase 1: Data Pipeline Foundation

**Timeline:** Week 2-3
**Goal:** Build production data pipeline on GCP

### Tasks

#### 1. GCP Project Setup

- [ ] Create GCP project: `sonicsignal-prod`
- [ ] Enable APIs:
  - Cloud Firestore
  - Cloud Functions (2nd gen)
  - Cloud Run
  - Secret Manager
  - Cloud Scheduler
  - Cloud Logging
- [ ] Set up billing alerts
- [ ] Install `gcloud` CLI locally
- [ ] Authenticate: `gcloud auth login`

#### 2. Secret Manager Configuration

- [ ] Store API keys in Secret Manager
  - `ticketmaster-api-key`
  - `seatgeek-client-id`
  - `seatgeek-client-secret`
  - `songkick-api-key`
  - `spotify-client-id`
  - `spotify-client-secret`
- [ ] Grant Cloud Functions access to secrets

#### 3. Firestore Schema Implementation

**Collections:**

- [ ] `events` collection
  - Create composite index: `date` (asc) + `curation_score` (desc)
  - Create index: `venue_id` + `date`
  - Create index: `artist_id` + `date`
- [ ] `artists` collection
  - Create index: `normalized_name` (for fuzzy matching)
  - Create index: `spotify_matched` + `popularity`
- [ ] `venues` collection
  - Create index: `capacity_tier`
  - Seed with manual venue list from Phase 0
- [ ] `user_preferences` collection (single doc: `default_user`)

#### 4. Harvester Cloud Function

**Structure:**
```
functions/harvester/
├── main.py              # Entry point
├── ticketmaster.py      # API client
├── seatgeek.py          # API client
├── songkick.py          # API client
├── requirements.txt
└── .env.yaml            # Secret references
```

**Tasks:**
- [ ] Port Phase 0 API fetchers to Cloud Function
- [ ] Add exponential backoff for rate limits
- [ ] Store raw events in Firestore `raw_events` subcollection (for debugging)
- [ ] Add structured logging (Cloud Logging)
- [ ] Deploy function:
  ```bash
  gcloud functions deploy harvester \
    --gen2 \
    --runtime python311 \
    --region us-east1 \
    --trigger-http \
    --entry-point main \
    --set-secrets 'TICKETMASTER_API_KEY=ticketmaster-api-key:latest'
  ```

#### 5. Deduper Cloud Function

**Tasks:**
- [ ] Port Phase 0 deduplication logic
- [ ] Read from `raw_events`, write to `events`
- [ ] Store duplicate confidence scores
- [ ] Flag low-confidence matches for manual review
- [ ] Deploy function (triggered by HTTP or Pub/Sub from harvester)

#### 6. Cloud Scheduler Setup

- [ ] Create weekly harvest job:
  ```bash
  gcloud scheduler jobs create http weekly-harvest \
    --schedule="0 3 * * 0" \
    --uri="https://REGION-PROJECT.cloudfunctions.net/harvester" \
    --time-zone="America/New_York"
  ```
- [ ] Test manual trigger: `gcloud scheduler jobs run weekly-harvest`

#### 7. Monitoring & Logging

- [ ] Set up Cloud Logging dashboard
- [ ] Create alert for function failures
- [ ] Monitor Firestore usage and costs

**Deliverable:** Firestore populated with deduplicated events, running on weekly schedule

---

## Phase 2: Enrichment & Scoring

**Timeline:** Week 3-4
**Goal:** Add Spotify metadata and curation scores

### Tasks

#### 1. Spotify OAuth Setup

- [ ] Implement OAuth flow locally to get refresh token
- [ ] Store refresh token in Secret Manager: `spotify-refresh-token`
- [ ] Test token refresh logic

#### 2. Enricher Cloud Function

**Tasks:**
- [ ] Read events from Firestore (unenriched artists)
- [ ] Search Spotify for artist
- [ ] If matched:
  - Store Spotify ID, popularity, genres, top tracks
  - Set `spotify_matched: true`
- [ ] If not matched:
  - Set `spotify_matched: false`
  - Set default values (popularity: 0, genres: [])
- [ ] Calculate curation score for matched artists:
  ```python
  score = (100 / artist_popularity) * (1000 / venue_capacity)
  ```
- [ ] Update event document with score
- [ ] Deploy function

#### 3. Manual Review Admin Endpoint

**Tasks:**
- [ ] Create FastAPI endpoint: `GET /admin/unmatched-artists`
- [ ] Return list of artists with `spotify_matched: false`
- [ ] Endpoint: `GET /admin/low-confidence-duplicates`
- [ ] Return duplicate pairs with confidence < 95%

#### 4. Backfill Enrichment

- [ ] Run enricher on existing events
- [ ] Verify scores look reasonable

**Deliverable:** Events with curation scores and Spotify metadata

---

## Phase 3: Web Application

**Timeline:** Week 5-6
**Goal:** Production web app with playlist automation

### Tasks

#### 1. FastAPI Backend

**Endpoints:**
- [ ] `GET /events` (with filters: date_from, date_to, capacity_tier, genre, min_score, max_score)
- [ ] `GET /events/{id}`
- [ ] `GET /artists`
- [ ] `GET /artists/{id}`
- [ ] `GET /venues`
- [ ] `GET /genres` (genre cloud data)

**Tasks:**
- [ ] Implement Firestore service layer
- [ ] Add CORS for frontend
- [ ] Implement pagination
- [ ] Add caching (optional)
- [ ] Write tests

#### 2. React Frontend

**Components:**
- [ ] `EventCard` - Display event with artist, venue, date, score
- [ ] `FilterSidebar` - Capacity toggles, date range, genre pills
- [ ] `GenreCloud` - Weighted tag cloud
- [ ] `EventList` - Infinite scroll or pagination

**Tasks:**
- [ ] Set up Vite + React
- [ ] Configure Tailwind CSS (dark mode)
- [ ] Implement API client
- [ ] Build components
- [ ] Add loading states, error handling

#### 3. Single User Preferences

- [ ] Create Firestore doc: `user_preferences/default_user`
- [ ] Store:
  - Preferred capacity tiers
  - Favorite genres
  - Min/max curation score
- [ ] Backend endpoint to read/update preferences

#### 4. Cloud Run Deployment

**Tasks:**
- [ ] Create Dockerfile (multi-stage: backend + frontend)
- [ ] Build and test locally
- [ ] Deploy to Cloud Run:
  ```bash
  gcloud run deploy sonic-signal \
    --source . \
    --region us-east1 \
    --allow-unauthenticated
  ```
- [ ] Configure custom domain (optional)
- [ ] Set min instances to 0 (cold starts acceptable for MVP)

#### 5. Playlist Automation (Playlister Function)

**Tasks:**
- [ ] Query Firestore for top 20 events (next 7 days, user preferences)
- [ ] Filter to `spotify_matched: true` only
- [ ] Fetch top 2 tracks per artist (40 total)
- [ ] Clear existing "SonicSignal Weekly" playlist
- [ ] Add tracks in curation score order
- [ ] Deploy function
- [ ] Set up Cloud Scheduler:
  ```bash
  gcloud scheduler jobs create http monday-playlist \
    --schedule="0 8 * * 1" \
    --uri="https://REGION-PROJECT.cloudfunctions.net/playlister" \
    --time-zone="America/New_York"
  ```

#### 6. Testing & Launch

- [ ] End-to-end test: Browse events, filter, check playlist
- [ ] Monitor for 1 week
- [ ] Fix any bugs
- [ ] Share with friends for feedback

**Deliverable:** Production web app at `https://sonicsignal.run.app` with automated playlists

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Events ingested/week | > 500 | Firestore document count |
| Deduplication accuracy | > 90% | Manual spot-check |
| Spotify match rate | > 70% | Matched / Total artists |
| Playlist update reliability | 100% | Cloud Logging success rate |
| Data freshness | < 7 days | `updated_at` timestamp delta |
| Web app response (p95) | < 1s | Cloud Monitoring latency (acceptable for MVP) |

---

## Next Steps

**Current Status:** Phase 0 not started

**Immediate Actions:**
1. Set up validation directory structure
2. Create Python virtual environment
3. Begin API key registration process
4. Start building `explore_apis.py`

**Questions to Resolve:**
- None at this time (decisions made)

**Risks:**
- API rate limits may be tighter than expected (mitigate with caching)
- Spotify match rate may be <70% (fallback: show unmatched artists anyway)
- Venue capacity data may be sparse (manual seed list as backup)
