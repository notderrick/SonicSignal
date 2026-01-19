# SonicSignal Product Specification

> **Version:** 1.0  
> **Date:** January 2026  
> **Platform:** Google Cloud Platform  
> **Dev Tools:** Claude Code, Antigravity, Cursor

---

## 1. Executive Summary

SonicSignal is a **Sonic Discovery Engine** that aggregates every concert in New York City, filters them by "vibe" (venue size and artist popularity), and automates weekly listening habits through Spotify integration.

### Problem Statement

NYC has an overwhelming number of live music events across hundreds of venues. Discovering hidden gems—specifically rising artists in intimate venues—requires manually checking multiple platforms (Ticketmaster, SeatGeek, Songkick, DICE, Resident Advisor). Music lovers miss great shows simply because they don't know they exist.

### Solution

A cloud-native web application that:
- Aggregates concert data from multiple sources
- Deduplicates listings using fuzzy matching
- Enriches events with Spotify metadata
- Calculates a proprietary "Curation Score" to surface hidden gems
- Automatically updates a personalized Spotify playlist every Monday morning

---

## 2. System Architecture

SonicSignal is built on Google Cloud Platform using a serverless architecture for automatic scaling, minimal operational overhead, and cost efficiency.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD SCHEDULER                          │
│              (Daily sync + Monday 8am playlist)             │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLOUD FUNCTIONS                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Harvester │  │ Deduper  │  │ Enricher │  │Playlister│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      FIRESTORE                              │
│        (events, artists, venues, user_preferences)          │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLOUD RUN                              │
│              (FastAPI backend + React frontend)             │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Data Ingestion Layer (The Harvesters)

Cloud Functions that collect raw concert data from external APIs on a scheduled basis.

| API Source | Coverage | Primary Use |
|------------|----------|-------------|
| **Ticketmaster** | Arenas, Stadiums | Captures "Big Shows" at major venues |
| **SeatGeek** | Mid-sized venues | Primary source for venue capacity metadata |
| **Songkick** | Small/DIY venues | Aggregates DICE, Eventbrite, RA listings |

### 2.2 Logic Engine (The Brain)

Cloud Functions that process and transform raw data:

- **Normalization:** Converts all dates to ISO-8601 format and strips "The" from artist names for accurate comparison
- **Fuzzy Deduplication:** Uses RapidFuzz library to merge events from different sources into a UnifiedEvent document
- **Curation Scoring:** Calculates a proprietary score for every event to surface hidden gems

### 2.3 Enrichment & Output Layer (The Hands)

- **Spotify API:** Fetches Artist IDs, popularity rankings, genres, and top 3 tracks
- **Firestore:** NoSQL document database storing events, artists, venues, and user preferences
- **Cloud Run Web App:** FastAPI backend with React frontend for browsing and filtering
- **Playlist Automation:** Cloud Function triggered every Monday at 8 AM to refresh the "SonicSignal Weekly" Spotify playlist

---

## 3. Technical Stack

### Core Technologies

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Backend Framework | FastAPI |
| Frontend | React + Vite |
| Database | Cloud Firestore |
| Compute | Cloud Run (web) + Cloud Functions (jobs) |
| Scheduling | Cloud Scheduler |
| Secrets | Secret Manager |

### GCP Services

| Service | Purpose |
|---------|---------|
| **Cloud Run** | Hosts containerized FastAPI + React web app. Scales to zero when idle. |
| **Cloud Functions** | Serverless functions for harvesting, deduplication, enrichment, playlist updates. |
| **Cloud Firestore** | NoSQL database for events, artists, venues, user preferences. Real-time sync capable. |
| **Cloud Scheduler** | Cron-based scheduling for daily data sync and Monday morning playlist updates. |
| **Secret Manager** | Secure storage for API keys and OAuth tokens. |
| **Cloud Logging** | Centralized logging for debugging and monitoring. |

### Python Libraries

| Library | Purpose |
|---------|---------|
| `google-cloud-firestore` | Firestore Python client |
| `functions-framework` | Cloud Functions local development |
| `httpx` | Async HTTP client for API calls |
| `spotipy` | Spotify Web API wrapper |
| `rapidfuzz` | Fuzzy string matching for deduplication |
| `pydantic` | Data validation and settings management |

---

## 4. Core Features

### 4.1 The Curation Score Formula

To help users find "Local/Smaller" acts, the app calculates a score for every show:

```
Score = (100 ÷ Artist Popularity) × (1000 ÷ Venue Capacity)
```

| Filter | Score Range | Description |
|--------|-------------|-------------|
| **Gem** | < 0.5 | Rising stars in intimate rooms |
| **Sweet Spot** | 0.5 - 5.0 | Balanced shows at mid-sized venues |
| **Blockbuster** | > 5.0 | Major stadium events |

### 4.2 Smart Filtering Sidebar

Users can filter events by:

