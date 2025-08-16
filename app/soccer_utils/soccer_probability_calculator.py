import pandas as pd
import numpy as np
from collections import defaultdict

# Cargar datos y tomar muestra aleatoria
data = pd.read_csv('results.csv')
if len(data) > 2000:
    data = data.sample(2000, random_state=42).reset_index(drop=True)

data['date'] = pd.to_datetime(data['date'])

# Precalcular partidos por equipo y por par de equipos
team_matches = defaultdict(list)
pair_matches = defaultdict(list)
for idx, row in data.iterrows():
    team_matches[row['home_team']].append((row['date'], idx))
    team_matches[row['away_team']].append((row['date'], idx))
    key1 = (row['home_team'], row['away_team'])
    key2 = (row['away_team'], row['home_team'])
    pair_matches[key1].append((row['date'], idx))
    pair_matches[key2].append((row['date'], idx))

# 1. Probabilidad de victoria según localía
def get_result(row):
    if row['home_score'] > row['away_score']:
        return 'home_win'
    elif row['home_score'] < row['away_score']:
        return 'away_win'
    else:
        return 'draw'

data['result'] = data.apply(get_result, axis=1)
data['venue'] = data['neutral'].map({True: 'neutral', False: 'home', 1: 'neutral', 0: 'home', 'TRUE': 'neutral', 'FALSE': 'home'})
data.loc[data['venue'].isna(), 'venue'] = 'home'

venue_win_probs = []
for venue in ['home', 'neutral']:
    total = len(data[data['venue'] == venue])
    wins = len(data[(data['venue'] == venue) & (data['result'] == 'home_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    venue_win_probs.append({'factor': 'venue', 'state': venue, 'win_probability': prob})
total_away = len(data[data['venue'] == 'home'])
away_wins = len(data[(data['venue'] == 'home') & (data['result'] == 'away_win')])
venue_win_probs.append({'factor': 'venue', 'state': 'away', 'win_probability': round(away_wins / total_away, 4) if total_away > 0 else 0})

# 2. Probabilidad de victoria según racha reciente
def get_streak(team, date):
    partidos = sorted([d for d, idx in team_matches[team] if d < date], reverse=True)
    if len(partidos) < 3:
        return 'neutral'
    idxs = [idx for d, idx in team_matches[team] if d in partidos[:3]]
    prev = data.loc[idxs]
    wins = 0
    losses = 0
    for _, row in prev.iterrows():
        if row['home_team'] == team and row['home_score'] > row['away_score']:
            wins += 1
        elif row['away_team'] == team and row['away_score'] > row['home_score']:
            wins += 1
        elif row['home_team'] == team and row['home_score'] < row['away_score']:
            losses += 1
        elif row['away_team'] == team and row['away_score'] < row['home_score']:
            losses += 1
    if wins >= 2:
        return 'good'
    elif losses >= 2:
        return 'bad'
    else:
        return 'neutral'

data['home_streak'] = data.apply(lambda row: get_streak(row['home_team'], row['date']), axis=1)
data['away_streak'] = data.apply(lambda row: get_streak(row['away_team'], row['date']), axis=1)

streak_win_probs = []
for streak in ['good', 'neutral', 'bad']:
    total = len(data[data['home_streak'] == streak])
    wins = len(data[(data['home_streak'] == streak) & (data['result'] == 'home_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    streak_win_probs.append({'factor': 'home_streak', 'state': streak, 'win_probability': prob})
    total = len(data[data['away_streak'] == streak])
    wins = len(data[(data['away_streak'] == streak) & (data['result'] == 'away_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    streak_win_probs.append({'factor': 'away_streak', 'state': streak, 'win_probability': prob})

# 3. Probabilidad de victoria según importancia del partido
data['importance'] = data['tournament'].apply(lambda x: 'low' if str(x).lower() == 'friendly' else 'high')
importance_win_probs = []
for imp in ['low', 'high']:
    total = len(data[data['importance'] == imp])
    wins = len(data[(data['importance'] == imp) & (data['result'] == 'home_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    importance_win_probs.append({'factor': 'importance', 'state': imp, 'win_probability': prob})

# 4. Historial directo (head-to-head)
def get_h2h_win_rate(row, n=5):
    key = (row['home_team'], row['away_team'])
    partidos = sorted([d for d, idx in pair_matches[key] if d < row['date']], reverse=True)
    if len(partidos) == 0:
        return None
    idxs = [idx for d, idx in pair_matches[key] if d in partidos[:n]]
    prev = data.loc[idxs]
    wins = 0
    total = 0
    for _, match in prev.iterrows():
        if match['home_team'] == row['home_team'] and match['result'] == 'home_win':
            wins += 1
        elif match['away_team'] == row['home_team'] and match['result'] == 'away_win':
            wins += 1
        total += 1
    return wins / total if total > 0 else None

data['h2h_win_rate'] = data.apply(get_h2h_win_rate, axis=1)

def h2h_group(val):
    if pd.isna(val):
        return 'no_data'
    elif val >= 0.6:
        return 'alta'
    elif val >= 0.3:
        return 'media'
    else:
        return 'baja'

data['h2h_group'] = data['h2h_win_rate'].apply(h2h_group)
h2h_win_probs = []
for group in ['alta', 'media', 'baja', 'no_data']:
    total = len(data[data['h2h_group'] == group])
    wins = len(data[(data['h2h_group'] == group) & (data['result'] == 'home_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    h2h_win_probs.append({'factor': 'h2h_group', 'state': group, 'win_probability': prob})

# 5. Fatiga (días de descanso)
def get_last_match_date(team, current_date):
    partidos = sorted([d for d, idx in team_matches[team] if d < current_date], reverse=True)
    if not partidos:
        return None
    return partidos[0]

def get_days_rest(row):
    last_date = get_last_match_date(row['home_team'], row['date'])
    if pd.isna(last_date) or last_date is None:
        return None
    return (row['date'] - last_date).days

data['home_days_rest'] = data.apply(get_days_rest, axis=1)

def rest_group(val):
    if pd.isna(val):
        return 'no_data'
    elif val < 4:
        return 'menos_4'
    else:
        return 'cuatro_o_mas'

data['rest_group'] = data['home_days_rest'].apply(rest_group)
rest_win_probs = []
for group in ['menos_4', 'cuatro_o_mas', 'no_data']:
    total = len(data[data['rest_group'] == group])
    wins = len(data[(data['rest_group'] == group) & (data['result'] == 'home_win')])
    prob = round(wins / total, 4) if total > 0 else 0
    rest_win_probs.append({'factor': 'rest_group', 'state': group, 'win_probability': prob})

# Exportar a CSV
final = venue_win_probs + streak_win_probs + importance_win_probs + h2h_win_probs + rest_win_probs
df_final = pd.DataFrame(final)
df_final.to_csv('soccer_win_probabilities.csv', index=False)
print("✅ Probabilidades exportadas a soccer_win_probabilities.csv (muestra rápida)")