from experta import *
from app.ai.base_models import BaseExpert
from app.ai.models.bayesian.basketball_bayesian_net import BasketballBayesianNetwork

class BasketballFact(Fact):
    pass

SPANISH_MAP = {
    'team_form': {'bueno': 'good', 'regular': 'average', 'malo': 'poor'},
    'player_injuries': {'ninguna': 'none', 'menor': 'minor', 'mayor': 'major'},
    'home_advantage': {'sí': 'yes', 'si': 'yes', 'no': 'no'},
    'betting_odds': {'bajas': 'low', 'medias': 'medium', 'altas': 'high'},
    'rest_days': {'0': '0-1', '1': '0-1', '2': '2-3', '3': '2-3', '4': '4+', '5': '4+', '6': '4+', '7': '4+'},
    'opponent_strength': {'fuerte': 'strong', 'promedio': 'average', 'débil': 'weak', 'debil': 'weak'},
    'recent_head_to_head': {'victoria': 'win', 'empate': 'draw', 'derrota': 'loss'},
    'match_importance': {'alta': 'high', 'media': 'medium', 'baja': 'low'}
}

VALID_STATES = {
    'team_form': ['good', 'average', 'poor'],
    'player_injuries': ['none', 'minor', 'major'],
    'home_advantage': ['yes', 'no'],
    'betting_odds': ['low', 'medium', 'high'],
    'rest_days': ['0-1', '2-3', '4+'],
    'opponent_strength': ['strong', 'average', 'weak'],
    'recent_head_to_head': ['win', 'draw', 'loss'],
    'match_importance': ['high', 'medium', 'low']
}

