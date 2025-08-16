import pytest
from unittest.mock import Mock, MagicMock
from experta import Fact
import numpy as np
import re
from app.models.soccer.expert_system import SoccerExpert, SoccerFact, SPANISH_MAP, VALID_STATES

class TestSoccerExpert:
    @pytest.fixture
    def mock_bayes_net(self):
        """Create a mock bayesian network for testing."""
        mock = Mock()
        # Configure mock prediction
        prediction = Mock()
        prediction.values = np.array([0.75, 0.25])  # Use numpy array instead of list
        prediction.state_names = {"risk": ["safe", "risky"]}
        mock.inference = Mock()
        mock.inference.query.return_value = prediction
        return mock

    @pytest.fixture
    def soccer_expert(self, mock_bayes_net):
        """Create a test instance of SoccerExpert with mocked Bayesian network."""
        return SoccerExpert(mock_bayes_net)

    def test_initialization(self, soccer_expert):
        """Test that the expert system initializes properly."""
        assert soccer_expert is not None
        assert soccer_expert.collected_data == {}

    def test_get_sport_name(self, soccer_expert):
        """Test the sport name is correct."""
        assert soccer_expert.get_sport_name() == "Soccer"

    def test_first_question(self, soccer_expert):
        """Test that the first question is about home advantage."""
        result = soccer_expert.get_next_question([])
        assert "question" in result
        assert "casa" in result["question"].lower()
        assert result["next_fact"] == "home_advantage"

    def test_spanish_input_translation(self):
        """Test that Spanish inputs are correctly translated."""
        assert SPANISH_MAP["home_advantage"]["sí"] == "home"
        assert SPANISH_MAP["performance"]["bajo"] == "low"
        assert SPANISH_MAP["recent_streak"]["ganadora"] == "winning"

    def test_validation_rejects_invalid_input(self, soccer_expert):
        """Test that invalid inputs are rejected."""
        invalid_fact = [{"home_advantage": "invalid"}]
        result = soccer_expert.get_next_question(invalid_fact)
        assert "message" in result
        assert "inválida" in result["message"]
        assert result["is_final"] is False

    def test_question_sequence(self, soccer_expert):
        """Test the sequence of questions."""
        # Test first question
        result = soccer_expert.get_next_question([])
        assert result["next_fact"] == "home_advantage"
        
        # Test second question after answering first
        result = soccer_expert.get_next_question([{"home_advantage": "sí"}])
        assert result["next_fact"] == "injuries"
        
        # Test third question after answering first two
        result = soccer_expert.get_next_question([
            {"home_advantage": "sí"}, 
            {"injuries": "no"}
        ])
        assert result["next_fact"] == "performance"

    def test_complete_flow_to_recommendation(self, soccer_expert):
        """Test the complete flow from start to recommendation."""
        complete_facts = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "sí"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        result = soccer_expert.get_next_question(complete_facts)
        
        # Should have a result, not a question
        assert "result" in result
        assert "question" not in result
        assert "segura" in result["result"]
        assert "75" in result["result"]  # Should show probability from our mock

    def test_bayesian_network_integration(self, soccer_expert):
        """Test integration with Bayesian Network."""
        complete_facts = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "sí"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        soccer_expert.get_next_question(complete_facts)
        
        # Verify the Bayesian network was queried with correct parameters
        soccer_expert.bayes_net.inference.query.assert_called_once()
        call_args = soccer_expert.bayes_net.inference.query.call_args[1]
        assert call_args["variables"] == ["risk"]
        assert call_args["evidence"]["home_advantage"] == "home"
        assert call_args["evidence"]["performance"] == "high"

    def test_invalid_state_handling(self, soccer_expert):
        """Test handling of invalid states."""
        # Use the standard API instead of directly calling internal methods
        invalid_facts = [
            {"home_advantage": "invalid"},  # Invalid value for home_advantage
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "sí"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        result = soccer_expert.get_next_question(invalid_facts)
        
        # Check that we get an error message about invalid input
        assert "result" in result
        assert "Error: valor no válido 'invalid'" in result["result"]
        assert "home_advantage" in result["result"]

    def test_individual_questions(self, soccer_expert):
        """Test each individual question rule."""
        # Test home_advantage question
        soccer_expert.reset()
        soccer_expert.ask_home_advantage()
        question_fact = next((fact for fact in soccer_expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "casa" in question_fact["question"].lower()
        assert question_fact["next_fact"] == "home_advantage"
        
        # Test injuries question
        soccer_expert.reset()
        soccer_expert.declare(SoccerFact(home_advantage="home"))
        soccer_expert.ask_injuries(home_advantage="home")
        question_fact = next((fact for fact in soccer_expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "lesionados" in question_fact["question"].lower()
        assert question_fact["next_fact"] == "injuries"
        
        # Test performance question
        soccer_expert.reset()
        soccer_expert.ask_performance(injuries="no")
        question_fact = next((fact for fact in soccer_expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "rendimiento" in question_fact["question"].lower()
        assert question_fact["next_fact"] == "performance"
    
    def test_empty_input_handling(self, soccer_expert):
        """Test handling of empty inputs."""
        result = soccer_expert.get_next_question([{"home_advantage": ""}])
        assert "inválida" in result["message"].lower()
        assert result["is_final"] is False
        assert result["next_fact"] == "home_advantage"
    
    def test_capitalization_handling(self, soccer_expert):
        """Test that capitalization doesn't matter."""
        # Capitalize the input
        result = soccer_expert.get_next_question([{"home_advantage": "SÍ"}])
        assert result["question"] is not None
        assert "lesionados" in result["question"].lower()
        assert result["next_fact"] == "injuries"
    
    def test_whitespace_handling(self, soccer_expert):
        """Test that extra whitespace is handled correctly."""
        result = soccer_expert.get_next_question([{"home_advantage": "  sí  "}])
        assert result["question"] is not None
        assert "lesionados" in result["question"].lower()
        assert result["next_fact"] == "injuries"
    
    def test_all_question_rules_exist(self, soccer_expert):
        """Test that all required question rules are defined."""
        # List of all expected questions
        expected_questions = [
            "home_advantage", "injuries", "performance", "weather",
            "rivalry", "league_position", "recent_streak", "match_importance",
            "physical_condition", "head_to_head"
        ]
        
        # Check there's a method to ask each question
        for question in expected_questions:
            ask_method = getattr(soccer_expert, f"ask_{question}", None)
            assert ask_method is not None, f"Missing ask method for {question}"
    
    def test_spanish_to_english_translation_complete(self):
        """Test that all fields have Spanish to English translations."""
        fields = [
            "home_advantage", "injuries", "performance", "weather",
            "rivalry", "league_position", "recent_streak", "match_importance",
            "physical_condition", "head_to_head"
        ]
        
        for field in fields:
            assert field in SPANISH_MAP, f"Field {field} missing from SPANISH_MAP"
            assert bool(SPANISH_MAP[field]), f"No translations for {field}"
    
    def test_valid_states_complete(self):
        """Test that valid states are defined for all fields."""
        fields = [
            "home_advantage", "injuries", "performance", "weather",
            "rivalry", "league_position", "recent_streak", "match_importance",
            "physical_condition", "head_to_head"
        ]
        
        for field in fields:
            assert field in VALID_STATES, f"Field {field} missing from VALID_STATES"
            assert bool(VALID_STATES[field]), f"No valid states for {field}"
    
    def test_explanation_contains_all_factors(self, soccer_expert, mock_bayes_net):
        """Test that explanation contains all factors with proper formatting."""
        # Complete set of answers covering all possibilities
        complete_facts = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "sí"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        # Get explanation
        result = soccer_expert.get_next_question(complete_facts)
        explanation = result["result"]
        
        # Check all relevant factors are mentioned
        assert "local" in explanation.lower() or "casa" in explanation.lower()
        assert "lesiones" in explanation.lower()  # Check for the general concept, not specific value
        assert "rendimiento" in explanation.lower()
        assert "clima" in explanation.lower()
        assert "rivalidad" in explanation.lower()
        assert "posición" in explanation.lower() or "tabla" in explanation.lower()
        assert "racha" in explanation.lower()
        assert "importancia" in explanation.lower() or "partido" in explanation.lower()
        assert "condición" in explanation.lower() or "física" in explanation.lower()
        assert "historial" in explanation.lower()
        
        # Check formatting
        assert "**segura**" in explanation or "**arriesgada**" in explanation
        assert re.search(r"\d+%", explanation)  # Percentage somewhere in text
        assert ":" in explanation  # Some kind of label

    @pytest.mark.parametrize("risk_value,expected_label", [
        ([0.8, 0.2], "segura"),
        ([0.2, 0.8], "arriesgada")
    ])
    def test_different_risk_outcomes(self, soccer_expert, mock_bayes_net, risk_value, expected_label):
        """Test that different risk values produce appropriate labels."""
        # Override the mock return value
        prediction = Mock()
        prediction.values = np.array(risk_value)
        prediction.state_names = {"risk": ["safe", "risky"]}
        mock_bayes_net.inference.query.return_value = prediction
        
        # Complete set of facts
        complete_facts = [
            {"home_advantage": "sí"},
            {"injuries": "no"},
            {"performance": "alto"},
            {"weather": "no"},
            {"rivalry": "sí"},
            {"league_position": "alta"},
            {"recent_streak": "ganadora"},
            {"match_importance": "alta"},
            {"physical_condition": "descansado"},
            {"head_to_head": "ventaja local"}
        ]
        
        result = soccer_expert.get_next_question(complete_facts)
        
        # Check correct label is used
        assert f"**{expected_label}**" in result["result"]
    
    def test_invalid_sequence_handling(self, soccer_expert):
        """Test handling when questions are provided out of sequence."""
        # Skip home_advantage and go straight to injuries
        result = soccer_expert.get_next_question([{"injuries": "no"}])
        
        # The system appears to accept the injuries answer and ask about performance instead
        assert result["question"] is not None
        assert "rendimiento" in result["question"].lower()
        assert result["next_fact"] == "performance"
    
    def test_multiple_acceptable_inputs(self, soccer_expert):
        """Test that multiple valid inputs are accepted."""
        # Test both 'sí' and 'si' are acceptable for home advantage
        for yes_variant in ["sí", "si"]:
            facts = [{"home_advantage": yes_variant}]
            result = soccer_expert.get_next_question(facts)
            assert result["question"] is not None
            assert "lesionados" in result["question"].lower()
            assert result["next_fact"] == "injuries"

    def test_translation_consistency(self):
        """Test the consistency between SPANISH_MAP and VALID_STATES."""
        for field, translations in SPANISH_MAP.items():
            if field in VALID_STATES:
                for spanish_value, english_value in translations.items():
                    assert english_value in VALID_STATES[field], \
                        f"Translation '{english_value}' for '{field}.{spanish_value}' not in VALID_STATES"
    
    def test_progression_after_answer(self, soccer_expert):
        """Test that answering a question properly progresses to the next question."""
        # Initial question
        initial_result = soccer_expert.get_next_question([])
        first_fact = initial_result["next_fact"]
        
        # Answer with valid value
        valid_spanish_value = next(iter(SPANISH_MAP[first_fact].keys()))
        result = soccer_expert.get_next_question([{first_fact: valid_spanish_value}])
        
        # Should have moved to next question, not same one
        assert result["next_fact"] != first_fact
    
    def test_collected_data_consistency(self, soccer_expert):
        """Test that the collected_data dictionary contains correct translations."""
        # Process all facts at once
        soccer_expert.reset()  # Start fresh
        
        # Call with all facts together
        soccer_expert.get_next_question([
            {"home_advantage": "sí"}, 
            {"injuries": "no"}, 
            {"performance": "alto"}
        ])
        
        # Check that at least the last fact was processed correctly
        assert "performance" in soccer_expert.collected_data
        assert soccer_expert.collected_data["performance"] == SPANISH_MAP["performance"]["alto"]