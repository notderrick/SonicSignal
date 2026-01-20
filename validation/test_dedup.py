"""
Phase 0: Deduplication Testing

Tests fuzzy matching logic to identify duplicate events across sources.
Uses RapidFuzz to match artist names and venue names.
"""

import json
import re
from typing import Any

import pandas as pd
from rapidfuzz import fuzz


def normalize_artist_name(name: str) -> str:
    """Normalize artist name for matching."""
    name = name.lower().strip()
    name = re.sub(r'^the\s+', '', name)  # Remove leading "The"
    name = re.sub(r'[^\w\s]', '', name)   # Remove special chars
    name = re.sub(r'\s+', ' ', name)      # Collapse whitespace
    return name


def normalize_venue_name(name: str) -> str:
    """Normalize venue name for matching."""
    name = name.lower().strip()
    name = re.sub(r'\s+(nyc|new york)$', '', name)  # Remove location suffix
    name = re.sub(r'^the\s+', '', name)  # Remove leading "The"
    name = re.sub(r'[^\w\s]', '', name)   # Remove special chars
    name = re.sub(r'\s+', ' ', name)      # Collapse whitespace
    return name


def is_duplicate(event1: dict[str, Any], event2: dict[str, Any]) -> tuple[bool, float, float]:
    """
    Check if two events are duplicates.

    Returns:
        (is_duplicate, artist_match_score, venue_match_score)
    """
    # Normalize names
    artist1_norm = normalize_artist_name(event1["artist"])
    artist2_norm = normalize_artist_name(event2["artist"])

    venue1_norm = normalize_venue_name(event1["venue"])
    venue2_norm = normalize_venue_name(event2["venue"])

    # Fuzzy match artists
    artist_score = fuzz.token_sort_ratio(artist1_norm, artist2_norm)

    # Fuzzy match venues
    venue_score = fuzz.token_sort_ratio(venue1_norm, venue2_norm)

    # Date match (exact)
    date_match = event1["date"] == event2["date"]

    # Criteria:
    # - Artist match >= 90%
    # - Venue match >= 85%
    # - Same date
    is_dup = artist_score >= 90 and venue_score >= 85 and date_match

    return is_dup, artist_score, venue_score


def find_duplicates(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find all duplicate event pairs."""
    duplicates = []

    # Compare each event with every other event
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            event1 = events[i]
            event2 = events[j]

            is_dup, artist_score, venue_score = is_duplicate(event1, event2)

            if is_dup:
                duplicates.append({
                    "event1_index": i,
                    "event2_index": j,
                    "event1_artist": event1["artist"],
                    "event2_artist": event2["artist"],
                    "event1_venue": event1["venue"],
                    "event2_venue": event2["venue"],
                    "date": event1["date"],
                    "artist_match": artist_score,
                    "venue_match": venue_score,
                    "confidence": "high" if artist_score >= 95 and venue_score >= 95 else "medium",
                    "event1_source": event1.get("source", "unknown"),
                    "event2_source": event2.get("source", "unknown"),
                })

    return duplicates


def main():
    """Run deduplication test."""
    print("=" * 60)
    print("🔍 SonicSignal - Deduplication Testing")
    print("=" * 60)

    # Load sample data
    print("\n📂 Loading sample data...")
    with open("sample_data/raw_events.json", "r") as f:
        data = json.load(f)

    events = data["sample_data"]
    print(f"✅ Loaded {len(events)} events")

    # Find duplicates
    print("\n🔎 Finding duplicates...")
    duplicates = find_duplicates(events)

    print(f"✅ Found {len(duplicates)} duplicate pairs")

    # Export to CSV
    if duplicates:
        df = pd.DataFrame(duplicates)
        df.to_csv("sample_data/duplicates.csv", index=False)
        print(f"💾 Exported to: sample_data/duplicates.csv")

    # Summary
    print("\n" + "=" * 60)
    print("📊 Deduplication Summary")
    print("=" * 60)
    print(f"Total events:        {len(events)}")
    print(f"Duplicate pairs:     {len(duplicates)}")
    print(f"Unique events:       {len(events) - len(duplicates)}")

    # Confidence breakdown
    high_conf = [d for d in duplicates if d["confidence"] == "high"]
    medium_conf = [d for d in duplicates if d["confidence"] == "medium"]

    print(f"\nHigh confidence:     {len(high_conf)}")
    print(f"Medium confidence:   {len(medium_conf)}")

    # Show sample duplicates
    if duplicates:
        print("\n" + "=" * 60)
        print("🔍 Sample Duplicates (first 5)")
        print("=" * 60)

        for i, dup in enumerate(duplicates[:5]):
            print(f"\n{i+1}. Artist Match: {dup['artist_match']:.1f}% | Venue Match: {dup['venue_match']:.1f}%")
            print(f"   Event 1: {dup['event1_artist']} @ {dup['event1_venue']} ({dup['event1_source']})")
            print(f"   Event 2: {dup['event2_artist']} @ {dup['event2_venue']} ({dup['event2_source']})")
            print(f"   Date: {dup['date']} | Confidence: {dup['confidence']}")

    # Calculate accuracy (if we know ground truth)
    metadata = data.get("metadata", {})
    expected_duplicates = metadata.get("num_duplicates", 0)

    if expected_duplicates > 0:
        accuracy = (len(duplicates) / expected_duplicates) * 100
        print("\n" + "=" * 60)
        print("✅ Accuracy Check")
        print("=" * 60)
        print(f"Expected duplicates: {expected_duplicates}")
        print(f"Found duplicates:    {len(duplicates)}")
        print(f"Detection rate:      {accuracy:.1f}%")

        if accuracy >= 90:
            print("✅ SUCCESS: Deduplication accuracy >= 90%")
        else:
            print("⚠️  WARNING: Deduplication accuracy < 90%")

    print("\n✅ Deduplication test complete!")


if __name__ == "__main__":
    main()
