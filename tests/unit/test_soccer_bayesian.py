import pytest
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from app.models.soccer.bayesian_net import SoccerBayesianNetwork
import numpy as np

class TestSoccerBayesianNetwork:
    @pytest.fixture
    def soccer_bayes_net(self):
        """Create a soccer Bayesian network for testing."""
        return SoccerBayesianNetwork()
    
    def test_initialization(self, soccer_bayes_net):
        """Test that the network initializes correctly."""
        assert soccer_bayes_net is not None
        assert soccer_bayes_net.model is not None
        assert soccer_bayes_net.inference is not None
        assert isinstance(soccer_bayes_net.model, BayesianNetwork)
    
    def test_network_structure(self, soccer_bayes_net):
        """Test that the network has the correct structure."""
        expected_edges = [
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
        ]
        
        expected_nodes = [
            'home_advantage', 'injuries', 'performance', 'weather', 
            'rivalry', 'league_position', 'recent_streak', 
            'match_importance', 'physical_condition', 'head_to_head', 'risk'
        ]
        
        assert set(soccer_bayes_net.model.nodes()) == set(expected_nodes)
        assert set(soccer_bayes_net.model.edges()) == set(expected_edges)
    
    def test_cpds(self, soccer_bayes_net):
        """Test that all CPDs are defined and valid."""
        for node in soccer_bayes_net.model.nodes():
            # Check that CPD exists for each node
            cpd = soccer_bayes_net.model.get_cpds(node)
            assert cpd is not None
            
            # Check that CPD is valid
            assert cpd.is_valid_cpd()
            
            # Check that state names are defined
            assert node in cpd.state_names
            
    def test_state_names(self, soccer_bayes_net):
        """Test that state names are correctly defined for each variable."""
        expected_states = {
            'home_advantage': ['home', 'away'],
            'injuries': ['no', 'yes'],
            'performance': ['low', 'medium', 'high'],
            'weather': ['no', 'yes'],
            'rivalry': ['no', 'yes'],
            'league_position': ['high', 'medium', 'low'],
            'recent_streak': ['winning', 'neutral', 'losing'],
            'match_importance': ['high', 'medium', 'low'],
            'physical_condition': ['rested', 'normal', 'fatigued'],
            'head_to_head': ['home_advantage', 'balanced', 'away_advantage'],
            'risk': ['safe', 'risky']
        }
        
        for node, states in expected_states.items():
            cpd = soccer_bayes_net.model.get_cpds(node)
            assert node in cpd.state_names
            assert cpd.state_names[node] == states
    
    def test_inference_engine(self, soccer_bayes_net):
        """Test that the inference engine can make predictions."""
        # Query risk with no evidence
        prediction = soccer_bayes_net.inference.query(['risk'])
        assert prediction is not None
        assert 'risk' in prediction.variables
        assert len(prediction.values) == 2  # safe and risky
        
    def test_inference_with_evidence(self, soccer_bayes_net):
        """Test inference with specific evidence."""
        # Favorable scenario: home team, no injuries, high performance
        favorable_evidence = {
            'home_advantage': 'home',
            'injuries': 'no',
            'performance': 'high'
        }
        favorable_prediction = soccer_bayes_net.inference.query(['risk'], evidence=favorable_evidence)
        
        # Unfavorable scenario: away team, injuries, low performance
        unfavorable_evidence = {
            'home_advantage': 'away',
            'injuries': 'yes',
            'performance': 'low'
        }
        unfavorable_prediction = soccer_bayes_net.inference.query(['risk'], evidence=unfavorable_evidence)
        
        # Check that favorable scenario has higher probability of being safe
        safe_idx = favorable_prediction.state_names['risk'].index('safe')
        assert favorable_prediction.values[safe_idx] > unfavorable_prediction.values[safe_idx]
    
    def test_complex_inference_scenario(self, soccer_bayes_net):
        """Test more complex inference scenario with multiple evidence factors."""
        evidence = {
            'home_advantage': 'home',
            'injuries': 'no',
            'performance': 'high',
            'weather': 'no',
            'rivalry': 'yes',
            'league_position': 'high',
            'recent_streak': 'winning',
            'match_importance': 'high',
            'physical_condition': 'rested',
            'head_to_head': 'home_advantage'
        }
        
        prediction = soccer_bayes_net.inference.query(['risk'], evidence=evidence)
        safe_idx = prediction.state_names['risk'].index('safe')
        risky_idx = prediction.state_names['risk'].index('risky')
        
        # With all these favorable conditions, the bet should be very safe
        assert prediction.values[safe_idx] > 0.75
        assert prediction.values[risky_idx] < 0.25
    
    def test_model_consistency(self, soccer_bayes_net):
        """Test that the model is internally consistent."""
        assert soccer_bayes_net.model.check_model()
    
    def test_cpd_shapes(self, soccer_bayes_net):
        """Test that CPDs have the correct shapes."""
        model = soccer_bayes_net.model
        
        # Check parent nodes have correct CPD shapes
        assert model.get_cpds('home_advantage').values.shape == (2,)
        assert model.get_cpds('injuries').values.shape == (2,)
        assert model.get_cpds('performance').values.shape == (3,)
        
        # Check risk has the correct shape (multi-dimensional)
        risk_cpd = model.get_cpds('risk')
        
        # The CPD shape should be [risk states, parent1 states, parent2 states, ...]
        # First dimension should be 2 (safe, risky)
        assert risk_cpd.values.shape[0] == 2
        
        # The dimensions should match the number of parent variables plus one (for risk itself)
        expected_dims = len(model.get_parents('risk')) + 1
        assert len(risk_cpd.values.shape) == expected_dims
        
        # Check that parent cardinalities match the corresponding dimensions in the CPD
        parent_nodes = model.get_parents('risk')
        for i, parent in enumerate(parent_nodes, 1):  # Start at 1 since dimension 0 is risk itself
            parent_card = len(model.get_cpds(parent).state_names[parent])
            assert risk_cpd.values.shape[i] == parent_card
    
    def test_parent_cpd_probabilities_sum_to_one(self, soccer_bayes_net):
        """Test that all parent node CPD probabilities sum to 1."""
        model = soccer_bayes_net.model
        
        parent_nodes = [
            'home_advantage', 'injuries', 'performance', 'weather', 
            'rivalry', 'league_position', 'recent_streak', 
            'match_importance', 'physical_condition', 'head_to_head'
        ]
        
        for node in parent_nodes:
            cpd = model.get_cpds(node)
            assert np.isclose(cpd.values.sum(), 1.0)
    
    def test_risk_cpd_columns_sum_to_one(self, soccer_bayes_net):
        """Test that each column in the risk CPD sums to 1."""
        risk_cpd = soccer_bayes_net.model.get_cpds('risk')
        
        # Each column should sum to 1
        column_sums = risk_cpd.values.sum(axis=0)
        assert np.allclose(column_sums, 1.0)
    
    def test_good_factors_increase_safety(self, soccer_bayes_net):
        """Test that positive factors increase the 'safe' probability."""
        inference = soccer_bayes_net.inference
        
        # Baseline with no evidence
        result_baseline = inference.query(['risk'], {})
        
        # Home advantage should increase safety
        result_home = inference.query(['risk'], {'home_advantage': 'home'})
        
        # No injuries should increase safety
        result_no_injuries = inference.query(['risk'], {'injuries': 'no'})
        
        # High performance should increase safety
        result_high_perf = inference.query(['risk'], {'performance': 'high'})
        
        # Check each factor increases safety probability
        safe_idx = result_baseline.state_names['risk'].index('safe')
        assert result_home.values[safe_idx] > result_baseline.values[safe_idx]
        assert result_no_injuries.values[safe_idx] > result_baseline.values[safe_idx]
        assert result_high_perf.values[safe_idx] > result_baseline.values[safe_idx]
    
    def test_bad_factors_decrease_safety(self, soccer_bayes_net):
        """Test that negative factors decrease the 'safe' probability."""
        inference = soccer_bayes_net.inference
        
        # Baseline with no evidence
        result_baseline = inference.query(['risk'], {})
        
        # Away games should decrease safety
        result_away = inference.query(['risk'], {'home_advantage': 'away'})
        
        # Injuries should decrease safety
        result_injuries = inference.query(['risk'], {'injuries': 'yes'})
        
        # Low performance should decrease safety
        result_low_perf = inference.query(['risk'], {'performance': 'low'})
        
        # Check each factor decreases safety probability
        safe_idx = result_baseline.state_names['risk'].index('safe')
        assert result_away.values[safe_idx] < result_baseline.values[safe_idx]
        assert result_injuries.values[safe_idx] < result_baseline.values[safe_idx]
        assert result_low_perf.values[safe_idx] < result_baseline.values[safe_idx]
    
    def test_combined_evidence_effect(self, soccer_bayes_net):
        """Test that combined evidence has a stronger effect than individual factors."""
        inference = soccer_bayes_net.inference
        
        # Base case - no evidence
        base_result = inference.query(['risk'], {})
        
        # Single positive evidence
        home_adv_result = inference.query(['risk'], {'home_advantage': 'home'})
        
        # Multiple positive evidence
        multiple_good_result = inference.query(['risk'], {
            'home_advantage': 'home',
            'injuries': 'no',
            'performance': 'high'
        })
        
        # The effect of multiple positive factors should be stronger
        safe_idx = base_result.state_names['risk'].index('safe')
        assert home_adv_result.values[safe_idx] > base_result.values[safe_idx]
        assert multiple_good_result.values[safe_idx] > home_adv_result.values[safe_idx]
    
    def test_league_position_effect(self, soccer_bayes_net):
        """Test that league position has the expected effect on risk."""
        inference = soccer_bayes_net.inference
        
        high_position = inference.query(['risk'], {'league_position': 'high'})
        low_position = inference.query(['risk'], {'league_position': 'low'})
        
        # A high league position should make betting safer than a low position
        safe_idx = high_position.state_names['risk'].index('safe')
        assert high_position.values[safe_idx] > low_position.values[safe_idx]
    
    def test_recent_streak_effect(self, soccer_bayes_net):
        """Test that recent streak has the expected effect on risk."""
        inference = soccer_bayes_net.inference
        
        winning_streak = inference.query(['risk'], {'recent_streak': 'winning'})
        losing_streak = inference.query(['risk'], {'recent_streak': 'losing'})
        
        # A winning streak should make betting safer than a losing streak
        safe_idx = winning_streak.state_names['risk'].index('safe')
        assert winning_streak.values[safe_idx] > losing_streak.values[safe_idx]
    
    def test_physical_condition_effect(self, soccer_bayes_net):
        """Test that physical condition has the expected effect on risk."""
        inference = soccer_bayes_net.inference
        
        rested_team = inference.query(['risk'], {'physical_condition': 'rested'})
        fatigued_team = inference.query(['risk'], {'physical_condition': 'fatigued'})
        
        # A rested team should make betting safer than a fatigued team
        safe_idx = rested_team.state_names['risk'].index('safe')
        assert rested_team.values[safe_idx] > fatigued_team.values[safe_idx]
    
    def test_extreme_scenarios(self, soccer_bayes_net):
        """Test extreme favorable and unfavorable scenarios."""
        inference = soccer_bayes_net.inference
        
        # Extremely favorable scenario
        favorable_evidence = {
            'home_advantage': 'home',
            'injuries': 'no',
            'performance': 'high',
            'weather': 'no',
            'rivalry': 'no',
            'league_position': 'high',
            'recent_streak': 'winning',
            'match_importance': 'high',
            'physical_condition': 'rested',
            'head_to_head': 'home_advantage'
        }
        
        # Extremely unfavorable scenario
        unfavorable_evidence = {
            'home_advantage': 'away',
            'injuries': 'yes',
            'performance': 'low',
            'weather': 'yes',
            'rivalry': 'yes',
            'league_position': 'low',
            'recent_streak': 'losing',
            'match_importance': 'low',
            'physical_condition': 'fatigued',
            'head_to_head': 'away_advantage'
        }
        
        favorable_result = inference.query(['risk'], favorable_evidence)
        unfavorable_result = inference.query(['risk'], unfavorable_evidence)
        
        safe_idx = favorable_result.state_names['risk'].index('safe')
        
        # Favorable scenario should have high safety probability
        assert favorable_result.values[safe_idx] > 0.8
        
        # Unfavorable scenario should have low safety probability
        assert unfavorable_result.values[safe_idx] < 0.2
        
        # The difference should be dramatic
        assert favorable_result.values[safe_idx] - unfavorable_result.values[safe_idx] > 0.6