"""
Synthetic football player dataset generator.
Run once to produce football_players.csv.
DATA IS SYNTHETIC — not based on any real players or real-world results.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

SEASONS = ["2021/22", "2022/23", "2023/24"]

CLUBS = [
    "FC Ironclad",
    "United Wanderers",
    "Riverside Athletic",
    "Northern Wolves",
    "Southgate City",
    "Eastfield United",
    "Western Rangers",
    "Blackmoor FC",
    "Crestview Athletic",
    "Thornton City",
]

POSITIONS = ["GK", "DEF", "MID", "FWD"]

# Realistic squad composition per club (total ~100 players across 10 clubs)
POSITION_COUNTS = {"GK": 3, "DEF": 8, "MID": 8, "FWD": 6}  # 25 per club × 10 = 250? no — we want 100 total
# 10 players per club: 1 GK, 3 DEF, 4 MID, 2 FWD  → 100 players
SQUAD = {"GK": 1, "DEF": 3, "MID": 4, "FWD": 2}

FIRST_NAMES = [
    "Luca", "Marco", "Carlos", "James", "Pierre", "Diego", "Mateo",
    "Kai", "Noah", "Leon", "Finn", "Erik", "Ali", "Omar", "Yusuf",
    "Tomas", "Ivan", "Nikola", "Bruno", "Sergio", "Raul", "Theo",
    "Oliver", "Felix", "Hugo", "Emil", "Max", "Joel", "Simon", "Rafi",
]
LAST_NAMES = [
    "Silva", "Müller", "Fernandez", "Johnson", "Dubois", "Rossi", "García",
    "Havertz", "Santos", "Becker", "Hansen", "Eriksson", "Hassan", "Diallo",
    "Yilmaz", "Novak", "Petrov", "Kovač", "Costa", "Moreno", "Ramos", "Henry",
    "Clarke", "Weber", "Blanc", "Lindqvist", "Braun", "Larsson", "Andersen", "Nkosi",
]


def generate_player_roster():
    """Build a fixed 100-player roster with club and position assignments."""
    rng = np.random.default_rng(42)
    players = []
    pid = 1
    for club in CLUBS:
        for pos, count in SQUAD.items():
            for _ in range(count):
                fn = FIRST_NAMES[rng.integers(0, len(FIRST_NAMES))]
                ln = LAST_NAMES[rng.integers(0, len(LAST_NAMES))]
                name = f"{fn} {ln}"
                age_base = int(rng.integers(18, 33))
                players.append({"player_id": pid, "player_name": name, "team": club,
                                 "position": pos, "age_base": age_base})
                pid += 1
    return players


# Position-weighted stat parameters: (low, high) for Poisson lambda or uniform range
STAT_PARAMS = {
    #              matches  goals    assists  shots   passes  dribbles  tackles  yellow  red
    "GK":  dict(matches=(20, 38), goals=(0, 0),  assists=(0, 1),  shots=(0, 1),   passes=(30, 55), dribbles=(0, 2),  tackles=(0, 3),  yellow=(0, 3), red=(0, 1)),
    "DEF": dict(matches=(15, 38), goals=(0, 4),  assists=(0, 5),  shots=(0, 8),   passes=(40, 70), dribbles=(5, 20), tackles=(30, 80),yellow=(1, 6), red=(0, 1)),
    "MID": dict(matches=(15, 38), goals=(2, 12), assists=(3, 14), shots=(20, 60), passes=(60, 120),dribbles=(20, 60),tackles=(20, 60),yellow=(1, 5), red=(0, 1)),
    "FWD": dict(matches=(15, 38), goals=(5, 25), assists=(2, 10), shots=(40, 120),passes=(20, 60), dribbles=(30, 70),tackles=(5, 20), yellow=(1, 4), red=(0, 1)),
}


def sample_stats(pos, rng, season_idx):
    """Sample one season's worth of stats for a player of the given position."""
    p = STAT_PARAMS[pos]
    matches = int(rng.integers(p["matches"][0], p["matches"][1] + 1))
    avg_mins = rng.uniform(55, 90)
    minutes = int(round(matches * avg_mins))

    goals   = int(rng.integers(p["goals"][0],   p["goals"][1]   + 1))
    assists = int(rng.integers(p["assists"][0],  p["assists"][1] + 1))

    # shots must be >= goals with realistic conversion rate
    min_shots = max(goals, p["shots"][0])
    shots = int(rng.integers(min_shots, max(min_shots + 1, p["shots"][1] + 1)))
    shots_on_target = int(round(shots * rng.uniform(0.30, 0.60)))
    shots_on_target = max(shots_on_target, goals)  # can't score without hitting target

    passes   = int(rng.integers(p["passes"][0],   p["passes"][1]   + 1))
    pass_acc = round(float(rng.uniform(0.62, 0.94)), 3)
    dribbles = int(rng.integers(p["dribbles"][0], p["dribbles"][1] + 1))
    tackles  = int(rng.integers(p["tackles"][0],  p["tackles"][1]  + 1))
    yellow   = int(rng.integers(p["yellow"][0],   p["yellow"][1]   + 1))
    red      = int(rng.integers(p["red"][0],       p["red"][1]      + 1))

    # Apply mild season-to-season trend (improves in s1, peaks s2, slight regression s3)
    trend = [0.90, 1.0, 0.95][season_idx]
    goals   = max(0, int(round(goals   * trend)))
    assists = max(0, int(round(assists * trend)))
    shots   = max(goals, int(round(shots * trend)))
    shots_on_target = max(goals, int(round(shots_on_target * trend)))

    # Rating: weighted composite, normalised to [5.0, 9.5]
    g_w   = min(goals   / 25, 1.0) * 0.30
    a_w   = min(assists / 15, 1.0) * 0.20
    pa_w  = (pass_acc - 0.60) / 0.34 * 0.20
    t_w   = min(tackles / 80, 1.0) * 0.15
    d_w   = min(dribbles / 70, 1.0) * 0.15
    raw   = g_w + a_w + pa_w + t_w + d_w          # 0..1
    noise = float(rng.uniform(-0.03, 0.03))
    rating = round(5.0 + raw * 4.5 + noise * 4.5, 2)
    rating = max(5.0, min(9.5, rating))

    return {
        "matches_played":   matches,
        "minutes_played":   minutes,
        "goals":            goals,
        "assists":          assists,
        "shots":            shots,
        "shots_on_target":  shots_on_target,
        "passes":           passes,
        "pass_accuracy":    pass_acc,
        "dribbles":         dribbles,
        "tackles":          tackles,
        "yellow_cards":     yellow,
        "red_cards":        red,
        "rating":           rating,
    }


