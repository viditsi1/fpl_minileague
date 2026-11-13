#!/usr/bin/env python3
"""
FPL Mini-League Differential Tracker
Identifies low-ownership, high-scoring players (differentials) within your FPL Classic or Draft mini-league.
"""

from collections import Counter
import requests
import sys

# Prompt user for League ID and Gameweek ID
try:
    LEAGUE_ID = int(input("Enter League ID: "))
    GAMEWEEK_ID = int(input("Enter Gameweek ID: "))
except ValueError:
    print("Error: Please enter valid numbers for the League ID and Gameweek.")
    sys.exit(1)

COUNT_BENCH_IN_OWNERSHIP = True   # True = count all 15 squad spots; False = active starters only
MAX_LEAGUE_OWNERSHIP_COUNT = None # Set to 1 to only include unique 1-of-1 players, or None for all

headers = {"User-Agent": "Mozilla/5.0"}
fpl_base = "https://fantasy.premierleague.com/api"
draft_base = "https://draft.premierleague.com/api"

# 1. Fetch player names from bootstrap-static
print("\nFetching data, please wait...")
bootstrap = requests.get(f"{fpl_base}/bootstrap-static/", headers=headers).json()
player_names = {p["id"]: p["web_name"] for p in bootstrap["elements"]}

# 2. Fetch Gameweek points for all players
live_data = requests.get(f"{fpl_base}/event/{GAMEWEEK_ID}/live/", headers=headers).json()
player_points = {p["id"]: p["stats"]["total_points"] for p in live_data["elements"]}

# 3. Fetch Mini-League entries (Classic with pagination first, fallback to Draft)
classic_resp = requests.get(f"{fpl_base}/leagues-classic/{LEAGUE_ID}/standings/?page_standings=1", headers=headers)

if classic_resp.status_code == 200:
    entries = []
    page = 1
    mode = "Classic"
    while True:
        if page > 1:
            classic_resp = requests.get(
                f"{fpl_base}/leagues-classic/{LEAGUE_ID}/standings/?page_standings={page}",
                headers=headers,
            )
            if classic_resp.status_code != 200:
                break

        league_data = classic_resp.json()
        if page == 1:
            league_name = league_data["league"]["name"]

        entries.extend([
            {"entry_id": m["entry"], "team": m["entry_name"], "manager": m["player_name"]}
            for m in league_data["standings"]["results"]
        ])

        if not league_data["standings"].get("has_next"):
            break
        page += 1

    picks_template = f"{fpl_base}/entry/{{entry_id}}/event/{GAMEWEEK_ID}/picks/"
else:
    draft_resp = requests.get(f"{draft_base}/league/{LEAGUE_ID}/details", headers=headers)
    draft_resp.raise_for_status()
    league_data = draft_resp.json()
    league_name = league_data["league"]["name"]
    entries = [
        {
            "entry_id": m["entry_id"],
            "team": m["entry_name"],
            "manager": f"{m['player_first_name']} {m['player_last_name']}",
        }
        for m in league_data["league_entries"]
    ]
    picks_template = f"{draft_base}/entry/{{entry_id}}/event/{GAMEWEEK_ID}"
    mode = "Draft"

total_teams = len(entries)
ownership_counts = Counter()
team_active_picks = []

# 4. First pass: Collect picks and count ownership across the mini-league
for entry in entries:
    picks_resp = requests.get(picks_template.format(entry_id=entry["entry_id"]), headers=headers)
    if picks_resp.status_code != 200:
        continue

    picks = picks_resp.json()["picks"]
    for pick in picks:
        pid = pick["element"]
        is_active = pick.get("multiplier", 1 if pick.get("position", 12) <= 11 else 0) > 0

        if COUNT_BENCH_IN_OWNERSHIP or is_active:
            ownership_counts[pid] += 1

        if is_active:
            team_active_picks.append({
                "team": entry["team"],
                "manager": entry["manager"],
                "pid": pid,
                "player": player_names.get(pid, f"ID {pid}"),
                "points": player_points.get(pid, 0),
            })

# 5. Second pass: Attach mini-league ownership stats and filter
candidates = []
for item in team_active_picks:
    owned_by = ownership_counts[item["pid"]]
    if MAX_LEAGUE_OWNERSHIP_COUNT and owned_by > MAX_LEAGUE_OWNERSHIP_COUNT:
        continue
    if item["points"] <= 0:
        continue

    item["owned_by"] = owned_by
    item["league_ownership_pct"] = (owned_by / total_teams) * 100
    candidates.append(item)

# 6. Sort by Lowest Mini-League Ownership first, then Highest Points
candidates.sort(key=lambda x: (x["owned_by"], -x["points"]))

print(f"\n=== {league_name} ({mode} | {total_teams} Teams) | GW{GAMEWEEK_ID} Mini-League Differentials ===\n")
for rank, c in enumerate(candidates[:15], start=1):
    print(
        f"{rank:>2}. {c['player']:<15} | {c['points']:>2} pts | "
        f"Owned by {c['owned_by']}/{total_teams} ({c['league_ownership_pct']:>5.1f}%) | "
        f"{c['team']} ({c['manager']})"
    )
