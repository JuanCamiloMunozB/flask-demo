from experta import *
from app.ai.base_models import BaseExpert
from app.ai.models.bayesian.soccer_bayesian_net import SoccerBayesianNetwork

SPANISH_MAP = {
    'home_advantage': {'sí': 'home', 'si': 'home', 'no': 'away'},
    'injuries': {'no': 'no', 'sí': 'yes', 'si': 'yes', 'yes': 'yes'},
    'performance': {'bajo': 'low', 'medio': 'medium', 'alto': 'high', 'baja': 'low', 'media': 'medium', 'alta': 'high'},
    'weather': {'no': 'no', 'sí': 'yes', 'si': 'yes', 'yes': 'yes'},
    'rivalry': {'no': 'no', 'sí': 'yes', 'si': 'yes', 'yes': 'yes'},
    'league_position': {'alta': 'high', 'media': 'medium', 'baja': 'low'},
    'recent_streak': {'ganadora': 'winning', 'neutral': 'neutral', 'perdedora': 'losing'},
    'match_importance': {'alta': 'high', 'media': 'medium', 'baja': 'low'},
    'physical_condition': {'descansado': 'rested', 'normal': 'normal', 'fatigado': 'fatigued'},
    'head_to_head': {'ventaja local': 'home_advantage', 'equilibrado': 'balanced', 'ventaja visitante': 'away_advantage'}
}

