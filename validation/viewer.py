"""
Phase 0: Validation Results Viewer

Simple web interface to view validation results on localhost.
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="SonicSignal Validation Viewer")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with navigation."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SonicSignal - Phase 0 Validation</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, sans-serif;
                background: #F9F9F7;
                color: #1A1A1A;
                padding: 40px;
                line-height: 1.6;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 {
                font-family: 'Playfair Display', serif;
                font-size: 3em;
                margin-bottom: 20px;
                border-bottom: 2px solid #1A1A1A;
                padding-bottom: 20px;
            }
            .nav {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .card {
                background: white;
                border: 1px solid #1A1A1A;
                padding: 30px;
                text-decoration: none;
                color: #1A1A1A;
                transition: background 0.2s;
            }
            .card:hover { background: #f0f0f0; }
            .card h2 {
                font-family: 'Playfair Display', serif;
                font-size: 1.8em;
                margin-bottom: 10px;
            }
            .card p { margin-top: 10px; opacity: 0.7; }
            .badge {
                display: inline-block;
                background: #2D5A27;
                color: white;
                padding: 4px 12px;
                font-size: 0.85em;
                font-family: 'JetBrains Mono', monospace;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 SonicSignal<br>Phase 0 Validation</h1>
            <div class="nav">
                <a href="/events" class="card">
                    <h2>Sample Events</h2>
                    <span class="badge">120 EVENTS</span>
                    <p>View all generated sample events with venue capacities and dates</p>
                </a>
                <a href="/duplicates" class="card">
                    <h2>Duplicates Found</h2>
                    <span class="badge">19 PAIRS • 95% ACCURACY</span>
                    <p>Deduplication results with match scores and confidence levels</p>
                </a>
                <a href="/stats" class="card">
                    <h2>Statistics</h2>
                    <span class="badge">ANALYSIS</span>
                    <p>Venue distribution, capacity analysis, and artist breakdown</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/events", response_class=HTMLResponse)
async def events():
    """View all events."""
    # Load events
    with open("sample_data/raw_events.json", "r") as f:
        data = json.load(f)

    events = data["sample_data"]

    # Build HTML
    rows = ""
    for i, event in enumerate(events[:50]):  # Show first 50
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td class="artist">{event['artist']}</td>
            <td>{event['venue']}</td>
            <td class="capacity">{event['venue_capacity']}</td>
            <td class="tier">{event['venue_tier']}</td>
            <td>{event['date']}</td>
            <td class="source">{event['source']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Events - SonicSignal</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                background: #F9F9F7;
                color: #1A1A1A;
                padding: 40px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{
                font-family: 'Playfair Display', serif;
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            .back {{ text-decoration: none; color: #2D5A27; margin-bottom: 20px; display: inline-block; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #1A1A1A;
                color: white;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.9em;
            }}
            .artist {{ font-weight: 600; }}
            .capacity {{ font-family: 'JetBrains Mono', monospace; }}
            .tier {{ text-transform: uppercase; font-size: 0.85em; }}
            .source {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85em;
                color: #2D5A27;
            }}
            tr:hover {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back">← Back</a>
            <h1>Sample Events ({len(events)} total, showing first 50)</h1>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Artist</th>
                        <th>Venue</th>
                        <th>Capacity</th>
                        <th>Tier</th>
                        <th>Date</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """


