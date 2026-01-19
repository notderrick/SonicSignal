"""
Phase 0: API Exploration Script

Fetches 1 week of NYC concert events from Ticketmaster, SeatGeek, and Songkick.
Exports raw data to JSON for analysis.
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

# API Configuration
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
SEATGEEK_CLIENT_ID = os.getenv("SEATGEEK_CLIENT_ID")
SEATGEEK_CLIENT_SECRET = os.getenv("SEATGEEK_CLIENT_SECRET")
SONGKICK_API_KEY = os.getenv("SONGKICK_API_KEY")

# NYC Metro ID for Songkick
SONGKICK_NYC_METRO_ID = 7644


async def fetch_ticketmaster_events() -> list[dict[str, Any]]:
    """Fetch events from Ticketmaster Discovery API."""
    print("\n🎫 Fetching from Ticketmaster...")

    if not TICKETMASTER_API_KEY:
        print("⚠️  TICKETMASTER_API_KEY not set. Skipping.")
        return []

    url = "https://app.ticketmaster.com/discovery/v2/events"

    # Date range: next 7 days
    start_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": "New York",
        "stateCode": "NY",
        "classificationName": "Music",
        "startDateTime": start_date,
        "endDateTime": end_date,
        "size": 200,  # Max per request
    }

    events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "_embedded" in data and "events" in data["_embedded"]:
                raw_events = data["_embedded"]["events"]

                for event in raw_events:
                    # Extract key fields
                    venue = event.get("_embedded", {}).get("venues", [{}])[0]

                    events.append({
                        "source": "ticketmaster",
                        "artist": event.get("name", "Unknown"),
                        "venue": venue.get("name", "Unknown"),
                        "venue_capacity": venue.get("capacity"),
                        "date": event.get("dates", {}).get("start", {}).get("localDate"),
                        "time": event.get("dates", {}).get("start", {}).get("localTime"),
                        "ticket_url": event.get("url"),
                        "raw": event,  # Store full response for debugging
                    })

                print(f"✅ Fetched {len(events)} events from Ticketmaster")
            else:
                print("⚠️  No events found in Ticketmaster response")

        except httpx.HTTPStatusError as e:
            print(f"❌ Ticketmaster API error: {e.response.status_code}")
        except Exception as e:
            print(f"❌ Ticketmaster fetch failed: {e}")

    return events


async def fetch_seatgeek_events() -> list[dict[str, Any]]:
    """Fetch events from SeatGeek API."""
    print("\n🪑 Fetching from SeatGeek...")

    if not SEATGEEK_CLIENT_ID or not SEATGEEK_CLIENT_SECRET:
        print("⚠️  SeatGeek credentials not set. Skipping.")
        return []

    url = "https://api.seatgeek.com/2/events"

    # Date range: next 7 days
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    params = {
        "client_id": SEATGEEK_CLIENT_ID,
        "client_secret": SEATGEEK_CLIENT_SECRET,
        "venue.city": "New York",
        "venue.state": "NY",
        "taxonomies.name": "concert",
        "datetime_utc.gte": start_date,
        "datetime_utc.lte": end_date,
        "per_page": 100,
    }

    events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "events" in data:
                raw_events = data["events"]

                for event in raw_events:
                    venue = event.get("venue", {})
                    performers = event.get("performers", [])
                    artist = performers[0].get("name") if performers else "Unknown"

                    events.append({
                        "source": "seatgeek",
                        "artist": artist,
                        "venue": venue.get("name", "Unknown"),
                        "venue_capacity": venue.get("capacity"),
                        "date": event.get("datetime_local", "").split("T")[0],
                        "time": event.get("datetime_local", "").split("T")[1] if "T" in event.get("datetime_local", "") else None,
                        "ticket_url": event.get("url"),
                        "raw": event,
                    })

                print(f"✅ Fetched {len(events)} events from SeatGeek")
            else:
                print("⚠️  No events found in SeatGeek response")

        except httpx.HTTPStatusError as e:
            print(f"❌ SeatGeek API error: {e.response.status_code}")
        except Exception as e:
            print(f"❌ SeatGeek fetch failed: {e}")

    return events


async def fetch_songkick_events() -> list[dict[str, Any]]:
    """Fetch events from Songkick API."""
    print("\n🎸 Fetching from Songkick...")

    if not SONGKICK_API_KEY:
        print("⚠️  SONGKICK_API_KEY not set. Skipping.")
        return []

    url = f"https://api.songkick.com/api/3.0/metro_areas/{SONGKICK_NYC_METRO_ID}/calendar.json"

    params = {
        "apikey": SONGKICK_API_KEY,
        "per_page": 100,
    }

    events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "resultsPage" in data and "results" in data["resultsPage"]:
                results = data["resultsPage"]["results"]

                if "event" in results:
                    raw_events = results["event"]

                    # Filter to next 7 days
                    end_date = datetime.now() + timedelta(days=7)

                    for event in raw_events:
                        event_date_str = event.get("start", {}).get("date")
                        if not event_date_str:
                            continue

                        event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                        if event_date > end_date:
                            continue

                        venue = event.get("venue", {})
                        performances = event.get("performance", [])
                        artist = performances[0].get("artist", {}).get("displayName") if performances else "Unknown"

                        events.append({
                            "source": "songkick",
                            "artist": artist,
                            "venue": venue.get("displayName", "Unknown"),
                            "venue_capacity": None,  # Songkick doesn't provide capacity
                            "date": event_date_str,
                            "time": event.get("start", {}).get("time"),
                            "ticket_url": event.get("uri"),
                            "raw": event,
                        })

                    print(f"✅ Fetched {len(events)} events from Songkick")
                else:
                    print("⚠️  No events found in Songkick response")

        except httpx.HTTPStatusError as e:
            print(f"❌ Songkick API error: {e.response.status_code}")
        except Exception as e:
            print(f"❌ Songkick fetch failed: {e}")

    return events


async def main():
    """Main execution function."""
    print("=" * 60)
    print("🎵 SonicSignal - Phase 0: API Exploration")
    print("=" * 60)

    # Fetch from all sources concurrently
    results = await asyncio.gather(
        fetch_ticketmaster_events(),
        fetch_seatgeek_events(),
        fetch_songkick_events(),
    )

    ticketmaster_events, seatgeek_events, songkick_events = results

    # Combine all events
    all_events = {
        "ticketmaster": ticketmaster_events,
        "seatgeek": seatgeek_events,
        "songkick": songkick_events,
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Ticketmaster: {len(ticketmaster_events)} events")
    print(f"SeatGeek:     {len(seatgeek_events)} events")
    print(f"Songkick:     {len(songkick_events)} events")
    print(f"TOTAL:        {len(ticketmaster_events) + len(seatgeek_events) + len(songkick_events)} events")

    # Export to JSON
    output_path = "sample_data/raw_events.json"
    with open(output_path, "w") as f:
        json.dump(all_events, f, indent=2)

    print(f"\n💾 Raw data exported to: {output_path}")

    # Basic overlap analysis
    print("\n" + "=" * 60)
    print("🔍 Quick Overlap Analysis")
    print("=" * 60)

    # Extract unique artists from each source
    tm_artists = {e["artist"].lower() for e in ticketmaster_events}
    sg_artists = {e["artist"].lower() for e in seatgeek_events}
    sk_artists = {e["artist"].lower() for e in songkick_events}

    print(f"Unique artists - Ticketmaster: {len(tm_artists)}")
    print(f"Unique artists - SeatGeek:     {len(sg_artists)}")
    print(f"Unique artists - Songkick:     {len(sk_artists)}")

    # Find overlaps
    tm_sg_overlap = tm_artists & sg_artists
    tm_sk_overlap = tm_artists & sk_artists
    sg_sk_overlap = sg_artists & sk_artists
    all_overlap = tm_artists & sg_artists & sk_artists

    print(f"\nOverlap (Ticketmaster ∩ SeatGeek):  {len(tm_sg_overlap)} artists")
    print(f"Overlap (Ticketmaster ∩ Songkick):  {len(tm_sk_overlap)} artists")
    print(f"Overlap (SeatGeek ∩ Songkick):      {len(sg_sk_overlap)} artists")
    print(f"Overlap (All 3 sources):            {len(all_overlap)} artists")

    if all_overlap:
        print(f"\nSample artists in all 3 sources: {list(all_overlap)[:5]}")

    print("\n✅ Exploration complete!")


if __name__ == "__main__":
    asyncio.run(main())