VALID_STATES = {
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

class SoccerFact(Fact):
    """Soccer-specific fact class."""
    pass

class SoccerExpert(BaseExpert):
    def __init__(self, bayes_net: SoccerBayesianNetwork):
        super().__init__()
        self.bayes_net = bayes_net
        self.reset()
        self.collected_data = {}

    def get_sport_name(self):
        return "Soccer"

    def get_next_question(self, facts):
        self.reset()
        self.collected_data = {}

        if not facts:
            self.run()
            for fact in self.facts.values():
                if "question" in fact:
                    return {"question": fact["question"], "next_fact": fact["next_fact"]}

        current_fact = facts[-1] if facts else {}
        translated = {}

        for key, value in current_fact.items():
            value_lc = value.strip().lower()
            valid_options = SPANISH_MAP.get(key, {})
            if value_lc not in valid_options:
                readable_options = ", ".join(valid_options.keys())
                return {
                    "message": f"Respuesta inválida para '{key}'. Opciones válidas: {readable_options}.",
                    "is_final": False,
                    "next_fact": key
                }
            translated[key] = SPANISH_MAP[key][value_lc]

        for k, v in translated.items():
            if v not in VALID_STATES.get(k, []):
                return {
                    "message": f"Valor no válido para '{k}': {v}. Opciones válidas: {', '.join(VALID_STATES[k])}",
                    "is_final": False,
                    "next_fact": k
                }

        self.declare(SoccerFact(**translated))

        for previous_fact in facts[:-1]:
            self.declare(SoccerFact(**{
                k: SPANISH_MAP.get(k, {}).get(v.strip().lower(), v.strip().lower())
                for k, v in previous_fact.items()
            }))

        self.run()

        for fact in self.facts.values():
            if isinstance(fact, Fact):
                if "question" in fact:
                    return {"question": fact["question"], "next_fact": fact["next_fact"]}
                if "result" in fact:
                    return {"result": fact["result"]}

        return None

    @Rule(NOT(SoccerFact(home_advantage=W())))
    def ask_home_advantage(self):
        self.declare(Fact(
            question="¿El equipo juega en casa? (sí, no)",
            next_fact="home_advantage"
        ))

    @Rule(SoccerFact(home_advantage=MATCH.home_advantage),
          NOT(SoccerFact(injuries=W())))
    def ask_injuries(self, home_advantage):
        self.collected_data["home_advantage"] = home_advantage
        self.declare(Fact(
            question="¿Hay jugadores lesionados importantes? (sí, no)",
            next_fact="injuries"
        ))

    @Rule(SoccerFact(injuries=MATCH.injuries),
          NOT(SoccerFact(performance=W())))
    def ask_performance(self, injuries):
        self.collected_data["injuries"] = injuries
        self.declare(Fact(
            question="¿Cómo ha sido el rendimiento reciente del equipo? (bajo, medio, alto)",
            next_fact="performance"
        ))

    @Rule(SoccerFact(performance=MATCH.performance),
          NOT(SoccerFact(weather=W())))
    def ask_weather(self, performance):
        self.collected_data["performance"] = performance
        self.declare(Fact(
            question="¿Hay condiciones climáticas adversas? (sí, no)",
            next_fact="weather"
        ))

    @Rule(SoccerFact(weather=MATCH.weather),
          NOT(SoccerFact(rivalry=W())))
    def ask_rivalry(self, weather):
        self.collected_data["weather"] = weather
        self.declare(Fact(
            question="¿Existe una rivalidad especial en este partido? (sí, no)",
            next_fact="rivalry"
        ))

    @Rule(SoccerFact(rivalry=MATCH.rivalry),
          NOT(SoccerFact(league_position=W())))
    def ask_league_position(self, rivalry):
        self.collected_data["rivalry"] = rivalry
        self.declare(Fact(
            question="¿Cuál es la posición del equipo en la tabla? (alta, media, baja)",
            next_fact="league_position"
        ))

    @Rule(SoccerFact(league_position=MATCH.league_position),
          NOT(SoccerFact(recent_streak=W())))
    def ask_recent_streak(self, league_position):
        self.collected_data["league_position"] = league_position
        self.declare(Fact(
            question="¿Cuál es la racha de resultados recientes? (ganadora, neutral, perdedora)",
            next_fact="recent_streak"
        ))

    @Rule(SoccerFact(recent_streak=MATCH.recent_streak),
          NOT(SoccerFact(match_importance=W())))
    def ask_match_importance(self, recent_streak):
        self.collected_data["recent_streak"] = recent_streak
        self.declare(Fact(
            question="¿Qué importancia tiene el partido? (alta, media, baja)",
            next_fact="match_importance"
        ))

    @Rule(SoccerFact(match_importance=MATCH.match_importance),
          NOT(SoccerFact(physical_condition=W())))
    def ask_physical_condition(self, match_importance):
        self.collected_data["match_importance"] = match_importance
        self.declare(Fact(
            question="¿Cuál es la condición física del equipo? (descansado, normal, fatigado)",
            next_fact="physical_condition"
        ))

    @Rule(SoccerFact(physical_condition=MATCH.physical_condition),
          NOT(SoccerFact(head_to_head=W())))
    def ask_head_to_head(self, physical_condition):
        self.collected_data["physical_condition"] = physical_condition
        self.declare(Fact(
            question="¿Cómo es el historial de enfrentamientos directos? (ventaja local, equilibrado, ventaja visitante)",
            next_fact="head_to_head"
        ))

    @Rule(SoccerFact(head_to_head=MATCH.head_to_head),
          SoccerFact(physical_condition=MATCH.physical_condition),
          SoccerFact(match_importance=MATCH.match_importance),
          SoccerFact(recent_streak=MATCH.recent_streak),
          SoccerFact(league_position=MATCH.league_position),
          SoccerFact(rivalry=MATCH.rivalry),
          SoccerFact(weather=MATCH.weather),
          SoccerFact(performance=MATCH.performance),
          SoccerFact(injuries=MATCH.injuries),
          SoccerFact(home_advantage=MATCH.home_advantage))
    def give_final_recommendation(self, head_to_head, physical_condition, match_importance, recent_streak, league_position, rivalry, weather, performance, injuries, home_advantage):
        self.collected_data.update({
            "home_advantage": home_advantage,
            "injuries": injuries,
            "performance": performance,
            "weather": weather,
            "rivalry": rivalry,
            "league_position": league_position,
            "recent_streak": recent_streak,
            "match_importance": match_importance,
            "physical_condition": physical_condition,
            "head_to_head": head_to_head
        })

        for key, val in self.collected_data.items():
            if val not in VALID_STATES.get(key, []):
                self.declare(Fact(result=f"Error: valor no válido '{val}' para '{key}'"))
                return

        prediction = self.bayes_net.inference.query(
            variables=["risk"],
            evidence=self.collected_data
        )

        values = prediction.values
        prob_safe = round(values[0] * 100, 2)
        label = prediction.state_names["risk"][values.argmax()]
        label_es = "segura" if label == "safe" else "arriesgada"

        explanation = (
            f"Se considera una apuesta **{label_es}**, con una probabilidad de éxito del {prob_safe}%.\n"
            f"Esto se debe a una combinación de factores: localía, lesiones, rendimiento, clima, rivalidad, posición en la tabla, racha, importancia del partido, condición física e historial directo."
        )

        self.declare(Fact(result=explanation))