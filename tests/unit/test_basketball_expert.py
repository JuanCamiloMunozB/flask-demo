import numpy as np
import pytest
from unittest.mock import Mock, patch 
from experta import Fact
from app.models.basketball.expert_system import BasketballExpert, BasketballFact, SPANISH_MAP, VALID_STATES
import re

class TestBasketballExpert:
    
    @pytest.fixture
    def mock_bayes_net(self):
        """Create a mock Bayesian network."""
        mock = Mock()
        # Mock the inference engine and query method
        mock.inference = Mock()
        
        # Create a better mock return value with numpy array
        values = np.array([0.75, 0.25])  # Use numpy array instead of list
        result_mock = Mock()
        result_mock.values = values
        result_mock.state_names = {"bet_risk": ["safe", "risky"]}
        
        mock.inference.query.return_value = result_mock
        return mock
        
    @pytest.fixture
    def expert(self, mock_bayes_net):
        """Create a basketball expert system with a mock Bayesian network."""
        return BasketballExpert(mock_bayes_net)
        
    def test_get_sport_name(self, expert):
        """Test that the sport name is correctly returned."""
        assert expert.get_sport_name() == "Basketball"
        
    def test_initial_question(self, expert):
        """Test that the first question is about team form."""
        result = expert.get_next_question([])
        assert result["question"] is not None
        assert "rendimiento reciente del equipo" in result["question"]
        assert result["next_fact"] == "team_form"
        
    def test_question_sequence(self, expert):
        """Test that questions follow the correct sequence."""
        # First question (team form)
        result = expert.get_next_question([{"team_form": "bueno"}])
        assert "lesiones" in result["question"]
        assert result["next_fact"] == "player_injuries"
        
        # Second question (player injuries)
        result = expert.get_next_question([
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"}
        ])
        assert "casa" in result["question"]
        assert result["next_fact"] == "home_advantage"
        
        # Third question (home advantage)
        result = expert.get_next_question([
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"}
        ])
        assert "cuotas" in result["question"]
        assert result["next_fact"] == "betting_odds"
    
    def test_invalid_input(self, expert):
        """Test that invalid inputs are properly handled."""
        result = expert.get_next_question([{"team_form": "invalid"}])
        assert "inválida" in result["message"]
        assert result["is_final"] is False
        assert result["next_fact"] == "team_form"
        
    def test_spanish_translation(self, expert):
        """Test that Spanish inputs are correctly translated."""
        facts = [{"team_form": "bueno"}, {"home_advantage": "sí"}, {"opponent_strength": "débil"}]
        expert.get_next_question(facts)
        
        # These should be translated correctly in collected_data
        assert "team_form" in expert.collected_data
        assert expert.collected_data["team_form"] == "good"
        
    def test_translation_dictionary(self):
        """Test that the translation dictionaries are properly defined."""
        # Check a few key translations
        assert SPANISH_MAP["team_form"]["bueno"] == "good"
        assert SPANISH_MAP["player_injuries"]["ninguna"] == "none"
        assert SPANISH_MAP["home_advantage"]["sí"] == "yes"
        assert SPANISH_MAP["opponent_strength"]["débil"] == "weak"
        
    def test_valid_states(self):
        """Test that valid states are properly defined."""
        assert "good" in VALID_STATES["team_form"]
        assert "none" in VALID_STATES["player_injuries"]
        assert "yes" in VALID_STATES["home_advantage"]
        assert "weak" in VALID_STATES["opponent_strength"]
        
    def test_full_conversation_flow(self, expert, mock_bayes_net):
        """Test a complete conversation flow."""
        # All required answers for a complete assessment
        complete_answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"travel_distance": "corta"},
            {"altitude": "baja"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"weather_conditions": "favorables"},
            {"match_importance": "alta"}
        ]
        
        # Get final result after providing all answers
        result = expert.get_next_question(complete_answers)
        
        # Check we got a final result
        assert "result" in result
        assert "segura" in result["result"]  # Should mention it's safe
        assert re.search(r"\d+%+", result["result"])  # Should mention the probability
        
        # Verify Bayesian network was called with correct evidence
        mock_bayes_net.inference.query.assert_called_once()
        call_args = mock_bayes_net.inference.query.call_args[1]
        assert call_args["variables"] == ["bet_risk"]
        
        # Check some of the translated evidence
        evidence = call_args["evidence"]
        assert evidence["team_form"] == "good"
        assert evidence["player_injuries"] == "none"
        assert evidence["home_advantage"] == "yes"
        assert evidence["opponent_strength"] == "weak"

    def test_explanation_factors(self, expert, mock_bayes_net):
        """Test that explanations include relevant factors."""
        result_mock = Mock()
        result_mock.values = np.array([0.25, 0.75])
        result_mock.state_names = {"bet_risk": ["safe", "risky"]}
        mock_bayes_net.inference.query.return_value = result_mock
        
        # Factors that should lead to risky assessment
        risky_answers = [
            {"team_form": "malo"},                # negative
            {"player_injuries": "mayor"},         # negative
            {"home_advantage": "no"},            # negative
            {"betting_odds": "altas"},           # negative
            {"rest_days": "1"},                  # negative
            {"opponent_strength": "fuerte"},     # negative
            {"recent_head_to_head": "derrota"},  # negative
            {"match_importance": "baja"}         # negative
        ]
        
        result = expert.get_next_question(risky_answers)
        
        # Should be risky and mention negative factors
        explanation = result["result"]
        assert "arriesgada" in explanation
        assert any(factor in explanation for factor in [
            "mal rendimiento", "titulares lesionados", "visitante", 
            "poco descanso", "rival es fuerte"
        ])

    def test_individual_questions(self, expert):
        """Test each individual question rule."""
        # Test team_form question
        expert.reset()
        expert.ask_team_form()
        question_fact = next((fact for fact in expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "rendimiento reciente" in question_fact["question"]
        assert question_fact["next_fact"] == "team_form"
        
        # Test player_injuries question
        expert.reset()
        expert.declare(BasketballFact(team_form="good"))
        expert.ask_player_injuries(form="good")
        question_fact = next((fact for fact in expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "lesiones" in question_fact["question"]
        assert question_fact["next_fact"] == "player_injuries"
        
        # Test home_advantage question
        expert.reset()
        expert.ask_home_advantage(injuries="none")
        question_fact = next((fact for fact in expert.facts.values() if "question" in fact), None)
        assert question_fact is not None
        assert "casa" in question_fact["question"]
        assert question_fact["next_fact"] == "home_advantage"
    
    def test_empty_input_handling(self, expert):
        """Test handling of empty inputs."""
        result = expert.get_next_question([{"team_form": ""}])
        assert "inválida" in result["message"]
        assert result["is_final"] is False
        assert result["next_fact"] == "team_form"
        
    def test_capitalization_handling(self, expert):
        """Test that capitalization doesn't matter."""
        # Capitalize the input
        result = expert.get_next_question([{"team_form": "BuEnO"}])
        assert result["question"] is not None
        assert "lesiones" in result["question"]
        assert result["next_fact"] == "player_injuries"
    
    def test_whitespace_handling(self, expert):
        """Test that extra whitespace is handled correctly."""
        result = expert.get_next_question([{"team_form": "  bueno  "}])
        assert result["question"] is not None
        assert "lesiones" in result["question"]
        assert result["next_fact"] == "player_injuries"
    
    def test_all_question_rules_exist(self, expert):
        """Test that all required question rules are defined."""
        # List of all expected questions
        expected_questions = [
            "team_form", "player_injuries", "home_advantage", "betting_odds",
            "rest_days", "opponent_strength", "recent_head_to_head", "match_importance"
        ]
        
        # Check there's a method to ask each question
        for question in expected_questions:
            ask_method = getattr(expert, f"ask_{question}", None)
            assert ask_method is not None, f"Missing ask method for {question}"

    def test_spanish_to_english_translation_complete(self):
        """Test that all fields have Spanish to English translations."""
        fields = [
            "team_form", "player_injuries", "home_advantage", "betting_odds",
            "rest_days", "opponent_strength", "recent_head_to_head", "match_importance"
        ]
        
        for field in fields:
            assert field in SPANISH_MAP, f"Field {field} missing from SPANISH_MAP"
            assert bool(SPANISH_MAP[field]), f"No translations for {field}"

    def test_valid_states_complete(self):
        """Test that valid states are defined for all fields."""
        fields = [
            "team_form", "player_injuries", "home_advantage", "betting_odds",
            "rest_days", "opponent_strength", "recent_head_to_head", "match_importance"
        ]
        
        for field in fields:
            assert field in VALID_STATES, f"Field {field} missing from VALID_STATES"
            assert bool(VALID_STATES[field]), f"No valid states for {field}"

    def test_explanation_contains_all_factors(self, expert, mock_bayes_net):
        """Test that explanation contains all factors with proper formatting."""
        # Complete set of answers covering all possibilities
        complete_answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"match_importance": "alta"}
        ]
        
        # Get explanation
        result = expert.get_next_question(complete_answers)
        explanation = result["result"]
        
        # Check all relevant factors are mentioned
        assert "buena forma" in explanation
        assert "no tiene jugadores lesionados" in explanation
        assert "juega como local" in explanation
        assert "cuotas reflejan alta probabilidad" in explanation
        assert "buen descanso" in explanation
        assert "rival está en mala forma" in explanation
        assert "ha ganado recientemente" in explanation
        assert "partido es decisivo" in explanation
        
        # Check formatting
        assert "**segura**" in explanation
        assert re.search(r"\d+%", explanation)  # Percentage somewhere in text
        assert "Esto se debe a:" in explanation
        assert "-" in explanation  # Bullet points

    def test_numerical_input_handling(self, expert):
        """Test handling of numerical inputs like rest days."""
        # Test each valid rest day value
        for day in ["0", "1", "2", "3", "4", "5", "6", "7"]:
            facts = [
                {"team_form": "bueno"},
                {"player_injuries": "ninguna"},
                {"home_advantage": "sí"},
                {"betting_odds": "bajas"},
                {"rest_days": day}
            ]
            result = expert.get_next_question(facts)
            assert result["question"] is not None
            assert "fuerte es el rival" in result["question"]

    @pytest.mark.parametrize("risk_value,expected_label", [
        ([0.8, 0.2], "segura"),
        ([0.2, 0.8], "arriesgada")
    ])
    def test_different_risk_outcomes(self, expert, mock_bayes_net, risk_value, expected_label):
        """Test that different risk values produce appropriate labels."""
        # Override the mock return value
        result_mock = Mock()
        result_mock.values = np.array(risk_value)
        result_mock.state_names = {"bet_risk": ["safe", "risky"]}
        mock_bayes_net.inference.query.return_value = result_mock
        
        # Complete conversation to get final result
        complete_answers = [
            {"team_form": "bueno"},
            {"player_injuries": "ninguna"},
            {"home_advantage": "sí"},
            {"betting_odds": "bajas"},
            {"rest_days": "4"},
            {"travel_distance": "corta"},
            {"altitude": "baja"},
            {"opponent_strength": "débil"},
            {"recent_head_to_head": "victoria"},
            {"weather_conditions": "favorables"},
            {"match_importance": "alta"}
        ]
        
        result = expert.get_next_question(complete_answers)
        
        # Check correct label is used
        assert f"**{expected_label}**" in result["result"]