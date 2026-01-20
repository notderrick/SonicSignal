"""
Phase 0: Generate Sample Data

Since Bandsintown and other APIs require auth, let's generate realistic sample data
to validate our deduplication and scoring logic.

This lets us proceed with Phase 0 validation without API barriers.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any

# NYC Venues with realistic capacity data
NYC_VENUES = [
    {"name": "Mercury Lounge", "capacity": 250, "tier": "intimate"},
    {"name": "Bowery Ballroom", "capacity": 575, "tier": "club"},
    {"name": "Brooklyn Steel", "capacity": 1800, "tier": "hall"},
    {"name": "Music Hall of Williamsburg", "capacity": 550, "tier": "club"},
    {"name": "Elsewhere", "capacity": 600, "tier": "club"},
    {"name": "Knockdown Center", "capacity": 1200, "tier": "hall"},
    {"name": "Baby's All Right", "capacity": 350, "tier": "club"},
    {"name": "Rough Trade NYC", "capacity": 250, "tier": "intimate"},
    {"name": "Warsaw", "capacity": 450, "tier": "club"},
    {"name": "Terminal 5", "capacity": 3000, "tier": "hall"},
    {"name": "Webster Hall", "capacity": 1500, "tier": "hall"},
    {"name": "Irving Plaza", "capacity": 1025, "tier": "hall"},
    {"name": "Madison Square Garden", "capacity": 20000, "tier": "arena"},
    {"name": "Barclays Center", "capacity": 19000, "tier": "arena"},
    {"name": "Radio City Music Hall", "capacity": 6000, "tier": "arena"},
]

# Sample artists with genre info (for realism)
SAMPLE_ARTISTS = [
    "Interpol",
    "Yeah Yeah Yeahs",
    "LCD Soundsystem",
    "The National",
    "TV on the Radio",
    "Vampire Weekend",
    "Beach House",
    "DIIV",
    "Parquet Courts",
    "Japanese Breakfast",
    "Snail Mail",
    "Soccer Mommy",
    "Alvvays",
    "Big Thief",
    "Phoebe Bridgers",
    "Mitski",
    "Car Seat Headrest",
    "Angel Olsen",
    "Fleet Foxes",
    "Father John Misty",
]

def generate_events(num_events: int = 100) -> list[dict[str, Any]]:
    """Generate realistic sample event data."""
    events = []

    for i in range(num_events):
        # Random date in next 7 days
        days_ahead = random.randint(0, 7)
        event_date = datetime.now() + timedelta(days=days_ahead)

        # Random time (evening shows: 7pm-11pm)
        hour = random.randint(19, 23)
        minute = random.choice([0, 30])
        event_time = event_date.replace(hour=hour, minute=minute, second=0)

        # Random artist and venue
        artist = random.choice(SAMPLE_ARTISTS)
        venue = random.choice(NYC_VENUES)

        # Generate event
        event = {
            "source": "sample_data",
            "artist": artist,
            "venue": venue["name"],
            "venue_capacity": venue["capacity"],
            "venue_tier": venue["tier"],
            "date": event_time.strftime("%Y-%m-%d"),
            "time": event_time.strftime("%H:%M:%S"),
            "datetime": event_time.isoformat(),
            "ticket_url": f"https://example.com/tickets/{i}",
            "description": f"{artist} live at {venue['name']}",
        }

        events.append(event)

    return events


def generate_duplicates(events: list[dict[str, Any]], num_duplicates: int = 20) -> list[dict[str, Any]]:
    """
    Generate duplicate events with slight variations to test deduplication.
    Simulates what happens when multiple sources list the same show.
    """
    duplicates = []

    for _ in range(num_duplicates):
        # Pick a random source event
        source_event = random.choice(events).copy()

        # Variation 1: Different source name
        duplicate = source_event.copy()
        duplicate["source"] = random.choice(["ticketmaster", "seatgeek", "songkick"])

        # Variation 2: Slight artist name difference
        variations = [
            source_event["artist"],  # Exact match
            f"The {source_event['artist']}",  # Added "The"
            source_event["artist"].upper(),  # All caps
            source_event["artist"].replace(" ", ""),  # No spaces
        ]
        duplicate["artist"] = random.choice(variations)

        # Variation 3: Venue name variation
        venue_variations = [
            source_event["venue"],  # Exact match
            source_event["venue"] + " NYC",  # Added location
            source_event["venue"].replace("The ", ""),  # Removed "The"
        ]
        duplicate["venue"] = random.choice(venue_variations)

        duplicates.append(duplicate)

    return duplicates


def main():
    """Generate sample data for validation."""
    print("=" * 60)
    print("🎵 SonicSignal - Generating Sample Data")
    print("=" * 60)

    # Generate base events
    print("\n📝 Generating 100 sample events...")
    events = generate_events(100)

    # Generate some duplicates to test deduplication logic
    print("📝 Generating 20 duplicate events (for dedup testing)...")
    duplicates = generate_duplicates(events, 20)

    # Combine
    all_events = events + duplicates
    random.shuffle(all_events)  # Mix them up

    print(f"\n✅ Generated {len(all_events)} total events:")
    print(f"   - {len(events)} unique events")
    print(f"   - {len(duplicates)} intentional duplicates")

    # Export to JSON
    import os
    os.makedirs("sample_data", exist_ok=True)

    output = {
        "sample_data": all_events,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "num_events": len(all_events),
            "num_unique": len(events),
            "num_duplicates": len(duplicates),
            "date_range": {
                "start": datetime.now().strftime("%Y-%m-%d"),
                "end": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            },
        }
    }

    with open("sample_data/raw_events.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Data exported to: sample_data/raw_events.json")

    # Analysis
    print("\n" + "=" * 60)
    print("🔍 Quick Analysis")
    print("=" * 60)

    venues = {e["venue"] for e in all_events}
    artists = {e["artist"] for e in all_events}

    print(f"Unique venues: {len(venues)}")
    print(f"Unique artists: {len(artists)}")

    capacities = [e["venue_capacity"] for e in all_events]
    print(f"\nCapacity range: {min(capacities)} - {max(capacities)}")
    print(f"Average capacity: {sum(capacities) / len(capacities):.0f}")

    # Sample venues
    print(f"\nSample venues:")
    for venue in list(venues)[:5]:
        print(f"  - {venue}")

    # Sample artists
    print(f"\nSample artists:")
    for artist in list(artists)[:5]:
        print(f"  - {artist}")

    print("\n✅ Sample data generation complete!")
    print("\nNext steps:")
    print("1. Review sample_data/raw_events.json")
    print("2. Build test_dedup.py to find the 20 duplicates")
    print("3. Build test_spotify.py to match artists to Spotify")


if __name__ == "__main__":
    main()
