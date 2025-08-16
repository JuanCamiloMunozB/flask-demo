import pytest
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.inference import VariableElimination
from app.models.basketball.bayesian_net import BasketballBayesianNetwork

class TestBasketballBayesianNetwork:
    
    @pytest.fixture
    def basketball_network(self):
        """Create a basketball Bayesian network instance for testing."""
        return BasketballBayesianNetwork()
    
    def test_init_creates_model_and_inference(self, basketball_network):
        """Test that initialization creates model and inference engine."""
        assert basketball_network.model is not None
        assert basketball_network.inference is not None
        assert isinstance(basketball_network.inference, VariableElimination)
    
    def test_model_is_bayesian_network(self, basketball_network):
        """Test that the created model is a BayesianNetwork instance."""
        assert isinstance(basketball_network.model, BayesianNetwork)

    def test_network_has_required_nodes(self, basketball_network):
        """Test that all required nodes are present in the network."""
        required_nodes = {
            'team_form', 'player_injuries', 'home_advantage', 
            'betting_odds', 'rest_days', 'opponent_strength', 
            'recent_head_to_head', 'match_importance', 'bet_risk'
        }
        assert set(basketball_network.model.nodes()) == required_nodes
    
    def test_network_structure(self, basketball_network):
        """Test that the network structure has the correct edges."""
        for node in basketball_network.model.nodes():
            if node != 'bet_risk':
                assert (node, 'bet_risk') in basketball_network.model.edges()
        
        # Check that bet_risk has no outgoing edges
        assert not any(edge[0] == 'bet_risk' for edge in basketball_network.model.edges())
    
    def test_cpd_shapes(self, basketball_network):
        """Test that CPDs have the correct shapes."""
        model = basketball_network.model
        
        # Check parent nodes have correct CPD shapes
        assert model.get_cpds('team_form').values.shape == (3,)
        assert model.get_cpds('player_injuries').values.shape == (3,)
        assert model.get_cpds('home_advantage').values.shape == (2,)
        
        # Check bet_risk has the correct shape (multi-dimensional) - first dimension is bet_risk's cardinality (2)
        bet_risk_cpd = model.get_cpds('bet_risk')
        
        # The CPD shape should be [bet_risk states, parent1 states, parent2 states, ...]
        # First dimension should be 2 (safe, risky)
        assert bet_risk_cpd.values.shape[0] == 2
        
        # The dimensions should match the number of parent variables plus one (for bet_risk itself)
        expected_dims = len(model.get_parents('bet_risk')) + 1
        assert len(bet_risk_cpd.values.shape) == expected_dims
        
        # Check that parent cardinalities match the corresponding dimensions in the CPD
        parent_nodes = model.get_parents('bet_risk')
        for i, parent in enumerate(parent_nodes, 1):  # Start at 1 since dimension 0 is bet_risk itself
            parent_card = len(model.get_cpds(parent).state_names[parent])
            assert bet_risk_cpd.values.shape[i] == parent_card
 
    def test_cpd_state_names(self, basketball_network):
        """Test that CPDs have the correct state names."""
        model = basketball_network.model
        
        state_name_checks = {
            'team_form': ['good', 'average', 'poor'],
            'player_injuries': ['none', 'minor', 'major'],
            'home_advantage': ['yes', 'no'],
            'betting_odds': ['low', 'medium', 'high'],
            'rest_days': ['0-1', '2-3', '4+'],
            'opponent_strength': ['strong', 'average', 'weak'],
            'recent_head_to_head': ['win', 'draw', 'loss'],
            'match_importance': ['high', 'medium', 'low'],
            'bet_risk': ['safe', 'risky']
        }
        
        for var, expected_states in state_name_checks.items():
            cpd = model.get_cpds(var)
            assert cpd.state_names[var] == expected_states

    def test_parent_cpd_probabilities_sum_to_one(self, basketball_network):
        """Test that all parent node CPD probabilities sum to 1."""
        model = basketball_network.model
        
        parent_nodes = [
            'team_form', 'player_injuries', 'home_advantage', 
            'betting_odds', 'rest_days', 'opponent_strength', 
            'recent_head_to_head', 'match_importance'
        ]
        
        for node in parent_nodes:
            cpd = model.get_cpds(node)
            assert np.isclose(cpd.values.sum(), 1.0, rtol=1e-4, atol=1e-4)
            
    def test_bet_risk_cpd_columns_sum_to_one(self, basketball_network):
        """Test that each column in the bet_risk CPD sums to 1."""
        bet_risk_cpd = basketball_network.model.get_cpds('bet_risk')
        
        # Each column should sum to 1
        column_sums = bet_risk_cpd.values.sum(axis=0)
        assert np.allclose(column_sums, 1.0)
    
    def test_good_factors_increase_safety(self, basketball_network):
        """Test that positive factors increase the 'safe' probability."""
        inference = basketball_network.inference
        
        # Baseline with average values
        average_evidence = {
            'team_form': 'average',
            'player_injuries': 'minor',
            'opponent_strength': 'average'
        }
        result_average = inference.query(['bet_risk'], average_evidence)
        
        # Good team form should increase safety
        good_form_evidence = average_evidence.copy()
        good_form_evidence['team_form'] = 'good'
        result_good_form = inference.query(['bet_risk'], good_form_evidence)
        
        assert result_good_form.values[0] > result_average.values[0]  # [0] is 'safe'
    
    def test_bad_factors_decrease_safety(self, basketball_network):
        """Test that negative factors decrease the 'safe' probability."""
        inference = basketball_network.inference
        
        # Baseline with average values
        average_evidence = {
            'team_form': 'average',
            'player_injuries': 'minor',
            'opponent_strength': 'average'
        }
        result_average = inference.query(['bet_risk'], average_evidence)
        
        # Bad team form should decrease safety
        bad_form_evidence = average_evidence.copy()
        bad_form_evidence['team_form'] = 'poor'
        result_bad_form = inference.query(['bet_risk'], bad_form_evidence)
        
        assert result_bad_form.values[0] < result_average.values[0]  # [0] is 'safe'
    
    def test_model_validity(self, basketball_network):
        """Test that the model passes the check_model validation."""
        assert basketball_network.model.check_model() is True
    
    def test_combined_evidence_effect(self, basketball_network):
        """Test that combined evidence has a stronger effect than individual factors."""
        inference = basketball_network.inference
        
        # Base case - no evidence
        base_result = inference.query(['bet_risk'], {})
        base_safe_prob = base_result.values[0]
        
        # Single positive evidence
        good_team_result = inference.query(['bet_risk'], {'team_form': 'good'})
        good_team_safe_prob = good_team_result.values[0]
        
        # Multiple positive evidence
        multiple_good_result = inference.query(['bet_risk'], {
            'team_form': 'good',
            'player_injuries': 'none',
            'home_advantage': 'yes'
        })
        multiple_good_safe_prob = multiple_good_result.values[0]
        
        # The effect of multiple positive factors should be stronger
        assert good_team_safe_prob > base_safe_prob
        assert multiple_good_safe_prob > good_team_safe_prob
    
    def test_opponent_strength_effect(self, basketball_network):
        """Test specifically that opponent strength has the expected effect."""
        inference = basketball_network.inference
        
        strong_opponent = inference.query(['bet_risk'], {'opponent_strength': 'strong'})
        weak_opponent = inference.query(['bet_risk'], {'opponent_strength': 'weak'})
        
        # Playing against a weak opponent should be safer than against a strong opponent
        assert weak_opponent.values[0] > strong_opponent.values[0]
    
    def test_home_advantage_effect(self, basketball_network):
        """Test that home advantage increases safety."""
        inference = basketball_network.inference
        
        home_game = inference.query(['bet_risk'], {'home_advantage': 'yes'})
        away_game = inference.query(['bet_risk'], {'home_advantage': 'no'})
        
        assert home_game.values[0] > away_game.values[0]