class BasketballExpert(BaseExpert):
    def __init__(self, bayes_net: BasketballBayesianNetwork):
        super().__init__()
        self.bayes_net = bayes_net
        self.reset()
        self.collected_data = {}

    def get_sport_name(self):
        return "Basketball"

    def get_next_question(self, facts, fact_cls=BasketballFact):
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
                return {
                    "message": f"Respuesta inválida para '{key}'. Opciones válidas: {', '.join(valid_options.keys())}.",
                    "is_final": False,
                    "next_fact": key
                }
            translated[key] = SPANISH_MAP[key][value_lc]

        for k, v in translated.items():
            if v not in VALID_STATES.get(k, []):
                return {
                    "message": f"Valor no válido para '{k}': {v}. Opciones válidas: {', '.join(VALID_STATES[k])}.",
                    "is_final": False,
                    "next_fact": k
                }

        self.declare(fact_cls(**translated))

        for previous_fact in facts[:-1]:
            self.declare(fact_cls(**{
                k: SPANISH_MAP.get(k, {}).get(v.strip().lower(), v.strip().lower())
                for k, v in previous_fact.items()
            }))

        self.run()

        for fact in self.facts.values():
            if "question" in fact:
                return {"question": fact["question"], "next_fact": fact["next_fact"]}
            if "result" in fact:
                return {"result": fact["result"]}

        return None

    @Rule(NOT(BasketballFact(team_form=W())))
    def ask_team_form(self):
        self.declare(Fact(
            question="¿Cómo ha sido el rendimiento reciente del equipo?\n(bueno: ha ganado la mayoría de los últimos partidos, regular: resultados mixtos, malo: ha perdido la mayoría)",
            next_fact="team_form"
        ))

    @Rule(BasketballFact(team_form=MATCH.form), NOT(BasketballFact(player_injuries=W())))
    def ask_player_injuries(self, form):
        self.collected_data["team_form"] = form
        self.declare(Fact(
            question="¿Qué nivel de lesiones tiene el equipo?\n(ninguna: todos disponibles, menor: lesiones leves o suplentes, mayor: titulares clave ausentes)",
            next_fact="player_injuries"
        ))

    @Rule(BasketballFact(player_injuries=MATCH.injuries), NOT(BasketballFact(home_advantage=W())))
    def ask_home_advantage(self, injuries):
        self.collected_data["player_injuries"] = injuries
        self.declare(Fact(
            question="¿El equipo juega en casa?\n(sí, no)",
            next_fact="home_advantage"
        ))

    @Rule(BasketballFact(home_advantage=MATCH.home), NOT(BasketballFact(betting_odds=W())))
    def ask_betting_odds(self, home):
        self.collected_data["home_advantage"] = home
        self.declare(Fact(
            question="¿Cómo son las cuotas para el equipo?\n(bajas: <1.5, medias: 1.5–2.5, altas: >2.5)",
            next_fact="betting_odds"
        ))

    @Rule(BasketballFact(betting_odds=MATCH.odds), NOT(BasketballFact(rest_days=W())))
    def ask_rest_days(self, odds):
        self.collected_data["betting_odds"] = odds
        self.declare(Fact(
            question="¿Cuántos días de descanso ha tenido el equipo antes del partido?\n(0–7 días)",
            next_fact="rest_days"
        ))

    @Rule(BasketballFact(rest_days=MATCH.rest), NOT(BasketballFact(opponent_strength=W())))
    def ask_opponent_strength(self, rest):
        self.collected_data["rest_days"] = rest
        self.declare(Fact(
            question="¿Qué tan fuerte es el rival?\n(fuerte: buen rendimiento o ranking, promedio, débil: en mala racha)",
            next_fact="opponent_strength"
        ))

    @Rule(BasketballFact(opponent_strength=MATCH.opp), NOT(BasketballFact(recent_head_to_head=W())))
    def ask_recent_head_to_head(self, opp):
        self.collected_data["opponent_strength"] = opp
        self.declare(Fact(
            question="¿Cuál fue el resultado más reciente entre estos equipos?\n(victoria, empate, derrota)",
            next_fact="recent_head_to_head"
        ))

    @Rule(BasketballFact(recent_head_to_head=MATCH.h2h), NOT(BasketballFact(match_importance=W())))
    def ask_match_importance(self, h2h):
        self.collected_data["recent_head_to_head"] = h2h
        self.declare(Fact(
            question="¿Qué importancia tiene este partido?\n(alta: decisivo, media: relevante, baja: amistoso o irrelevante)",
            next_fact="match_importance"
        ))

    @Rule(
        BasketballFact(team_form=MATCH.form),
        BasketballFact(player_injuries=MATCH.injuries),
        BasketballFact(home_advantage=MATCH.home),
        BasketballFact(betting_odds=MATCH.odds),
        BasketballFact(rest_days=MATCH.rest),
        BasketballFact(opponent_strength=MATCH.opp),
        BasketballFact(recent_head_to_head=MATCH.h2h),
        BasketballFact(match_importance=MATCH.importance)
    )
    def give_final_recommendation(self, form, injuries, home, odds, rest, opp, h2h, importance):
        self.collected_data.update({
            "team_form": form,
            "player_injuries": injuries,
            "home_advantage": home,
            "betting_odds": odds,
            "rest_days": rest,
            "opponent_strength": opp,
            "recent_head_to_head": h2h,
            "match_importance": importance
        })

        prediction = self.bayes_net.inference.query(
            variables=["bet_risk"],
            evidence=self.collected_data
        )

        values = prediction.values
        prob_safe = round(values[0] * 100, 2)
        label = prediction.state_names["bet_risk"][values.argmax()]
        label_es = "segura" if label == "safe" else "arriesgada"

        factores = []

        # Solo incluir factores que empujan hacia la decisión final
        if label == "safe":
            if form == "good":
                factores.append("el equipo llega en buena forma")
            if injuries in ["none", "minor"]:
                factores.append("no tiene jugadores lesionados" if injuries == "none" else "solo tiene lesiones menores")
            if home == "yes":
                factores.append("juega como local")
            if odds == "low":
                factores.append("las cuotas reflejan alta probabilidad de victoria")
            if rest == "4+":
                factores.append("el equipo ha tenido buen descanso")
            if opp == "weak":
                factores.append("el rival está en mala forma")
            if h2h == "win":
                factores.append("ha ganado recientemente contra este rival")
            if importance == "high":
                factores.append("el partido es decisivo")

        elif label == "risky":
            if form == "poor":
                factores.append("el equipo ha tenido un mal rendimiento reciente")
            if injuries == "major":
                factores.append("tiene jugadores titulares lesionados")
            if home == "no":
                factores.append("juega como visitante")
            if odds == "high":
                factores.append("las cuotas son altas, lo que sugiere baja probabilidad")
            if rest == "0-1":
                factores.append("el equipo llega con poco descanso")
            if opp == "strong":
                factores.append("el rival es fuerte")
            if h2h == "loss":
                factores.append("ha perdido recientemente contra este rival")
            if importance == "low":
                factores.append("el partido no tiene mucha importancia")

        formatted_causes = "\n- " + "\n- ".join(factores)

        explanation = (
            f"Se considera una apuesta **{label_es}**, con una probabilidad de éxito del {prob_safe}%\n"
            f"Esto se debe a:{formatted_causes}"
        )

        self.declare(Fact(result=explanation))
