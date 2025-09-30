"""
Unit and integration tests for validating schemas and running the simulation engine.
This file tests the Pydantic models and also runs the SimulationEngine with a
complex model to verify the output.
"""

import unittest
import json
import os
import numpy as np
from pydantic import ValidationError

# Import the schemas to be tested
from schemas import ChannelModelSchema, StimulusProtocolSchema
# Import the engine for integration testing
from simulation import SimulationEngine

# --- Test Data ---

VALID_CHANNEL_DATA = {
    "channel_id": "SimpleVoltageGatedK",
    "states": [
        {"id": "C", "name": "Closed", "conductance": 0.0},
        {"id": "O", "name": "Open", "conductance": 15.0}
    ],
    "transitions": [
        {"from": "C", "to": "O", "rate_equation": "0.1 * exp(V / 25.0)"},
        {"from": "O", "to": "C", "rate_equation": "0.05 * exp(-V / 20.0)"}
    ]
}

INVALID_CHANNEL_NEGATIVE_CONDUCTANCE = {
    "channel_id": "InvalidConductance",
    "states": [{"id": "C", "name": "Closed", "conductance": -5.0}], # <-- INVALID
    "transitions": []
}

INVALID_CHANNEL_BAD_TRANSITION = {
    "channel_id": "InvalidTransition",
    "states": [{"id": "C", "name": "Closed", "conductance": 0.0}],
    "transitions": [{"from": "C", "to": "X", "rate_equation": "0.1"}] # <-- INVALID
}

VALID_PROTOCOL_DATA = {
    "protocol_id": "VoltageStep_Neg70_to_Pos40",
    "holding_values": {
        "voltage_mV": -70.0,
        "internal_K_mM": 140.0,
        "external_K_mM": 5.0
    },
    "epochs": [{
        "variable": "voltage_mV",
        "start_time_ms": 50.0,
        "duration_ms": 200.0,
        "value": 40.0
    }]
}

INVALID_PROTOCOL_BAD_EPOCH_VAR = {
    "protocol_id": "InvalidEpochVariable",
    "holding_values": {"voltage_mV": -80.0, "internal_K_mM": 150.0, "external_K_mM": 4.0},
    "epochs": [{"variable": "voltage", "start_time_ms": 10, "duration_ms": 100, "value": 0}] # <-- INVALID
}

# --- Data for Hodgkin-Huxley K+ Channel Integration Test ---

# A more complex, 5-state model approximating a Hodgkin-Huxley K+ channel
HH_K_CHANNEL_MODEL = {
    "channel_id": "HodgkinHuxley_K",
    "states": [
        {"id": "C4", "name": "C4", "conductance": 0.0},
        {"id": "C3", "name": "C3", "conductance": 0.0},
        {"id": "C2", "name": "C2", "conductance": 0.0},
        {"id": "C1", "name": "C1", "conductance": 0.0},
        {"id": "O", "name": "Open", "conductance": 20.0}
    ],
    "transitions": [
        # alpha_n = 0.01 * (V + 55) / (1 - exp(-(V + 55) / 10))
        # beta_n = 0.125 * exp(-(V + 65) / 80)
        {"from": "C4", "to": "C3", "rate_equation": "4 * (0.01 * (V + 55) / (1 - exp(-(V + 55) / 10)))"},
        {"from": "C3", "to": "C4", "rate_equation": "1 * (0.125 * exp(-(V + 65) / 80))"},
        {"from": "C3", "to": "C2", "rate_equation": "3 * (0.01 * (V + 55) / (1 - exp(-(V + 55) / 10)))"},
        {"from": "C2", "to": "C3", "rate_equation": "2 * (0.125 * exp(-(V + 65) / 80))"},
        {"from": "C2", "to": "C1", "rate_equation": "2 * (0.01 * (V + 55) / (1 - exp(-(V + 55) / 10)))"},
        {"from": "C1", "to": "C2", "rate_equation": "3 * (0.125 * exp(-(V + 65) / 80))"},
        {"from": "C1", "to": "O", "rate_equation": "1 * (0.01 * (V + 55) / (1 - exp(-(V + 55) / 10)))"},
        {"from": "O", "to": "C1", "rate_equation": "4 * (0.125 * exp(-(V + 65) / 80))"}
    ]
}

# A protocol to activate and then deactivate the HH K+ channel
HH_ACTIVATION_PROTOCOL = {
    "protocol_id": "HH_K_Activation_Deactivation",
    "holding_values": {
        "voltage_mV": -80.0,
        "internal_K_mM": 150.0,
        "external_K_mM": 4.0
    },
    "epochs": [
        {
            "variable": "voltage_mV",
            "start_time_ms": 100,
            "duration_ms": 400,
            "value": 50.0
        }
    ]
}