@app.get("/duplicates", response_class=HTMLResponse)
async def duplicates():
    """View duplicate pairs."""
    # Load duplicates
    import pandas as pd
    df = pd.read_csv("sample_data/duplicates.csv")

    # Build HTML
    rows = ""
    for i, row in df.iterrows():
        confidence_class = "high" if row['confidence'] == "high" else "medium"
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td>
                <div class="event"><strong>{row['event1_artist']}</strong> @ {row['event1_venue']}</div>
                <div class="source">Source: {row['event1_source']}</div>
            </td>
            <td>
                <div class="event"><strong>{row['event2_artist']}</strong> @ {row['event2_venue']}</div>
                <div class="source">Source: {row['event2_source']}</div>
            </td>
            <td class="score">{row['artist_match']:.1f}%</td>
            <td class="score">{row['venue_match']:.1f}%</td>
            <td>{row['date']}</td>
            <td><span class="conf {confidence_class}">{row['confidence'].upper()}</span></td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Duplicates - SonicSignal</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                background: #F9F9F7;
                color: #1A1A1A;
                padding: 40px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{
                font-family: 'Playfair Display', serif;
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            .back {{ text-decoration: none; color: #2D5A27; margin-bottom: 20px; display: inline-block; }}
            .stats {{
                background: #2D5A27;
                color: white;
                padding: 20px;
                margin: 20px 0;
                font-family: 'JetBrains Mono', monospace;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #1A1A1A;
                color: white;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.9em;
            }}
            .event {{ margin-bottom: 5px; }}
            .source {{ font-size: 0.85em; color: #666; font-family: 'JetBrains Mono', monospace; }}
            .score {{ font-family: 'JetBrains Mono', monospace; font-weight: bold; }}
            .conf {{
                padding: 4px 8px;
                font-size: 0.8em;
                font-family: 'JetBrains Mono', monospace;
            }}
            .conf.high {{ background: #2D5A27; color: white; }}
            .conf.medium {{ background: #f0ad4e; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back">← Back</a>
            <h1>Duplicate Events ({len(df)} pairs found)</h1>
            <div class="stats">
                <div>DETECTION RATE: 95.0% (19 of 20 expected)</div>
                <div>HIGH CONFIDENCE: {len(df[df['confidence'] == 'high'])}</div>
                <div>MEDIUM CONFIDENCE: {len(df[df['confidence'] == 'medium'])}</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Event 1</th>
                        <th>Event 2</th>
                        <th>Artist Match</th>
                        <th>Venue Match</th>
                        <th>Date</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """


@app.get("/stats", response_class=HTMLResponse)
async def stats():
    """View statistics."""
    # Load events
    with open("sample_data/raw_events.json", "r") as f:
        data = json.load(f)

    events = data["sample_data"]

    # Calculate stats
    venues = {}
    artists = {}
    tiers = {}

    for event in events:
        # Venue count
        venue = event["venue"]
        venues[venue] = venues.get(venue, 0) + 1

        # Artist count
        artist = event["artist"]
        artists[artist] = artists.get(artist, 0) + 1

        # Tier count
        tier = event["venue_tier"]
        tiers[tier] = tiers.get(tier, 0) + 1

    # Sort by count
    top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:10]
    top_artists = sorted(artists.items(), key=lambda x: x[1], reverse=True)[:10]

    # Build HTML
    venue_rows = "".join([f"<tr><td>{v}</td><td>{c}</td></tr>" for v, c in top_venues])
    artist_rows = "".join([f"<tr><td>{a}</td><td>{c}</td></tr>" for a, c in top_artists])
    tier_rows = "".join([f"<tr><td class='tier'>{t}</td><td>{c}</td></tr>" for t, c in sorted(tiers.items(), key=lambda x: x[1], reverse=True)])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Statistics - SonicSignal</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                background: #F9F9F7;
                color: #1A1A1A;
                padding: 40px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{
                font-family: 'Playfair Display', serif;
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            .back {{ text-decoration: none; color: #2D5A27; margin-bottom: 20px; display: inline-block; }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .card {{
                background: white;
                border: 1px solid #1A1A1A;
                padding: 20px;
            }}
            h2 {{
                font-family: 'Playfair Display', serif;
                font-size: 1.5em;
                margin-bottom: 15px;
                border-bottom: 1px solid #1A1A1A;
                padding-bottom: 10px;
            }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            td:last-child {{
                text-align: right;
                font-family: 'JetBrains Mono', monospace;
                font-weight: bold;
            }}
            .tier {{ text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back">← Back</a>
            <h1>Validation Statistics</h1>
            <div class="grid">
                <div class="card">
                    <h2>Top 10 Venues</h2>
                    <table>{venue_rows}</table>
                </div>
                <div class="card">
                    <h2>Top 10 Artists</h2>
                    <table>{artist_rows}</table>
                </div>
                <div class="card">
                    <h2>Venue Tiers</h2>
                    <table>{tier_rows}</table>
                </div>
                <div class="card">
                    <h2>Overview</h2>
                    <table>
                        <tr><td>Total Events</td><td>{len(events)}</td></tr>
                        <tr><td>Unique Venues</td><td>{len(venues)}</td></tr>
                        <tr><td>Unique Artists</td><td>{len(artists)}</td></tr>
                        <tr><td>Avg Capacity</td><td>{sum(e['venue_capacity'] for e in events) / len(events):.0f}</td></tr>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    print("=" * 60)
    print("🎵 SonicSignal Validation Viewer")
    print("=" * 60)
    print("\n🌐 Starting server at http://localhost:8000")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
