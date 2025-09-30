import unittest
import numpy as np
from pydantic import ValidationError

# Assuming the user's files are in the same directory or accessible in the python path
from schemas import ChannelModelSchema, StimulusProtocolSchema
from simulation import SimulationEngine, Stimulus

# --- Test Fixtures: Reusable, valid data for tests ---

def create_valid_model_data():
    """Returns a dictionary for a valid two-state (C->O) channel model."""
    return {
        "channel_id": "test_kv1",
        "states": [
            {"id": "C", "name": "Closed", "conductance": 0.0},
            {"id": "O", "name": "Open", "conductance": 1.2} # nS
        ],
        "rate_functions": [
            {"id": "alpha", "equation": "0.1 * exp(V / 25.0)"},
            {"id": "beta", "equation": "0.2 * exp(-V / 50.0)"}
        ],
        "transitions": [
            {"from": "C", "to": "O", "rate_function_id": "alpha"},
            {"from": "O", "to": "C", "rate_function_id": "beta"}
        ]
    }

def create_valid_protocol_data():
    """Returns a dictionary for a valid stimulus protocol with a voltage step."""
    return {
        "protocol_id": "test_step",
        "holding_values": {
            "voltage_mV": -80.0,
            "internal_K_mM": 140.0,
            "external_K_mM": 5.0,
            "volume_internal_L": 1e-12, # 1 pL
            "volume_external_L": 1e-6   # 1 uL
        },
        "epochs": [
            {
                "variable": "voltage_mV",
                "start_time_ms": 100.0,
                "duration_ms": 200.0,
                "value": 40.0
            }
        ]
    }


# --- Test Cases ---

class TestSchemas(unittest.TestCase):
    """Tests for the Pydantic data validation schemas in schemas.py."""

    def test_valid_model_passes(self):
        """Check that a correctly structured model validates successfully."""
        try:
            ChannelModelSchema(**create_valid_model_data())
        except ValidationError as e:
            self.fail(f"Valid model data failed validation: {e}")

    def test_valid_protocol_passes(self):
        """Check that a correctly structured protocol validates successfully."""
        try:
            StimulusProtocolSchema(**create_valid_protocol_data())
        except ValidationError as e:
            self.fail(f"Valid protocol data failed validation: {e}")

    def test_model_fails_with_invalid_transition_state(self):
        """Ensure model validation fails if a transition refers to a non-existent state."""
        invalid_data = create_valid_model_data()
        invalid_data["transitions"].append(
            {"from": "C", "to": "Z_INVALID", "rate_function_id": "alpha"}
        )
        with self.assertRaisesRegex(ValueError, "is not a defined state id"):
            ChannelModelSchema(**invalid_data)

    def test_model_fails_with_invalid_rate_function_id(self):
        """Ensure model validation fails if a transition refers to a non-existent rate function."""
        invalid_data = create_valid_model_data()
        invalid_data["transitions"].append(
            {"from": "C", "to": "O", "rate_function_id": "gamma_INVALID"}
        )
        with self.assertRaisesRegex(ValueError, "is not a defined function id"):
            ChannelModelSchema(**invalid_data)
            
    def test_protocol_fails_with_invalid_epoch_variable(self):
        """Ensure protocol validation fails if an epoch targets an invalid variable."""
        invalid_data = create_valid_protocol_data()
        invalid_data["epochs"].append({
            "variable": "temperature_C", # This variable is not in HoldingValues
            "start_time_ms": 10.0,
            "duration_ms": 50.0,
            "value": 37.0
        })
        with self.assertRaisesRegex(ValueError, "is not a valid variable"):
            StimulusProtocolSchema(**invalid_data)


class TestStimulus(unittest.TestCase):
    """Tests for the Stimulus helper class."""
    
    def setUp(self):
        """Set up a stimulus object for all tests in this class."""
        protocol_schema = StimulusProtocolSchema(**create_valid_protocol_data())
        self.stimulus = Stimulus(protocol_schema)
        self.holding_voltage = protocol_schema.holding_values.voltage_mV

    def test_returns_holding_value_before_epochs(self):
        """Test that the holding value is returned for a time before any epoch starts."""
        self.assertEqual(self.stimulus.get_value_at_time('voltage_mV', 50.0), self.holding_voltage)

    def test_returns_epoch_value_during_epoch(self):
        """Test that the correct epoch value is returned within an epoch's time range."""
        self.assertEqual(self.stimulus.get_value_at_time('voltage_mV', 150.0), 40.0)

    def test_returns_value_at_epoch_start(self):
        """Test that the epoch value is active at its exact start time."""
        self.assertEqual(self.stimulus.get_value_at_time('voltage_mV', 100.0), 40.0)

    def test_returns_holding_value_at_epoch_end(self):
        """Test that the value reverts to holding at the exact end time of an epoch."""
        # End time is start (100) + duration (200) = 300. The epoch is active for t in [100, 300).
        self.assertEqual(self.stimulus.get_value_at_time('voltage_mV', 300.0), self.holding_voltage)


