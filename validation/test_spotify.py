"""
Phase 0: Spotify Matching Test

Tests how many artists from sample data can be matched to Spotify profiles.
Measures match rate and collects popularity/genre data for scoring validation.
"""

import json
import os
from typing import Any

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def init_spotify() -> spotipy.Spotify:
    """Initialize Spotify client."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise ValueError(
            "Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and "
            "SPOTIFY_CLIENT_SECRET in .env file.\n\n"
            "Get them at: https://developer.spotify.com/dashboard"
        )

    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def search_artist(sp: spotipy.Spotify, artist_name: str) -> dict[str, Any] | None:
    """
    Search for an artist on Spotify.

    Returns artist data if found, None otherwise.
    """
    try:
        results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)

        if results["artists"]["items"]:
            artist = results["artists"]["items"][0]
            return {
                "name": artist["name"],
                "spotify_id": artist["id"],
                "popularity": artist["popularity"],
                "genres": artist["genres"],
                "followers": artist["followers"]["total"],
                "image_url": artist["images"][0]["url"] if artist["images"] else None,
                "spotify_url": artist["external_urls"]["spotify"],
            }
    except Exception as e:
        print(f"⚠️  Error searching for {artist_name}: {e}")

    return None


def main():
    """Run Spotify matching test."""
    print("=" * 60)
    print("🎧 SonicSignal - Spotify Matching Test")
    print("=" * 60)

    # Initialize Spotify
    print("\n🔑 Initializing Spotify client...")
    try:
        sp = init_spotify()
        print("✅ Connected to Spotify API")
    except ValueError as e:
        print(f"\n❌ {e}")
        return

    # Load sample data
    print("\n📂 Loading sample data...")
    with open("sample_data/raw_events.json", "r") as f:
        data = json.load(f)

    events = data["sample_data"]

    # Extract unique artists
    unique_artists = list(set(event["artist"] for event in events))
    unique_artists.sort()

    print(f"✅ Found {len(unique_artists)} unique artists")

    # Search for each artist
    print(f"\n🔎 Searching Spotify for {len(unique_artists)} artists...")

    matches = []
    unmatched = []

    for artist_name in tqdm(unique_artists, desc="Searching"):
        result = search_artist(sp, artist_name)

        if result:
            matches.append({
                "original_name": artist_name,
                "spotify_name": result["name"],
                "spotify_id": result["spotify_id"],
                "popularity": result["popularity"],
                "genres": ", ".join(result["genres"]) if result["genres"] else "",
                "followers": result["followers"],
                "image_url": result["image_url"],
                "spotify_url": result["spotify_url"],
                "matched": True,
            })
        else:
            unmatched.append(artist_name)
            matches.append({
                "original_name": artist_name,
                "spotify_name": "",
                "spotify_id": "",
                "popularity": 0,
                "genres": "",
                "followers": 0,
                "image_url": "",
                "spotify_url": "",
                "matched": False,
            })

    print(f"\n✅ Search complete!")

    # Export results
    df = pd.DataFrame(matches)
    df.to_csv("sample_data/spotify_matches.csv", index=False)
    print(f"💾 Exported to: sample_data/spotify_matches.csv")

    # Export unmatched artists
    if unmatched:
        with open("sample_data/unmatched_artists.txt", "w") as f:
            f.write("\n".join(unmatched))
        print(f"💾 Unmatched artists saved to: sample_data/unmatched_artists.txt")

    # Calculate metrics
    num_matched = len([m for m in matches if m["matched"]])
    match_rate = (num_matched / len(unique_artists)) * 100

    print("\n" + "=" * 60)
    print("📊 Spotify Matching Results")
    print("=" * 60)
    print(f"Total artists:       {len(unique_artists)}")
    print(f"Matched:             {num_matched}")
    print(f"Unmatched:           {len(unmatched)}")
    print(f"Match rate:          {match_rate:.1f}%")

    if match_rate >= 70:
        print("✅ SUCCESS: Match rate >= 70%")
    else:
        print("⚠️  WARNING: Match rate < 70%")

    # Popularity analysis
    matched_df = df[df["matched"] == True]
    if not matched_df.empty:
        print("\n" + "=" * 60)
        print("🎵 Popularity Analysis (Matched Artists)")
        print("=" * 60)
        print(f"Average popularity:  {matched_df['popularity'].mean():.1f}")
        print(f"Median popularity:   {matched_df['popularity'].median():.1f}")
        print(f"Min popularity:      {matched_df['popularity'].min()}")
        print(f"Max popularity:      {matched_df['popularity'].max()}")

        # Popularity distribution
        low_pop = len(matched_df[matched_df["popularity"] < 30])
        mid_pop = len(matched_df[(matched_df["popularity"] >= 30) & (matched_df["popularity"] < 70)])
        high_pop = len(matched_df[matched_df["popularity"] >= 70])

        print(f"\nPopularity distribution:")
        print(f"  Low (<30):         {low_pop} ({low_pop/len(matched_df)*100:.1f}%)")
        print(f"  Medium (30-69):    {mid_pop} ({mid_pop/len(matched_df)*100:.1f}%)")
        print(f"  High (70+):        {high_pop} ({high_pop/len(matched_df)*100:.1f}%)")

        # Top genres
        all_genres = []
        for genres_str in matched_df["genres"]:
            if genres_str:
                all_genres.extend(genres_str.split(", "))

        if all_genres:
            from collections import Counter
            genre_counts = Counter(all_genres).most_common(10)

            print(f"\n" + "=" * 60)
            print("🎸 Top 10 Genres")
            print("=" * 60)
            for genre, count in genre_counts:
                print(f"  {genre:30} {count}")

    # Sample matches
    if not matched_df.empty:
        print("\n" + "=" * 60)
        print("🔍 Sample Matched Artists (first 5)")
        print("=" * 60)

        for i, row in matched_df.head(5).iterrows():
            print(f"\n{row['original_name']}")
            print(f"  Spotify: {row['spotify_name']}")
            print(f"  Popularity: {row['popularity']}")
            print(f"  Genres: {row['genres'][:60]}{'...' if len(row['genres']) > 60 else ''}")
            print(f"  Followers: {row['followers']:,}")

    # Unmatched artists
    if unmatched:
        print("\n" + "=" * 60)
        print(f"⚠️  Unmatched Artists ({len(unmatched)})")
        print("=" * 60)
        for artist in unmatched[:10]:
            print(f"  - {artist}")
        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more")

    print("\n✅ Spotify matching test complete!")
    print("\nNext steps:")
    print("1. Review sample_data/spotify_matches.csv")
    print("2. Check sample_data/unmatched_artists.txt")
    print("3. View results at http://localhost:8000 (if viewer is running)")


if __name__ == "__main__":
    main()
