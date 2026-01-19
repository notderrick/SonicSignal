# Phase 0: Validation Scripts

This directory contains scripts to validate the SonicSignal data pipeline approach before building production infrastructure.

## Setup

1. **Create virtual environment:**
   ```bash
   cd validation
   python3 -m venv ../venv
   source ../venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   ```bash
   cp ../.env.example ../.env
   # Edit .env and add your API keys
   ```

## API Key Registration

You'll need to register for the following APIs:

### Ticketmaster Discovery API
1. Go to https://developer.ticketmaster.com/
2. Create an account
3. Request an API key
4. Add to `.env`: `TICKETMASTER_API_KEY=your_key_here`

### SeatGeek Platform API
1. Go to https://platform.seatgeek.com/
2. Sign up for a developer account
3. Get your Client ID and Client Secret
4. Add to `.env`:
   - `SEATGEEK_CLIENT_ID=your_client_id`
   - `SEATGEEK_CLIENT_SECRET=your_client_secret`

### Songkick API
1. Go to https://www.songkick.com/developer
2. Request an API key
3. Add to `.env`: `SONGKICK_API_KEY=your_key_here`

### Spotify Web API
1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Get your Client ID and Client Secret
4. Add to `.env`:
   - `SPOTIFY_CLIENT_ID=your_client_id`
   - `SPOTIFY_CLIENT_SECRET=your_client_secret`

## Scripts

### 1. `explore_apis.py` - API Exploration
Fetches 1 week of NYC events from all 3 sources and exports to JSON.

**Usage:**
```bash
python explore_apis.py
```

**Output:**
- `sample_data/raw_events.json` - Raw API responses
- Console summary with event counts and overlap analysis

**Success Criteria:**
- Fetch >100 events from each source
- No rate limit errors
- Data structure is consistent

### 2. `test_dedup.py` - Deduplication Testing
Tests fuzzy matching logic to identify duplicate events across sources.

**Usage:**
```bash
python test_dedup.py
```

**Output:**
- `sample_data/duplicates.csv` - Identified duplicate pairs with confidence scores
- Manual review required to validate accuracy

**Success Criteria:**
- >90% accuracy on manual review
- <5% false positives

### 3. `test_spotify.py` - Spotify Match Rate
Tests how many artists from sample data can be matched to Spotify profiles.

**Usage:**
```bash
python test_spotify.py
```

**Output:**
- `sample_data/spotify_matches.csv` - Artist matches with popularity/genres
- `sample_data/unmatched_artists.txt` - Artists not found on Spotify

**Success Criteria:**
- >70% match rate
- Understand why artists don't match

## Validation Checklist

- [ ] Register for all 4 API accounts
- [ ] Configure `.env` with all keys
- [ ] Run `explore_apis.py` - fetches >100 events per source
- [ ] Run `test_dedup.py` - deduplication >90% accurate
- [ ] Run `test_spotify.py` - match rate >70%
- [ ] Manual review of sample_data outputs
- [ ] Create `VALIDATION_REPORT.md` with findings
- [ ] Decision: Proceed to Phase 1 or adjust strategy

## Troubleshooting

**API Rate Limits:**
- Ticketmaster: 5 requests/second, 5000/day
- SeatGeek: 1000 requests/day (free tier)
- Songkick: Contact support for limits
- Spotify: 100 requests/30 seconds

If you hit rate limits, add delays between requests or reduce fetch window.

**No Events Found:**
- Check date range (should be next 7 days)
- Verify city/state filters are correct
- Some sources may have fewer NYC events during certain weeks

**Import Errors:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
