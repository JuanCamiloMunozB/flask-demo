from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from app.ai.base_models import BaseBayesianNetwork

class SoccerBayesianNetwork(BaseBayesianNetwork):
    """
    Enhanced Bayesian network for football betting with additional real-world variables.
    """
    def create_network(self):
        model = BayesianNetwork([
            ('home_advantage', 'risk'),
            ('injuries', 'risk'),
            ('performance', 'risk'),
            ('weather', 'risk'),
            ('rivalry', 'risk'),
            ('league_position', 'risk'),
            ('recent_streak', 'risk'),
            ('match_importance', 'risk'),
            ('physical_condition', 'risk'),
            ('head_to_head', 'risk')
        ])

        
        total = 0.4987 + 0.2635
        cpd_home_advantage = TabularCPD(
            variable='home_advantage', variable_card=2,
            values=[[0.4987 / total], [0.2635 / total]],  
            state_names={'home_advantage': ['home', 'away']}
        )

        cpd_injuries = TabularCPD(
            variable='injuries', variable_card=2,
            values=[[0.65], [0.35]],
            state_names={'injuries': ['no', 'yes']}
        )

        cpd_performance = TabularCPD(
            variable='performance', variable_card=3,
            values=[[0.2], [0.5], [0.3]],
            state_names={'performance': ['low', 'medium', 'high']}
        )

        cpd_weather = TabularCPD(
            variable='weather', variable_card=2,
            values=[[0.85], [0.15]], 
            state_names={'weather': ['no', 'yes']}
        )

        cpd_rivalry = TabularCPD(
            variable='rivalry', variable_card=2,
            values=[[0.6], [0.4]],  # ['no', 'yes']
            state_names={'rivalry': ['no', 'yes']}
        )

        cpd_league_position = TabularCPD(
            variable='league_position', variable_card=3,
            values=[[0.3], [0.4], [0.3]], 
            state_names={'league_position': ['high', 'medium', 'low']}
        )

        cpd_recent_streak = TabularCPD(
            variable='recent_streak', variable_card=3,
            values=[[0.25], [0.5], [0.25]],  
            state_names={'recent_streak': ['winning', 'neutral', 'losing']}
        )

       
        imp_high = 0.4809
        imp_low = 0.4681
        imp_medium = round((imp_high + imp_low) / 2, 4) 
        imp_total = imp_high + imp_medium + imp_low
        cpd_match_importance = TabularCPD(
            variable='match_importance', variable_card=3,
            values=[[imp_high / imp_total], [imp_medium / imp_total], [imp_low / imp_total]],  
            state_names={'match_importance': ['high', 'medium', 'low']}
        )

        # Cambiado según CSV: rest_group (normalizado)
        rest_total = 0.4667 + 0.4852 + 0.3438
        cpd_physical_condition = TabularCPD(
            variable='physical_condition', variable_card=3,
            values=[[0.4667 / rest_total], [0.4852 / rest_total], [0.3438 / rest_total]],  
            state_names={'physical_condition': ['rested', 'normal', 'fatigued']}
        )

        h2h_total = 0.5029 + 0.5974 + 0.4441
        cpd_head_to_head = TabularCPD(
            variable='head_to_head', variable_card=3,
            values=[[0.5029 / h2h_total], [0.5974 / h2h_total], [0.4441 / h2h_total]],  
            state_names={'head_to_head': ['home_advantage', 'balanced', 'away_advantage']}
        )

      
        safe = []
        risky = []

        from itertools import product
        for home_advantage, injury, performance, weather, rivalry, league_position, recent_streak, match_importance, physical_condition, head_to_head in product(
            ['home', 'away'],
            ['no', 'yes'],
            ['low', 'medium', 'high'],
            ['no', 'yes'],
            ['no', 'yes'],
            ['high', 'medium', 'low'],
            ['winning', 'neutral', 'losing'],
            ['high', 'medium', 'low'],
            ['rested', 'normal', 'fatigued'],
            ['home_advantage', 'balanced', 'away_advantage']
        ):
            risk = 0.0

            
            risk += 0.15 if home_advantage == 'away' else -0.1
            risk += 0.25 if injury == 'yes' else -0.05
            risk += 0.25 if performance == 'low' else (-0.05 if performance == 'high' else 0.0)
            risk += 0.2 if weather == 'yes' else -0.05
            risk += 0.1 if rivalry == 'yes' else -0.05

            
            risk += -0.1 if league_position == 'high' else (0.05 if league_position == 'low' else 0.0)
            risk += -0.1 if recent_streak == 'winning' else (0.1 if recent_streak == 'losing' else 0.0)
            risk += -0.05 if match_importance == 'high' else (0.05 if match_importance == 'low' else 0.0)
            risk += -0.1 if physical_condition == 'rested' else (0.1 if physical_condition == 'fatigued' else 0.0)
            risk += -0.05 if head_to_head == 'home_advantage' else (0.05 if head_to_head == 'away_advantage' else 0.0)

            risk = min(max(0.05 + risk, 0.01), 0.99)
            safe_prob = round(1 - risk, 3)
            risky_prob = round(risk, 3)

            safe.append(safe_prob)
            risky.append(risky_prob)

        cpd_risk = TabularCPD(
            variable='risk', variable_card=2,
            values=[safe, risky],
            evidence=[
                'home_advantage', 'injuries', 'performance', 'weather', 'rivalry',
                'league_position', 'recent_streak', 'match_importance',
                'physical_condition', 'head_to_head'
            ],
            evidence_card=[2, 2, 3, 2, 2, 3, 3, 3, 3, 3],
            state_names={
                'risk': ['safe', 'risky'],
                'home_advantage': ['home', 'away'],
                'injuries': ['no', 'yes'],
                'performance': ['low', 'medium', 'high'],
                'weather': ['no', 'yes'],
                'rivalry': ['no', 'yes'],
                'league_position': ['high', 'medium', 'low'],
                'recent_streak': ['winning', 'neutral', 'losing'],
                'match_importance': ['high', 'medium', 'low'],
                'physical_condition': ['rested', 'normal', 'fatigued'],
                'head_to_head': ['home_advantage', 'balanced', 'away_advantage']
            }
        )

        model.add_cpds(
            cpd_home_advantage, cpd_injuries, cpd_performance,
            cpd_weather, cpd_rivalry, cpd_league_position, cpd_recent_streak,
            cpd_match_importance, cpd_physical_condition, cpd_head_to_head, cpd_risk
        )
        assert model.check_model()
        return model