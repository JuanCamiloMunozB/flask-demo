import pytest
from app.models.basketball.expert_system import BasketballExpert, SPANISH_MAP
from app.models.basketball.bayesian_net import BasketballBayesianNetwork
import re

class TestBasketballAdviser:
    @pytest.fixture
    def adviser(self):
        """Create a complete basketball adviser with real components."""
        bayes_net = BasketballBayesianNetwork()
        return BasketballExpert(bayes_net)
    
    def test_complete_conversation_flow(self, adviser):
        """Test the complete end-to-end conversation flow."""
        # Start with first question
        result = adviser.get_next_question([])
        assert "question" in result
        assert result["next_fact"] == "team_form"
        
        answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"match_importance": "alta"}
        ]
        
        # Follow the conversation step by step
        for i, answer in enumerate(answers[:-1]):
            partial_answers = answers[:i+1]
            result = adviser.get_next_question(partial_answers)
            assert "question" in result
            assert result["next_fact"] == list(answers[i+1].keys())[0]
        
        # Get final recommendation
        result = adviser.get_next_question(answers)
        assert "result" in result
        assert "segura" in result["result"]  # Should predict safe bet
        assert re.search(r"\d+%", result["result"])  # Should mention probability
    
    def test_negative_scenario(self, adviser):
        """Test a scenario that should result in a risky prediction."""
        negative_answers = [
            {"team_form": "malo"},
            {"player_injuries": "mayor"},
            {"home_advantage": "no"},
            {"betting_odds": "altas"},
            {"rest_days": "0"},
            {"opponent_strength": "fuerte"},
            {"recent_head_to_head": "derrota"},
            {"match_importance": "baja"}
        ]
        
        result = adviser.get_next_question(negative_answers)
        assert "result" in result
        assert "arriesgada" in result["result"]  # Should predict risky bet
    
    def test_mixed_scenario(self, adviser):
        """Test a scenario with mixed positive and negative factors."""
        mixed_answers = [
            {"team_form": "bueno"},        # positive
            {"player_injuries": "mayor"},  # negative
            {"home_advantage": "sí"},      # positive
            {"betting_odds": "medias"},    # neutral
            {"rest_days": "2"},           # neutral
            {"opponent_strength": "promedio"}, # neutral
            {"recent_head_to_head": "empate"}, # neutral
            {"match_importance": "media"}  # neutral
        ]
        
        result = adviser.get_next_question(mixed_answers)
        assert "result" in result
        # Check that the explanation mentions positive factors (since it's likely safe)
        assert "buena forma" in result["result"]
        assert "local" in result["result"]
    
    def test_invalid_answer_handling(self, adviser):
        """Test how the system handles invalid answers during the conversation."""
        # Start with first question
        result = adviser.get_next_question([])
        assert result["next_fact"] == "team_form"
        
        # Provide an invalid answer
        result = adviser.get_next_question([{"team_form": "excelente"}])  # Invalid value
        assert "message" in result
        assert "inválida" in result["message"]
        assert result["next_fact"] == "team_form"  # Should ask same question again
        
        # Now provide a valid answer and continue
        result = adviser.get_next_question([{"team_form": "bueno"}])
        assert "question" in result
        assert result["next_fact"] == "player_injuries"
    
    def test_integration_with_bayesian_network(self, adviser):
        """Test that the expert system correctly uses the Bayesian network."""
        # Complete set of answers
        answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"match_importance": "alta"}
        ]
        
        # Initialize the adviser with spy on the Bayesian network
        bayes_net = BasketballBayesianNetwork()
        expert = BasketballExpert(bayes_net)
        
        # Capture original query method to check it's being called
        original_query = bayes_net.inference.query
        call_count = [0]  # Use list to allow modification inside the wrapper
        
        def query_wrapper(*args, **kwargs):
            call_count[0] += 1
            return original_query(*args, **kwargs)
        
        bayes_net.inference.query = query_wrapper
        
        # Get recommendation
        expert.get_next_question(answers)
        
        # Verify Bayesian network was called
        assert call_count[0] > 0
    
    def test_answers_are_translated_correctly(self, adviser):
        """Test that Spanish answers are translated correctly to English for the Bayesian network."""
        # First answer in Spanish
        result = adviser.get_next_question([{"team_form": "bueno"}])
        assert adviser.collected_data.get("team_form") == SPANISH_MAP["team_form"]["bueno"]
        
        # Second answer in Spanish
        result = adviser.get_next_question([
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"}
        ])
        assert adviser.collected_data.get("player_injuries") == SPANISH_MAP["player_injuries"]["ninguna"]
    
    def test_numerical_input_handling(self, adviser):
        """Test how numerical inputs like rest days are handled."""
        # Navigate to rest days question
        answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"}
        ]
        result = adviser.get_next_question(answers)
        assert result["next_fact"] == "rest_days"
        
        # Add a numerical answer
        answers.append({"rest_days": "2"})
        result = adviser.get_next_question(answers)
        
        # Check that the numerical answer was properly translated
        assert adviser.collected_data.get("rest_days") == "2-3"
        assert result["next_fact"] == "opponent_strength"
    
    def test_alternate_spellings_accepted(self, adviser):
        """Test that alternate spellings (like accented vs non-accented) are accepted."""
        # Test with accented character
        result1 = adviser.get_next_question([{"team_form": "bueno"}])
        next_fact1 = result1["next_fact"]
        
        # Reset and test with 'si' instead of 'sí'
        adviser.reset()
        result2 = adviser.get_next_question([{"team_form": "bueno"}, {"player_injuries": "ninguna"}])
        assert result2["next_fact"] == "home_advantage"
        
        result3 = adviser.get_next_question([
            {"team_form": "bueno"}, 
            {"player_injuries": "ninguna"}, 
            {"home_advantage": "si"}  # Without accent
        ])
        assert result3["next_fact"] == "betting_odds"
        
        # Also test with 'debil' instead of 'débil'
        answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "si"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"opponent_strength": "debil"},  # Without accent
        ]
        
        result = adviser.get_next_question(answers)
        assert result["next_fact"] == "recent_head_to_head"
    
    def test_consistency_of_recommendations(self, adviser):
        """Test that the same inputs always produce the same recommendation."""
        positive_answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"match_importance": "alta"}
        ]
        
        # Get recommendation first time
        result1 = adviser.get_next_question(positive_answers)
        
        # Reset and get recommendation again
        adviser.reset()
        result2 = adviser.get_next_question(positive_answers)
        
        # Recommendations should be the same
        assert result1["result"] == result2["result"]