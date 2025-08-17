import kagglehub
import sqlite3
import pandas as pd
from collections import Counter
from pathlib import Path

# Descargar el dataset
path = kagglehub.dataset_download("wyattowalsh/basketball")
db_path = Path(path) / "nba.sqlite"

# Conectar a SQLite
conn = sqlite3.connect(db_path)
games = pd.read_sql_query("SELECT * FROM game", conn)
inactive = pd.read_sql_query("SELECT * FROM inactive_players", conn)
conn.close()

games['game_date'] = pd.to_datetime(games['game_date'])
games.sort_values(by='game_date', inplace=True)

# Contadores por categoría
form_counter = Counter()
injury_counter = Counter()
home_advantage_counter = Counter()
rest_days_counter = Counter()
opponent_strength_counter = Counter()
head_to_head_counter = Counter()
importance_counter = Counter()

# team_form
team_games = games.groupby('team_id_home')
for _, group in team_games:
    group = group.sort_values('game_date')
    for idx in range(5, len(group)):
        last5 = group.iloc[idx - 5:idx]
        wins = (last5['wl_home'] == 'W').sum()
        if wins >= 4:
            form_counter.update(['good'])
        elif wins >= 2:
            form_counter.update(['average'])
        else:
            form_counter.update(['poor'])

# player_injuries
injuries_per_game = inactive.groupby('game_id').size()
for count in injuries_per_game:
    if count == 0:
        injury_counter.update(['none'])
    elif count <= 2:
        injury_counter.update(['minor'])
    else:
        injury_counter.update(['major'])

# home_advantage
home_advantage_counter.update(['yes'] * len(games))

# rest_days
for _, group in team_games:
    group = group.sort_values('game_date')
    group['prev_date'] = group['game_date'].shift(1)
    group = group.dropna()
    group['rest_days'] = (group['game_date'] - group['prev_date']).dt.days
    bins = pd.cut(group['rest_days'], [0, 1, 3, 100], labels=['0-1', '2-3', '4+'])
    rest_days_counter.update(bins.astype(str))

# opponent_strength
win_rates = games.groupby('team_id_home')['wl_home'].apply(lambda x: (x == 'W').mean())
for _, row in games.iterrows():
    opp_rate = win_rates.get(row['team_id_away'], 0)
    if opp_rate > 0.6:
        opponent_strength_counter.update(['strong'])
    elif opp_rate > 0.4:
        opponent_strength_counter.update(['average'])
    else:
        opponent_strength_counter.update(['weak'])

# recent_head_to_head
matchups = games.groupby(['team_id_home', 'team_id_away'])
for (_, _), group in matchups:
    group = group.sort_values('game_date')
    if len(group) > 1:
        last = group.iloc[-2]
        if last['wl_home'] == 'W':
            head_to_head_counter.update(['win'])
        else:
            head_to_head_counter.update(['loss'])
head_to_head_counter.update(['draw'])  # for completeness

# match_importance (aproximado)
importance_counter.update(['high'] * int(0.3 * len(games)))
importance_counter.update(['medium'] * int(0.4 * len(games)))
importance_counter.update(['low'] * (len(games) - sum(importance_counter.values())))

# Exportar como CSV
def format_probs(counter, var):
    total = sum(counter.values())
    return pd.DataFrame([{
        "variable": var,
        "state": state,
        "probability": round(count / total, 4)
    } for state, count in counter.items()])

frames = [
    format_probs(form_counter, "team_form"),
    format_probs(injury_counter, "player_injuries"),
    format_probs(home_advantage_counter, "home_advantage"),
    format_probs(rest_days_counter, "rest_days"),
    format_probs(opponent_strength_counter, "opponent_strength"),
    format_probs(head_to_head_counter, "recent_head_to_head"),
    format_probs(importance_counter, "match_importance")
]

final_df = pd.concat(frames, ignore_index=True)
final_df.to_csv("basketball_probabilities_full.csv", index=False)
print("✅ Probabilities saved to basketball_probabilities_full.csv")
