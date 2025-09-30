import json
from typing import List, Dict

# This import was missing
import matplotlib.pyplot as plt
import numpy as np
import sympy
# Corrected sympy import statement
from sympy.parsing.sympy_parser import parse_expr
from pydantic import BaseModel, Field
from scipy.integrate import solve_ivp


from schemas import ChannelModelSchema, StimulusProtocolSchema

# --- Stimulus Class (Corrected) ---

class Stimulus:
    """A helper class to get the value of any stimulus variable at a given time."""
    def __init__(self, protocol: StimulusProtocolSchema):
        self.protocol = protocol

    def get_value_at_time(self, variable_name: str, t_ms: float) -> float:
        """
        Finds the value of a variable at a specific time t_ms by checking epochs.
        If no epoch is active, returns the holding value.
        """
        # Default to the holding value
        value = getattr(self.protocol.holding_values, variable_name)

        # Check if any epoch overrides the holding value at this time
        for epoch in self.protocol.epochs:
            if epoch.variable == variable_name:
                start = epoch.start_time_ms
                end = start + epoch.duration_ms
                if start <= t_ms < end:
                    return epoch.value
        
        return value


# --- Simulation Engine (Corrected) ---

class SimulationEngine:
    """
    Orchestrates the ion channel simulation.
    """
    def __init__(self, model: ChannelModelSchema, protocol: StimulusProtocolSchema):
        self.model = model
        self.protocol = protocol
        self.stimulus = Stimulus(protocol)

        # Store state information
        self.state_map = {state.id: i for i, state in enumerate(model.states)}
        self.num_states = len(model.states)
        self.conductances = np.array([state.conductance for state in model.states])

        # Physical constants
        self.R = 8.314  # Ideal gas constant
        self.F = 96485  # Faraday constant
        self.T = 293.15 # Temperature in Kelvin (20 C)
        self.z = 1      # Valence of K+

        #volume of cells currently using place holders, will need to change this to a user changable variable at some point
        self.volume_internal_L = getattr(self.protocol.holding_values, 'volume_internal_L', 1e-12)
        self.volume_external_L = getattr(self.protocol.holding_values, 'volume_external_L', 1e-6)
        
        self._prepare_rate_equations()

    def _prepare_rate_equations(self):
        """
        Parses all unique rate equation strings from the model using SymPy and
        converts them into fast, callable numerical functions.
        """
        V = sympy.symbols('V')
        allowed_symbols = {'V': V, 'exp': sympy.exp}

        self._rate_functions = {}

        for func in self.model.rate_functions:
            if func.id not in self._rate_functions:
                parsed_expr = parse_expr(func.equation, local_dict=allowed_symbols)
                self._rate_functions[func.id] = sympy.lambdify(V, parsed_expr, 'numpy')


    def _ode_system(self, t_s, y):
        """
        The system of ODEs for the channel state probabilities, using a Q-matrix.
        """
        t_ms = t_s * 1000.0
        V = self.stimulus.get_value_at_time('voltage_mV', t_ms)


        probabilities = y[:self.num_states]
        internal_K_mM = y[self.num_states]
        external_K_mM = y[self.num_states + 1]


        # Initialize the transition matrix Q
        Q = np.zeros((self.num_states, self.num_states))

        #Build the Q-matrix using the refractored transition schema
        for trans in self.model.transitions:
            from_idx, to_idx = self.state_map[trans.from_state], self.state_map[trans.to_state]
            rate = self._rate_functions[trans.rate_function_id](V) * trans.multiplier
            Q[to_idx, from_idx] += rate
            Q[from_idx, from_idx] -= rate
        d_probabilities_dt = Q @ probabilities

        if internal_K_mM <= 0 or external_K_mM <= 0:
            nernst_potential = 0
            total_current_pA = 0
        else:
            nernst_potential = ((self.R * self.T) / (self.z * self.F) * np.log(external_K_mM / internal_K_mM)) * 1000
        
        total_conductance = self.conductances @ probabilities
        total_current_pA = total_conductance * (V - nernst_potential)

        current_A = total_current_pA * 1e-12
        flux_mol_s = current_A/(self.z * self.F)
        flux_mmol_s = flux_mol_s * 1000

        #Calculate concentration change rate 
        d_internal_K_dt = -flux_mmol_s/self.volume_internal_L
        d_external_K_dt = flux_mmol_s/self.volume_external_L

        dydt = np.concatenate((d_probabilities_dt, [d_internal_K_dt], [d_external_K_dt]))
        return dydt

    def run(self, duration_ms: float, steps: int):
        """
        Runs the full simulation.
        """
        print(f"🔬 Running simulation for '{self.model.channel_id}'...")

        # Initial conditions: start in the first defined state
        y0_probs = np.zeros(self.num_states)
        y0_probs[0] = 1.0
        
        # --- FIX ---: Correctly access the nested holding_values attributes
        y0_int_k = self.protocol.holding_values.internal_K_mM
        y0_ext_k = self.protocol.holding_values.external_K_mM
        
        y0 = np.concatenate((y0_probs, [y0_int_k], [y0_ext_k]))

        t_span_s = [0, duration_ms / 1000.0]
        t_eval_s = np.linspace(t_span_s[0], t_span_s[1], steps)

        solution = solve_ivp(
            fun=self._ode_system,
            t_span=t_span_s, y0=y0, t_eval=t_eval_s,
            method='RK45', rtol=1e-6, atol=1e-9
        )

        # --- Post-processing ---
        time_ms = solution.t * 1000.0
        probabilities = solution.y[:self.num_states, :]
        internal_K_trace = solution.y[self.num_states, :]
        external_K_trace = solution.y[self.num_states + 1, :]

        # Recalculate final traces using the time varying results
        voltage_trace = np.array([self.stimulus.get_value_at_time('voltage_mV', t) for t in time_ms])
        
        # Avoid division by zero if concentrations drop to or below zero
        # Create a mask for valid concentration values
        valid_concs = (internal_K_trace > 0) & (external_K_trace > 0)
        nernst_potential_trace = np.zeros_like(time_ms)
        nernst_potential_trace[valid_concs] = ((self.R * self.T) / (self.z * self.F) * np.log(external_K_trace[valid_concs] / internal_K_trace[valid_concs])) * 1000

        total_conductance_trace = self.conductances @ probabilities
        total_current_pA_trace = total_conductance_trace * (voltage_trace - nernst_potential_trace)

        print("✅ Simulation complete.")
        return {
            "time_ms": time_ms,
            "voltage_mV": voltage_trace,
            "probabilities": probabilities,
            "total_conductance_nS": total_conductance_trace,
            "total_current_pA": total_current_pA_trace,
            "internal_K_mM": internal_K_trace,
            "external_K_mM": external_K_trace,
            "nernst_potential_mV": nernst_potential_trace,
            "state_map": self.state_map
        }

