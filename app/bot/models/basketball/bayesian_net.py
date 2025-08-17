from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from app.bot.models.base_models import BaseBayesianNetwork

class BasketballBayesianNetwork(BaseBayesianNetwork):
    def create_network(self):
        model = BayesianNetwork([
            ('team_form', 'bet_risk'),
            ('player_injuries', 'bet_risk'),
            ('home_advantage', 'bet_risk'),
            ('betting_odds', 'bet_risk'),
            ('rest_days', 'bet_risk'),
            ('opponent_strength', 'bet_risk'),
            ('recent_head_to_head', 'bet_risk'),
            ('match_importance', 'bet_risk'),
        ])

        cpd_team_form = TabularCPD('team_form', 3, [[0.412], [0.468], [0.12]],
            state_names={'team_form': ['good', 'average', 'poor']})

        cpd_player_injuries = TabularCPD('player_injuries', 3, [[0.0], [0.0526], [0.9474]],
            state_names={'player_injuries': ['none', 'minor', 'major']})

        cpd_home_advantage = TabularCPD('home_advantage', 2, [[1.0], [0.0]],
            state_names={'home_advantage': ['yes', 'no']})

        cpd_betting_odds = TabularCPD('betting_odds', 3, [[0.4], [0.4], [0.2]],
            state_names={'betting_odds': ['low', 'medium', 'high']})

        cpd_rest_days = TabularCPD('rest_days', 3, [[0.028], [0.523], [0.449]],
            state_names={'rest_days': ['0-1', '2-3', '4+']})

        cpd_opponent_strength = TabularCPD('opponent_strength', 3, [[0.6744], [0.3206], [0.0049]],
            state_names={'opponent_strength': ['strong', 'average', 'weak']})

        cpd_recent_head_to_head = TabularCPD('recent_head_to_head', 3, [[0.5871], [0.0009], [0.412]],
            state_names={'recent_head_to_head': ['win', 'draw', 'loss']})

        cpd_match_importance = TabularCPD('match_importance', 3, [[0.3], [0.4], [0.3]],
            state_names={'match_importance': ['high', 'medium', 'low']})

        from itertools import product
        safe_probs = []
        risky_probs = []

        for tf, inj, home, odds, rest, opp, h2h, imp in product(
            range(3), range(3), range(2), range(3), range(3), range(3), range(3), range(3)
        ):
            safe = 0.5

            if tf == 0: safe += 0.1
            elif tf == 2: safe -= 0.1

            if inj == 0: safe += 0.05
            elif inj == 2: safe -= 0.05

            if home == 0: safe += 0.05
            else: safe -= 0.05

            if odds == 0: safe += 0.05
            elif odds == 2: safe -= 0.05

            if rest == 2: safe += 0.05
            elif rest == 0: safe -= 0.05

            if opp == 0: safe -= 0.1
            elif opp == 2: safe += 0.1

            if h2h == 0: safe += 0.05
            elif h2h == 2: safe -= 0.05

            if imp == 0: safe += 0.05
            elif imp == 2: safe -= 0.05

            safe = round(max(min(safe, 0.99), 0.01), 3)
            risky = round(1 - safe, 3)

            safe_probs.append(safe)
            risky_probs.append(risky)

        cpd_bet_risk = TabularCPD(
            variable='bet_risk',
            variable_card=2,
            values=[safe_probs, risky_probs],
            evidence=[
                'team_form', 'player_injuries', 'home_advantage',
                'betting_odds', 'rest_days', 'opponent_strength',
                'recent_head_to_head', 'match_importance'
            ],
            evidence_card=[3, 3, 2, 3, 3, 3, 3, 3],
            state_names={
                'bet_risk': ['safe', 'risky'],
                'team_form': ['good', 'average', 'poor'],
                'player_injuries': ['none', 'minor', 'major'],
                'home_advantage': ['yes', 'no'],
                'betting_odds': ['low', 'medium', 'high'],
                'rest_days': ['0-1', '2-3', '4+'],
                'opponent_strength': ['strong', 'average', 'weak'],
                'recent_head_to_head': ['win', 'draw', 'loss'],
                'match_importance': ['high', 'medium', 'low']
            }
        )

        model.add_cpds(
            cpd_team_form,
            cpd_player_injuries,
            cpd_home_advantage,
            cpd_betting_odds,
            cpd_rest_days,
            cpd_opponent_strength,
            cpd_recent_head_to_head,
            cpd_match_importance,
            cpd_bet_risk
        )

        model.check_model()
        return model
