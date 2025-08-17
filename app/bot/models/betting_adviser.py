class BettingAdviser:
    """
    Betting adviser class to provide betting recommendations based on user input.
    This class uses a Bayesian network and an inference engine to analyze match conditions
    and provide betting advice.
    """
    
    _instances = {}

    def __new__(cls, sport):
        sport_key = sport.lower()
        if sport_key not in cls._instances:
            cls._instances[sport_key] = super(BettingAdviser, cls).__new__(cls)
            cls._instances[sport_key].initialize(sport_key)
        return cls._instances[sport_key]

    def initialize(self, sport):
        self.sport = sport
        self.expert = SportFactory.create_expert_system(sport)
    
    def get_betting_advice(self, facts):
        response = self.expert.get_next_question(facts)

        if response is None:
            return {
                "message": "No hay recomendaciones disponibles en este momento.",
                "is_final": True,
                "next_fact": None
            }

        if "message" in response and response.get("next_fact"):
            return {
                "message": response["message"],
                "is_final": False,
                "next_fact": response["next_fact"]
            }

        if "result" in response:
            return {
                "message": response["result"],
                "is_final": True,
                "next_fact": None
            }

        if "question" in response:
            return {
                "message": response["question"],
                "is_final": False,
                "next_fact": response["next_fact"]
            }

        return {
            "message": "No hay recomendaciones disponibles.",
            "is_final": True,
            "next_fact": None
        }


class SportFactory:
    """
    Factory class to create appropriate models based on sport selection.
    """

    @staticmethod
    def create_expert_system(sport):
        sport = sport.lower()
        
        if sport == "soccer":
            from app.bot.models.soccer.expert_system import SoccerExpert
            from app.bot.models.soccer.bayesian_net import SoccerBayesianNetwork
            return SoccerExpert(SoccerBayesianNetwork())
        
        elif sport == "basketball":
            from app.bot.models.basketball.expert_system import BasketballExpert
            from app.bot.models.basketball.bayesian_net import BasketballBayesianNetwork
            return BasketballExpert(BasketballBayesianNetwork())
        
        else:
            raise ValueError(f"Sport '{sport}' not supported")