class TestSimulationEngine(unittest.TestCase):
    """Tests for the main SimulationEngine class and its core logic."""

    def setUp(self):
        """Prepare a standard engine instance for testing."""
        self.model = ChannelModelSchema(**create_valid_model_data())
        self.protocol = StimulusProtocolSchema(**create_valid_protocol_data())
        self.engine = SimulationEngine(self.model, self.protocol)

    def test_rate_equation_parsing(self):
        """Verify that a string equation is correctly parsed and evaluated."""
        # The 'alpha' function is '0.1 * exp(V / 25.0)'
        rate_func = self.engine._rate_functions['alpha']
        
        # Test case 1: V = 0
        self.assertAlmostEqual(rate_func(0), 0.1 * np.exp(0 / 25.0))
        # Test case 2: V = 50
        self.assertAlmostEqual(rate_func(50), 0.1 * np.exp(50 / 25.0))

    def test_conservation_of_probability(self):
        """The sum of state probabilities must always be 1.0."""
        results = self.engine.run(duration_ms=50, steps=100)
        prob_sum = np.sum(results["probabilities"], axis=0)

        print(f"The current prob_sum = '{prob_sum}'")
        # Assert that all values in the sum array are close to 1.0
        self.assertTrue(np.allclose(prob_sum, 1.0), "Sum of probabilities deviates from 1.0")

    def test_initial_conditions(self):
        """Check if the simulation starts in the correct state."""
        results = self.engine.run(duration_ms=1, steps=2)
        # Probability of the first state ('C') should be 1.0 at t=0
        self.assertAlmostEqual(results["probabilities"][0, 0], 1.0)
        # All other state probabilities should be 0.0 at t=0
        self.assertAlmostEqual(np.sum(results["probabilities"][1:, 0]), 0.0)
        # Initial concentrations should match the protocol
        self.assertAlmostEqual(results["internal_K_mM"][0], self.protocol.holding_values.internal_K_mM)
        self.assertAlmostEqual(results["external_K_mM"][0], self.protocol.holding_values.external_K_mM)

    def test_equilibrium_at_nernst_potential(self):
        """At Nernst potential, net current and concentration change should be zero."""
        protocol_data = create_valid_protocol_data()
        
        # Calculate Nernst potential for K+
        R, T, F, z = 8.314, 293.15, 96485, 1
        Ki = protocol_data["holding_values"]["internal_K_mM"]
        Ko = protocol_data["holding_values"]["external_K_mM"]
        nernst_potential_mV = ((R * T) / (z * F) * np.log(Ko / Ki)) * 1000
        
        # Set holding voltage to Nernst and remove epochs
        protocol_data["holding_values"]["voltage_mV"] = nernst_potential_mV
        protocol_data["epochs"] = [] 
        
        protocol = StimulusProtocolSchema(**protocol_data)
        engine = SimulationEngine(self.model, protocol)
        results = engine.run(duration_ms=100, steps=100)
        
        # Current should be zero (or very close)
        self.assertTrue(np.allclose(results["total_current_pA"], 0.0, atol=1e-9))
        # Concentrations should not change
        self.assertAlmostEqual(results["internal_K_mM"][0], results["internal_K_mM"][-1])
        self.assertAlmostEqual(results["external_K_mM"][0], results["external_K_mM"][-1])

    def test_ion_concentration_dynamics(self):
        """Verify concentrations change correctly in response to sustained current."""
        # Use a protocol that holds voltage at +40mV to drive K+ out
        protocol_data = create_valid_protocol_data()
        protocol_data["holding_values"]["voltage_mV"] = 40.0
        protocol_data["epochs"] = []
        
        protocol = StimulusProtocolSchema(**protocol_data)
        engine = SimulationEngine(self.model, protocol)
        results = engine.run(duration_ms=200, steps=200)

        # Check for a sustained positive (outward) current
        self.assertTrue(np.all(results["total_current_pA"][10:] > 0)) # Check after initial transient
        # Internal K+ should decrease
        self.assertLess(results["internal_K_mM"][-1], results["internal_K_mM"][0])
        # External K+ should increase
        self.assertGreater(results["external_K_mM"][-1], results["external_K_mM"][0])

    def test_zero_conductance_model(self):
        """If all states have zero conductance, current must be zero."""
        model_data = create_valid_model_data()
        # Set all conductances to zero
        for state in model_data["states"]:
            state["conductance"] = 0.0
        
        zero_conductance_model = ChannelModelSchema(**model_data)
        engine = SimulationEngine(zero_conductance_model, self.protocol)
        results = engine.run(duration_ms=300, steps=100)

        # Total conductance and current must be zero throughout
        self.assertTrue(np.all(results["total_conductance_nS"] == 0.0))
        self.assertTrue(np.all(results["total_current_pA"] == 0.0))
        # Concentrations should not change if there's no current
        self.assertAlmostEqual(results["internal_K_mM"][0], results["internal_K_mM"][-1])
        self.assertAlmostEqual(results["external_K_mM"][0], results["external_K_mM"][-1])


# --- Main execution block to run tests ---
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