- **Capacity Toggle:** Intimate (<300), Club (300-1.5k), Hall (1.5k-5k), Arena (5k+)
- **Date Range:** "Tonight," "This Weekend," "Next 7 Days"
- **Genre Clouds:** Dynamic tags from Spotify (e.g., "Indie Rock," "Techno," "Jazz")

### 4.3 The Monday Morning Briefing

Every Monday at 8 AM EST, Cloud Scheduler triggers the playlist function:

1. Queries Firestore for top 20 shows matching user preferences for the upcoming week
2. Fetches top 2 tracks from each of the 20 artists via Spotify API
3. Clears the existing "SonicSignal Weekly" Spotify playlist
4. Adds the 40 tracks in order of Curation Score

---

## 5. Execution Roadmap

### Phase 0: Validation Sprint (Week 1)

**Goal:** Validate the data pipeline approach with real API data before building infrastructure

1. **API Exploration Script:** Simple Python script to fetch 1 week of NYC events from all 3 sources
2. **Deduplication Proof-of-Concept:** Test RapidFuzz matching thresholds with real data, export to CSV for manual review
3. **Spotify Match Rate Test:** Attempt to match 50-100 artists, measure success rate and identify edge cases
4. **Venue Capacity Analysis:** Assess how much data is missing, create manual seed list for key NYC venues

**Success Criteria:**
- Successfully fetch events from all 3 APIs
- Deduplication achieves >90% accuracy on manual review
- Spotify match rate >70%
- Decision: Proceed to Phase 1 or adjust strategy

**Deliverable:** Validation report with sample data and recommendations

### Phase 1: Data Pipeline Foundation (Week 2-3)

1. **GCP Project Setup:** Create project, enable APIs (Firestore, Cloud Functions, Cloud Run, Secret Manager)
2. **Firestore Schema:** Implement collections for events, artists, venues with proper indexes
3. **Harvester Functions:** Deploy Cloud Functions to fetch from Ticketmaster, SeatGeek, Songkick
4. **Deduplication Logic:** Implement RapidFuzz matching and merge into unified events
5. **Weekly Scheduling:** Cloud Scheduler job to trigger harvester every Sunday at 3 AM EST

**Deliverable:** Firestore populated with deduplicated events, running on weekly schedule

### Phase 2: Enrichment & Scoring (Week 3-4)

1. **Spotify OAuth:** Implement auth flow, store refresh token in Secret Manager
2. **Artist Enrichment:** Cloud Function to match artists to Spotify IDs, fetch popularity/genres
3. **Unmatched Artist Handling:** Store artists without Spotify profiles with `spotify_matched: false` flag
4. **Curation Engine:** Calculate scores for matched artists only
5. **Manual Review Tools:** Simple admin endpoint to view unmatched artists and low-confidence duplicates

**Deliverable:** Enriched events with Curation Scores and Spotify metadata where available

### Phase 3: Web Application (Week 5-6)

1. **FastAPI Backend:** REST API for events, filtering (capacity, genre, date range)
2. **React Frontend:** Dark-mode UI with filtering sidebar, event cards, genre clouds
3. **Single User Profile:** Store default user preferences in Firestore (no auth required initially)
4. **Cloud Run Deploy:** Containerize and deploy with HTTPS
5. **Playlist Automation:** Cloud Scheduler job for Monday 8 AM playlist refresh (Spotify-matched artists only)

**Deliverable:** Production-ready web app with automated playlist updates

---

## 6. Project Structure

```
sonic-signal/
├── validation/              # Phase 0 exploration scripts
│   ├── explore_apis.py      # Test API connections
│   ├── test_dedup.py        # Deduplication POC
│   ├── test_spotify.py      # Spotify matching test
│   ├── sample_data/         # CSV exports for manual review
│   └── requirements.txt
├── functions/
│   ├── harvester/           # API scraper functions
│   │   ├── main.py
│   │   ├── ticketmaster.py
│   │   ├── seatgeek.py
│   │   ├── songkick.py
│   │   └── requirements.txt
│   ├── deduper/             # Fuzzy matching logic
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── enricher/            # Spotify integration
│   │   ├── main.py
│   │   └── requirements.txt
│   └── playlister/          # Monday morning job
│       ├── main.py
│       └── requirements.txt
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app
│   │   ├── routers/
│   │   │   ├── events.py
│   │   │   ├── artists.py
│   │   │   └── venues.py
│   │   ├── models/
│   │   │   ├── event.py
│   │   │   ├── artist.py
│   │   │   └── venue.py
│   │   └── services/
│   │       ├── firestore.py
│   │       └── spotify.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── EventCard.jsx
│   │   │   ├── FilterSidebar.jsx
│   │   │   └── GenreCloud.jsx
│   │   ├── hooks/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
├── terraform/               # Infrastructure as code (optional)
├── SPEC.md                  # This file
├── CLAUDE.md                # Claude Code instructions
└── README.md
```

---

## 7. Data Models (Firestore)

### 7.1 Events Collection

