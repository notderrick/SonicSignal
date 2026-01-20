# Phase 0: Validation Scripts

This directory contains scripts to validate the SonicSignal data pipeline approach before building production infrastructure.

## Quick Start (No API Keys Required!)

1. **Create virtual environment:**
   ```bash
   cd /Users/derrickhoward/Development/sonicsignal
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r validation/requirements.txt
   ```

3. **Run exploration (works immediately!):**
   ```bash
   python validation/explore_apis_bandsintown.py
   ```

That's it! No API key registration needed to get started.

## Why Bandsintown?

For Phase 0 validation, we're using **Bandsintown** instead of Ticketmaster/SeatGeek/Songkick because:

✅ **No API key signup required** - Just provide an app identifier
✅ **Comprehensive NYC coverage** - Includes indie venues and smaller acts
✅ **Good data quality** - Artist names, venues, dates, ticket links
✅ **Easy to use** - Simple REST API, no OAuth

Later in production (Phase 1+), we can add additional sources if needed.

## Configuration

### Required (for Bandsintown)

Edit `.env` and set:
```bash
BANDSINTOWN_APP_ID=sonicsignal  # Can be any identifier
```

Or just use the default - it works without configuration!

### Optional (for Spotify matching)

Only needed when running `test_spotify.py`:

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Get your Client ID and Client Secret
4. Add to `.env`:
   ```bash
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

## Scripts

### 1. `explore_apis_bandsintown.py` - API Exploration ⭐ START HERE

Fetches 1 week of NYC events from Bandsintown and exports to JSON.

**Usage:**
```bash
python validation/explore_apis_bandsintown.py
```

**Output:**
- `sample_data/raw_events.json` - Raw API responses with metadata
- Console summary with event counts, venue/artist lists, capacity analysis

**What it does:**
1. Searches Bandsintown for NYC events in next 7 days
2. If few results, also searches popular NYC artists
3. Exports all data to JSON
4. Provides quick stats on venues, artists, capacity data

**Success Criteria:**
- Fetch >50 events from Bandsintown
- Events have artist, venue, date, ticket URL
- Some events include venue capacity

### 2. `test_dedup.py` - Deduplication Testing (TODO)

Tests fuzzy matching logic to identify duplicate events.

**Usage:**
```bash
python validation/test_dedup.py
```

**Output:**
- `sample_data/duplicates.csv` - Identified duplicate pairs with confidence scores
- Manual review required to validate accuracy

**Success Criteria:**
- >90% accuracy on manual review
- <5% false positives

### 3. `test_spotify.py` - Spotify Match Rate (TODO)

Tests how many artists from sample data can be matched to Spotify profiles.

**Requires Spotify API keys** (see Configuration above)

**Usage:**
```bash
python validation/test_spotify.py
```

**Output:**
- `sample_data/spotify_matches.csv` - Artist matches with popularity/genres
- `sample_data/unmatched_artists.txt` - Artists not found on Spotify

**Success Criteria:**
- >70% match rate
- Understand why artists don't match

## Validation Checklist

- [ ] Run `explore_apis_bandsintown.py` - fetches >50 events
- [ ] Review `sample_data/raw_events.json` - check data quality
- [ ] Build and run `test_dedup.py` - deduplication >90% accurate
- [ ] Get Spotify API keys (optional for now)
- [ ] Build and run `test_spotify.py` - match rate >70%
- [ ] Create `VALIDATION_REPORT.md` with findings
- [ ] Decision: Proceed to Phase 1 or adjust strategy

## Troubleshooting

**No events found:**
- Bandsintown may have limited data for certain dates
- Try running on a different day of the week
- The script will automatically try artist-based search as fallback

**Rate limiting:**
- Bandsintown is generally permissive
- Script includes 200ms delays between artist requests
- If you hit limits, reduce the sample artist list

**Import errors:**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Run `pip install -r requirements.txt` again

## Legacy Scripts

**`explore_apis.py`** - Original script using Ticketmaster/SeatGeek/Songkick.
Kept for reference but requires API key registration. Use `explore_apis_bandsintown.py` instead for Phase 0.

## Production Notes

For Phase 1 (production deployment), we may want to:
- Add Ticketmaster for major venue coverage
- Add SeatGeek for capacity data
- Add Songkick for DIY/small venue coverage
- Use Bandsintown as the base layer

But for validation, Bandsintown alone is sufficient to prove the concept.
