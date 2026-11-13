import streamlit as st
import requests
import pandas as pd
from collections import Counter

st.set_page_config(
    page_title="FPL Mini-League Differential Tracker",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ FPL Mini-League Differential Tracker")
st.markdown("Identify low-ownership, high-scoring players (differentials) within your **FPL Classic** or **Draft** mini-league.")

# User inputs
col1, col2 = st.columns(2)
with col1:
    league_id = st.number_input("League ID", min_value=1, value=19308, step=1, help="Find this in the URL of your mini-league standings page")
with col2:
    gameweek_id = st.number_input("Gameweek ID", min_value=1, max_value=38, value=10, step=1)

with st.expander("⚙️ Advanced Settings"):
    count_bench = st.checkbox("Count bench players toward mini-league ownership", value=True)
    max_ownership = st.number_input("Max Mini-League Ownership Count (0 = no limit)", min_value=0, value=0, step=1, help="e.g., set to 1 to only show unique 1-of-1 differential picks")
    top_n = st.slider("Number of differentials to show", min_value=5, max_value=50, value=15)

if st.button("🚀 Find Differentials", type="primary"):
    headers = {"User-Agent": "Mozilla/5.0"}
    fpl_base = "https://fantasy.premierleague.com/api"
    draft_base = "https://draft.premierleague.com/api"

    with st.spinner("Fetching player data from FPL API..."):
        try:
            # 1. Fetch player names
            bootstrap = requests.get(f"{fpl_base}/bootstrap-static/", headers=headers).json()
            player_names = {p["id"]: p["web_name"] for p in bootstrap["elements"]}

            # 2. Fetch Gameweek points
            live_data = requests.get(f"{fpl_base}/event/{gameweek_id}/live/", headers=headers).json()
            player_points = {p["id"]: p["stats"]["total_points"] for p in live_data["elements"]}

            # 3. Fetch Mini-League entries (Classic first with pagination, fallback to Draft)
            classic_resp = requests.get(f"{fpl_base}/leagues-classic/{league_id}/standings/?page_standings=1", headers=headers)

            if classic_resp.status_code == 200:
                entries = []
                page = 1
                mode = "Classic"
                while True:
                    if page > 1:
                        classic_resp = requests.get(
                            f"{fpl_base}/leagues-classic/{league_id}/standings/?page_standings={page}",
                            headers=headers
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

                picks_template = f"{fpl_base}/entry/{{entry_id}}/event/{gameweek_id}/picks/"
            else:
                draft_resp = requests.get(f"{draft_base}/league/{league_id}/details", headers=headers)
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
                picks_template = f"{draft_base}/entry/{{entry_id}}/event/{gameweek_id}"
                mode = "Draft"

            total_teams = len(entries)
            ownership_counts = Counter()
            team_active_picks = []

            # 4. Collect picks across all teams
            progress_bar = st.progress(0, text="Analyzing team picks...")
            for i, entry in enumerate(entries):
                picks_resp = requests.get(picks_template.format(entry_id=entry["entry_id"]), headers=headers)
                if picks_resp.status_code == 200:
                    picks = picks_resp.json()["picks"]
                    for pick in picks:
                        pid = pick["element"]
                        is_active = pick.get("multiplier", 1 if pick.get("position", 12) <= 11 else 0) > 0

                        if count_bench or is_active:
                            ownership_counts[pid] += 1

                        if is_active:
                            team_active_picks.append({
                                "team": entry["team"],
                                "manager": entry["manager"],
                                "pid": pid,
                                "player": player_names.get(pid, f"ID {pid}"),
                                "points": player_points.get(pid, 0),
                            })
                progress_bar.progress((i + 1) / total_teams, text=f"Analyzed {i + 1}/{total_teams} teams...")

            # 5. Filter and rank candidates
            candidates = []
            max_limit = max_ownership if max_ownership > 0 else None
            for item in team_active_picks:
                owned_by = ownership_counts[item["pid"]]
                if max_limit and owned_by > max_limit:
                    continue
                if item["points"] <= 0:
                    continue

                item["owned_by"] = owned_by
                item["league_ownership_pct"] = round((owned_by / total_teams) * 100, 1)
                candidates.append(item)

            candidates.sort(key=lambda x: (x["owned_by"], -x["points"]))

            # Display results
            st.success(f"### {league_name} ({mode} | {total_teams} Teams) — GW{gameweek_id}")

            if not candidates:
                st.warning("No differentials found with positive points for this gameweek.")
            else:
                top_candidates = candidates[:top_n]
                table_data = []
                for rank, c in enumerate(top_candidates, start=1):
                    table_data.append({
                        "Rank": rank,
                        "Player": c["player"],
                        "Points": c["points"],
                        "Ownership": f"{c['owned_by']}/{total_teams} ({c['league_ownership_pct']}%)",
                        "Team": c["team"],
                        "Manager": c["manager"],
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"fpl_differentials_league_{league_id}_gw{gameweek_id}.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Error fetching data: {e}")