```
events/{event_id}
{
  "title": "Artist Name @ Venue",
  "artist_id": "ref:artists/abc123",
  "venue_id": "ref:venues/xyz789",
  "date": "2026-02-15T20:00:00Z",
  "curation_score": 0.42,
  "sources": ["seatgeek", "songkick"],
  "ticket_url": "https://...",
  "created_at": Timestamp,
  "updated_at": Timestamp
}
```

### 7.2 Artists Collection

```
artists/{artist_id}
{
  "name": "Artist Name",
  "normalized_name": "artist name",
  "spotify_id": "spotify:artist:xxx",
  "spotify_matched": true,
  "popularity": 45,
  "genres": ["indie rock", "alternative"],
  "top_tracks": ["track_id_1", "track_id_2", "track_id_3"],
  "image_url": "https://..."
}
```

**Note:** Artists without Spotify profiles will have:
- `spotify_matched: false`
- `spotify_id: null`
- `popularity: 0`
- `genres: []`
- `top_tracks: []`

These artists will appear in the UI but be excluded from playlist generation.

### 7.3 Venues Collection

```
venues/{venue_id}
{
  "name": "Mercury Lounge",
  "aliases": ["Merc Lounge", "The Mercury"],
  "capacity": 250,
  "capacity_tier": "intimate",
  "address": "217 E Houston St, New York, NY",
  "neighborhood": "Lower East Side",
  "geo": GeoPoint(40.7223, -73.9877)
}
```

---

## 8. API Integration Details

### 8.1 Ticketmaster Discovery API

- **Endpoint:** `https://app.ticketmaster.com/discovery/v2/events`
- **Auth:** API Key (query parameter)
- **Rate Limit:** 5 requests/second, 5000/day
- **Key Fields:** `name`, `dates.start.localDate`, `_embedded.venues[0]`

### 8.2 SeatGeek API

- **Endpoint:** `https://api.seatgeek.com/2/events`
- **Auth:** Client ID + Secret
- **Rate Limit:** 1000 requests/day (free tier)
- **Key Fields:** `title`, `datetime_local`, `venue.capacity`, `performers[0].name`

### 8.3 Songkick API

- **Endpoint:** `https://api.songkick.com/api/3.0/metro_areas/{id}/calendar.json`
- **Auth:** API Key
- **NYC Metro ID:** 7644
- **Key Fields:** `displayName`, `start.date`, `venue.displayName`, `performance[0].artist`

### 8.4 Spotify Web API

- **Auth:** OAuth 2.0 (Authorization Code Flow)
- **Scopes Required:** `playlist-modify-public`, `playlist-modify-private`, `user-library-read`
- **Key Endpoints:** `/v1/search`, `/v1/artists/{id}`, `/v1/artists/{id}/top-tracks`, `/v1/playlists/{id}/tracks`

---

## 9. GCP Configuration

### Secret Manager Secrets

| Secret Name | Description |
|-------------|-------------|
| `ticketmaster-api-key` | Ticketmaster Discovery API key |
| `seatgeek-client-id` | SeatGeek client identifier |
| `seatgeek-client-secret` | SeatGeek client secret |
| `songkick-api-key` | Songkick API key |
| `spotify-client-id` | Spotify app client ID |
| `spotify-client-secret` | Spotify app client secret |
| `spotify-refresh-token` | Spotify OAuth refresh token |

### Cloud Scheduler Jobs

| Job Name | Schedule | Target |
|----------|----------|--------|
| `weekly-harvest` | `0 3 * * 0` (Sun 3 AM EST) | harvester-function |
| `monday-playlist` | `0 8 * * 1` (Mon 8 AM EST) | playlister-function |

**Note:** Weekly harvesting reduces API costs and rate limit pressure. Can be increased to daily once data freshness requirements are validated.

---

## 10. Known Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| **API Rate Limits** | Exponential backoff with jitter. Cache in Firestore. Async batch requests. |
| **Venue Name Variations** | Maintain `aliases` array in Firestore. Fuzzy matching with 85%+ threshold. |
| **Spotify OAuth Expiry** | Store refresh token in Secret Manager. Auto-refresh before playlist updates. |
| **Artist Name Matching** | Normalize names (strip "The", lowercase). Store `normalized_name` field. |
| **Missing Venue Capacity** | Seed venues collection with NYC data. Default to "Club" tier (500). Flag for review. |
| **Cold Start Latency** | Cloud Run min instances (1). Use 2nd gen Functions if needed. |

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Events ingested/week | > 500 | Firestore document count |
| Deduplication accuracy | > 95% | Manual spot-check |
| Spotify match rate | > 80% | Matched / Total artists |
| Playlist update reliability | 100% | Cloud Logging success rate |
| Data freshness | < 24 hours | `updated_at` timestamp delta |
| Web app response (p95) | < 500ms | Cloud Monitoring latency |

---

## Revision History

- **v1.0 (January 2026):** Initial specification with GCP architecture