class TestValidationAndSimulation(unittest.TestCase):
    """Test suite for validating schemas and running the simulation engine."""

    # --- Schema Unit Tests ---
    
    def test_valid_channel_model(self):
        """Tests that a valid channel model dictionary is parsed successfully."""
        try:
            ChannelModelSchema(**VALID_CHANNEL_DATA)
        except ValidationError as e:
            self.fail(f"Valid channel data failed validation unexpectedly: {e}")

    def test_invalid_negative_conductance(self):
        """Tests that validation fails if a state has negative conductance."""
        with self.assertRaises(ValidationError):
            ChannelModelSchema(**INVALID_CHANNEL_NEGATIVE_CONDUCTANCE)

    def test_invalid_transition_state(self):
        """Tests that validation fails if a transition refers to a non-existent state."""
        with self.assertRaises(ValidationError):
            ChannelModelSchema(**INVALID_CHANNEL_BAD_TRANSITION)

    def test_valid_stimulus_protocol(self):
        """Tests that a valid stimulus protocol dictionary is parsed successfully."""
        try:
            StimulusProtocolSchema(**VALID_PROTOCOL_DATA)
        except ValidationError as e:
            self.fail(f"Valid protocol data failed validation unexpectedly: {e}")

    def test_invalid_epoch_variable(self):
        """Tests that validation fails if an epoch variable is not a valid name."""
        with self.assertRaises(ValidationError):
            StimulusProtocolSchema(**INVALID_PROTOCOL_BAD_EPOCH_VAR)
            
    def test_simulation_file_workflow(self):
        """
        Tests the full workflow: creating, writing, reading, and validating
        the model and protocol JSON files.
        """
        model_path = "test_model.json"
        protocol_path = "test_protocol.json"
        
        with open(model_path, 'w') as f:
            json.dump(VALID_CHANNEL_DATA, f, indent=4)
        with open(protocol_path, 'w') as f:
            json.dump(VALID_PROTOCOL_DATA, f, indent=4)

        try:
            with open(model_path, 'r') as f:
                loaded_model = json.load(f)
            with open(protocol_path, 'r') as f:
                loaded_protocol = json.load(f)
            
            ChannelModelSchema(**loaded_model)
            StimulusProtocolSchema(**loaded_protocol)
            
        except Exception as e:
            self.fail(f"Full file workflow test failed unexpectedly: {e}")
            
        finally:
            if os.path.exists(model_path):
                os.remove(model_path)
            if os.path.exists(protocol_path):
                os.remove(protocol_path)

    # --- Simulation Integration Test ---

    def test_hodgkin_huxley_k_channel_simulation(self):
        """
        An integration test that runs the simulation with a complex
        Hodgkin-Huxley K+ channel model and verifies the output current.
        """
        # 1. Validate the complex model and protocol
        model = ChannelModelSchema(**HH_K_CHANNEL_MODEL)
        protocol = StimulusProtocolSchema(**HH_ACTIVATION_PROTOCOL)

        # 2. Initialize and run the simulation engine
        engine = SimulationEngine(model=model, protocol=protocol)
        results = engine.run(duration_ms=600, steps=2000)

        # 3. Perform assertions on the results
        self.assertIn("time_ms", results)
        self.assertIn("total_current_pA", results)
        
        time = results["time_ms"]
        current = results["total_current_pA"]
        probabilities = results["probabilities"]
        open_prob = probabilities[model.state_map['O']] # Probability of the 'Open' state
        conductance = results["total_conductance_nS"]
        voltage = results["voltage_mV"]
        
        # --- DEBUGGING PRINTS ---
        print("\n--- Hodgkin-Huxley Test Debug ---")

        # The current should be near zero at the beginning (t=50ms)
        start_current = current[np.where(time >= 50)[0][0]]
        self.assertAlmostEqual(start_current, 0.0, delta=1.0, msg="Current should be near zero before activation.")

        # The current should rise to a significant positive peak during the voltage step (t=100 to 500ms)
        activation_mask = np.where((time > 100) & (time <= 500))
        activation_phase_current = current[activation_mask]
        
        peak_current_index = np.argmax(activation_phase_current)
        peak_current = activation_phase_current[peak_current_index]
        
        # Find the index in the original, full arrays
        peak_time_index = activation_mask[0][peak_current_index]

        print(f"Peak Current Value: {peak_current:.2f} pA (Expected > 100 pA)")
        print(f"Time of Peak Current: {time[peak_time_index]:.2f} ms")
        print(f"Max Open Probability (P(O)): {np.max(open_prob):.3f}")
        print(f"Conductance at Peak: {conductance[peak_time_index]:.2f} nS")
        
        # Calculate driving force (V_m - E_k)
        # E_k is roughly -94mV for these concentrations
        driving_force = voltage[peak_time_index] - (-94) 
        print(f"Voltage at Peak: {voltage[peak_time_index]:.1f} mV")
        print(f"Driving Force (V - E_k) at Peak: {driving_force:.1f} mV")
        print("-----------------------------------\n")

        self.assertGreater(peak_current, 100.0, msg="Peak activation current is too low.")

        # The current should decay back towards zero after the step (t > 500ms)
        end_current = current[-1]
        self.assertLess(end_current, peak_current / 2, msg="Current did not deactivate sufficiently.")
        self.assertAlmostEqual(end_current, 0.0, delta=10.0, msg="Current should return near zero after deactivation.")


if __name__ == '__main__':
    unittest.main(verbosity=2)

