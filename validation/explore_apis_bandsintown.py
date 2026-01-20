"""
Phase 0: API Exploration Script (Bandsintown)

Fetches upcoming NYC concert events from Bandsintown API.
Much simpler than original approach - no API key registration required!
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Bandsintown Configuration
# No API key needed - just provide an app identifier
BANDSINTOWN_APP_ID = os.getenv("BANDSINTOWN_APP_ID", "sonicsignal")

# NYC location query
NYC_LOCATION = "New York, NY"


async def fetch_bandsintown_events() -> list[dict[str, Any]]:
    """Fetch events from Bandsintown API by location."""
    print("\n🎸 Fetching from Bandsintown...")

    # Bandsintown API endpoint (using newer format)
    url = "https://rest.bandsintown.com/events"

    # Date range: next 7 days
    start_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "app_id": BANDSINTOWN_APP_ID,
        "location": NYC_LOCATION,
        "date": f"{start_date},{end_date}",
    }

    events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            raw_events = response.json()

            if isinstance(raw_events, list):
                for event in raw_events:
                    venue = event.get("venue", {})
                    lineup = event.get("lineup", [])
                    artist = lineup[0] if lineup else event.get("artist", {}).get("name", "Unknown")

                    events.append({
                        "source": "bandsintown",
                        "artist": artist if isinstance(artist, str) else artist,
                        "venue": venue.get("name", "Unknown"),
                        "venue_capacity": venue.get("capacity"),  # May be null
                        "venue_region": venue.get("region", ""),
                        "venue_city": venue.get("city", ""),
                        "date": event.get("datetime", "").split("T")[0],
                        "time": event.get("datetime", "").split("T")[1].split("+")[0] if "T" in event.get("datetime", "") else None,
                        "ticket_url": event.get("url"),
                        "description": event.get("description", ""),
                        "raw": event,  # Store full response for debugging
                    })

                print(f"✅ Fetched {len(events)} events from Bandsintown")
            else:
                print("⚠️  Unexpected response format from Bandsintown")

        except httpx.HTTPStatusError as e:
            print(f"❌ Bandsintown API error: {e.response.status_code}")
            print(f"   Response: {e.response.text[:200]}")
        except Exception as e:
            print(f"❌ Bandsintown fetch failed: {e}")

    return events


async def fetch_bandsintown_by_artists(sample_artists: list[str]) -> list[dict[str, Any]]:
    """
    Fetch events from Bandsintown by searching for specific artists.
    This is an alternative approach if location-based search doesn't work well.
    """
    print("\n🎤 Fetching artist events from Bandsintown...")

    events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for artist in tqdm(sample_artists, desc="Fetching artists"):
            url = f"https://rest.bandsintown.com/artists/{artist}/events"

            params = {
                "app_id": BANDSINTOWN_APP_ID,
            }

            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                artist_events = response.json()

                if isinstance(artist_events, list):
                    # Filter to NYC events in next 7 days
                    end_date = datetime.now() + timedelta(days=7)

                    for event in artist_events:
                        venue = event.get("venue", {})

                        # Check if in NYC area
                        if venue.get("city") not in ["New York", "Brooklyn", "Queens", "Bronx", "Manhattan"]:
                            continue

                        # Check if within date range
                        event_date_str = event.get("datetime", "").split("T")[0]
                        if event_date_str:
                            event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                            if event_date > end_date:
                                continue

                        events.append({
                            "source": "bandsintown",
                            "artist": artist,
                            "venue": venue.get("name", "Unknown"),
                            "venue_capacity": venue.get("capacity"),
                            "venue_region": venue.get("region", ""),
                            "venue_city": venue.get("city", ""),
                            "date": event_date_str,
                            "time": event.get("datetime", "").split("T")[1].split("+")[0] if "T" in event.get("datetime", "") else None,
                            "ticket_url": event.get("url"),
                            "raw": event,
                        })

                # Small delay to be respectful to API
                await asyncio.sleep(0.2)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    continue  # Artist not found, skip
                print(f"⚠️  Error fetching {artist}: {e.response.status_code}")
            except Exception as e:
                print(f"⚠️  Error fetching {artist}: {e}")

    print(f"✅ Fetched {len(events)} NYC events from {len(sample_artists)} artists")
    return events


async def main():
    """Main execution function."""
    print("=" * 60)
    print("🎵 SonicSignal - Phase 0: API Exploration (Bandsintown)")
    print("=" * 60)

    # Fetch events from Bandsintown
    bandsintown_events = await fetch_bandsintown_events()

    # If location search didn't return many results, try artist-based search
    # with a sample of popular NYC-based artists
    if len(bandsintown_events) < 50:
        print("\n⚠️  Location search returned few results. Trying artist-based search...")
        sample_artists = [
            "LCD Soundsystem",
            "The National",
            "Interpol",
            "Yeah Yeah Yeahs",
            "Vampire Weekend",
            "TV on the Radio",
            "The Strokes",
            "Animal Collective",
            "Beach House",
            "DIIV",
        ]
        artist_events = await fetch_bandsintown_by_artists(sample_artists)
        bandsintown_events.extend(artist_events)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Bandsintown: {len(bandsintown_events)} events")

    # Export to JSON
    output_path = "sample_data/raw_events.json"
    os.makedirs("sample_data", exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({
            "bandsintown": bandsintown_events,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "date_range": {
                    "start": datetime.now().strftime("%Y-%m-%d"),
                    "end": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                },
                "location": NYC_LOCATION,
            }
        }, f, indent=2)

    print(f"\n💾 Raw data exported to: {output_path}")

    # Basic analysis
    print("\n" + "=" * 60)
    print("🔍 Quick Analysis")
    print("=" * 60)

    # Extract unique venues and artists
    venues = {e["venue"] for e in bandsintown_events}
    artists = {e["artist"] for e in bandsintown_events}

    print(f"Unique venues: {len(venues)}")
    print(f"Unique artists: {len(artists)}")

    # Venue capacity analysis
    events_with_capacity = [e for e in bandsintown_events if e.get("venue_capacity")]
    print(f"\nEvents with capacity data: {len(events_with_capacity)} / {len(bandsintown_events)}")

    if events_with_capacity:
        capacities = [e["venue_capacity"] for e in events_with_capacity]
        print(f"Capacity range: {min(capacities)} - {max(capacities)}")
        print(f"Average capacity: {sum(capacities) / len(capacities):.0f}")

    # Sample venues
    print(f"\nSample venues ({min(5, len(venues))} of {len(venues)}):")
    for venue in list(venues)[:5]:
        print(f"  - {venue}")

    # Sample artists
    print(f"\nSample artists ({min(5, len(artists))} of {len(artists)}):")
    for artist in list(artists)[:5]:
        print(f"  - {artist}")

    print("\n✅ Exploration complete!")
    print("\nNext steps:")
    print("1. Review sample_data/raw_events.json")
    print("2. Run test_dedup.py (when created) to test deduplication")
    print("3. Run test_spotify.py to test Spotify matching")


if __name__ == "__main__":
    asyncio.run(main())
