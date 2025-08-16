import pytest
from app.models.soccer.expert_system import SoccerExpert, SPANISH_MAP
from app.models.soccer.bayesian_net import SoccerBayesianNetwork
import re

class TestSoccerAdviser:
    @pytest.fixture
    def adviser(self):
        """Create a complete soccer adviser with real components."""
        bayes_net = SoccerBayesianNetwork()
        return SoccerExpert(bayes_net)
    
    def test_complete_conversation_flow(self, adviser):
        """Test the complete end-to-end conversation flow."""
        # Start with first question
        result = adviser.get_next_question([])
        assert "question" in result
        assert result["next_fact"] == "home_advantage"
        
        # Provide all answers sequentially
        answers = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "no"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
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
            {"home_advantage": "no"},
            {"injuries": "sí"},
            {"performance": "bajo"},
            {"weather": "sí"},
            {"rivalry": "sí"},
            {"league_position": "baja"},
            {"recent_streak": "perdedora"},
            {"match_importance": "baja"},
            {"physical_condition": "fatigado"},
            {"head_to_head": "ventaja visitante"}
        ]
        
        result = adviser.get_next_question(negative_answers)
        assert "result" in result
        assert "arriesgada" in result["result"]  # Should predict risky bet
    
    def test_mixed_scenario(self, adviser):
        """Test a scenario with mixed positive and negative factors."""
        mixed_answers = [
            {"home_advantage": "sí"},      # positive
            {"injuries": "sí"},            # negative
            {"performance": "medio"},      # neutral
            {"weather": "no"},             # positive
            {"rivalry": "no"},             # positive
            {"league_position": "media"},  # neutral
            {"recent_streak": "neutral"},  # neutral
            {"match_importance": "alta"},  # positive
            {"physical_condition": "normal"}, # neutral
            {"head_to_head": "equilibrado"}  # neutral
        ]
        
        result = adviser.get_next_question(mixed_answers)
        assert "result" in result
        # Check that explanation mentions factors considered
        assert "combinación de factores" in result["result"]
    
    def test_invalid_answer_handling(self, adviser):
        """Test how the system handles invalid answers during the conversation."""
        # Start with first question
        result = adviser.get_next_question([])
        assert result["next_fact"] == "home_advantage"
        
        # Provide an invalid answer
        result = adviser.get_next_question([{"home_advantage": "tal vez"}])  # Invalid value
        assert "message" in result
        assert "inválida" in result["message"]
        assert result["next_fact"] == "home_advantage"  # Should ask same question again
        
        # Now provide a valid answer and continue
        result = adviser.get_next_question([{"home_advantage": "sí"}])
        assert "question" in result
        assert result["next_fact"] == "injuries"
    
    def test_integration_with_bayesian_network(self, adviser):
        """Test that the expert system correctly uses the Bayesian network."""
        # Complete set of answers
        answers = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "no"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        # Initialize the adviser with spy on the Bayesian network
        bayes_net = SoccerBayesianNetwork()
        expert = SoccerExpert(bayes_net)
        
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
        result = adviser.get_next_question([{"home_advantage": "sí"}])
        assert adviser.collected_data.get("home_advantage") == SPANISH_MAP["home_advantage"]["sí"]
        
        # Second answer in Spanish
        result = adviser.get_next_question([
            {"home_advantage": "sí"},
            {"injuries": "no"}
        ])
        assert adviser.collected_data.get("injuries") == SPANISH_MAP["injuries"]["no"]
    
    def test_alternate_spellings_accepted(self, adviser):
        """Test that alternate spellings (like accented vs non-accented) are accepted."""
        # Test with accented character
        result1 = adviser.get_next_question([{"home_advantage": "sí"}])
        next_fact1 = result1["next_fact"]
        
        # Reset and test with 'si' instead of 'sí'
        adviser.reset()
        result2 = adviser.get_next_question([{"home_advantage": "si"}])
        assert result2["next_fact"] == next_fact1
        
        # Test alternate spellings for performance
        answers = [
            {"home_advantage": "si"},
            {"injuries": "no"},
            {"performance": "alta"}  # feminine form instead of masculine
        ]
        
        result = adviser.get_next_question(answers)
        assert result["next_fact"] == "weather"
    
    def test_consistency_of_recommendations(self, adviser):
        """Test that the same inputs always produce the same recommendation."""
        positive_answers = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "no"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        # Get recommendation first time
        result1 = adviser.get_next_question(positive_answers)
        
        # Reset and get recommendation again
        adviser.reset()
        result2 = adviser.get_next_question(positive_answers)
        
        # Recommendations should be the same
        assert result1["result"] == result2["result"]
    
    def test_boundary_cases(self, adviser):
        """Test boundary cases like mixed factors that could lead to close predictions."""
        boundary_answers = [
            {"home_advantage": "sí"},      # positive
            {"injuries": "sí"},            # negative
            {"performance": "alto"},       # positive
            {"weather": "sí"},             # negative
            {"rivalry": "sí"},             # negative
            {"league_position": "alta"},   # positive
            {"recent_streak": "ganadora"}, # positive
            {"match_importance": "alta"},  # positive
            {"physical_condition": "fatigado"}, # negative
            {"head_to_head": "ventaja local"}  # positive
        ]
        
        result = adviser.get_next_question(boundary_answers)
        assert "result" in result
        # Should include percentage in response
        assert re.search(r"\d+%", result["result"])
    
    def test_variability_of_factors(self, adviser):
        """Test that changing a single factor can influence the recommendation."""
        base_answers = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "no"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        changed_answers = base_answers.copy()
        # Change just one factor to something negative
        changed_answers[1] = {"injuries": "sí"}
        changed_answers[2] = {"performance": "bajo"}
        changed_answers[3] = {"weather": "sí"}
        
        # Get both recommendations
        result1 = adviser.get_next_question(base_answers)
        adviser.reset()
        result2 = adviser.get_next_question(changed_answers)
        
        # Extract probabilities using regex
        prob1 = float(re.search(r"(\d+\.\d+)%", result1["result"]).group(1))
        prob2 = float(re.search(r"(\d+\.\d+)%", result2["result"]).group(1))
        
        # The version with injuries should have lower probability of success
        assert prob2 < prob1