def build_dataset():
    rng = np.random.default_rng(42)
    roster = generate_player_roster()
    rows = []
    for season_idx, season in enumerate(SEASONS):
        for player in roster:
            stats = sample_stats(player["position"], rng, season_idx)
            row = {
                "player_id":   player["player_id"],
                "player_name": player["player_name"],
                "season":      season,
                "team":        player["team"],
                "position":    player["position"],
                "age":         player["age_base"] + season_idx,
            }
            row.update(stats)
            rows.append(row)

    df = pd.DataFrame(rows)

    # Enforce column order
    col_order = [
        "player_id", "player_name", "season", "team", "position", "age",
        "matches_played", "minutes_played", "goals", "assists",
        "shots", "shots_on_target", "passes", "pass_accuracy",
        "dribbles", "tackles", "yellow_cards", "red_cards", "rating",
    ]
    df = df[col_order]
    return df


if __name__ == "__main__":
    df = build_dataset()
    df.to_csv("football_players.csv", index=False)
    print(f"[OK] Generated football_players.csv")
    print(f"   Rows    : {len(df)}")
    print(f"   Columns : {list(df.columns)}")
    print(f"   Seasons : {df['season'].unique().tolist()}")
    print(f"   Teams   : {df['team'].nunique()} clubs")
    print(f"   Players : {df['player_id'].nunique()} unique players")
    print(df.describe(include='all').to_string())
