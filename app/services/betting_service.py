from app.core.exceptions import ExpertSystemError


class BettingService:
    """Service for handling betting-related operations."""
    
    def __init__(self):
        self._advisers = {}
    
    def get_adviser(self, sport: str):
        """Get or create a betting adviser for the specified sport."""
        sport_key = sport.lower()
        
        if sport_key not in self._advisers:
            try:
                from app.ai.betting_adviser import BettingAdviser
                self._advisers[sport_key] = BettingAdviser(sport_key)
            except Exception as e:
                raise ExpertSystemError(f"Failed to create adviser for {sport}: {str(e)}")
        
        return self._advisers[sport_key]
    
    def get_betting_advice(self, sport: str, facts: list) -> dict:
        """Get betting advice for the specified sport and facts."""
        try:
            adviser = self.get_adviser(sport)
            response = adviser.get_betting_advice(facts)
            
            if response is None:
                return {
                    "message": "No hay recomendaciones disponibles en este momento.",
                    "is_final": True,
                    "next_fact": None
                }
            
            return response
            
        except Exception as e:
            raise ExpertSystemError(f"Error getting betting advice: {str(e)}")
    
    def validate_sport(self, sport: str) -> bool:
        """Validate if the sport is supported."""
        supported_sports = ['soccer', 'basketball']
        return sport.lower() in supported_sports
