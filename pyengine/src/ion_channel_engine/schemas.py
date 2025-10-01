"""
Defines the Pydantic data models for validating the ion channel model and 
stimulus protocol JSON files. This ensures that the simulation engine 
only receives data with the correct structure, types, and constraints.
"""

import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from collections import defaultdict

# --- Channel Model Schemas ---

class KineticModel(BaseModel):
    model_name: str
    states: list
    transitions: list
    rate_equations: list
    stimulus protocol

class State(BaseModel):
    """Defines a single conformational state of the ion channel."""
    id: str = Field(..., min_length=1, description="A short, unique identifier for the state (e.g., 'C', 'O').")
    name: str = Field(..., min_length=1, description="A descriptive name for the state (e.g., 'Closed', 'Open').")
    conductance: float = Field(..., ge=0, description="The electrical conductance in this state (nS). Must be >= 0.")


class RateFunction(BaseModel):
    """Defines a reusable rate equation formula."""
    id: str = Field(..., min_length=1, description= "Unique identifier for the rate function")
    equation: str = Field(..., min_length=1, description="The mathematical formula as a string")


class Transition(BaseModel):
    """Defines a transition between two states."""
    # Using alias to allow the use of the Python keyword 'from' in the JSON file
    from_state: str = Field(..., alias='from', description="The 'id' of the starting state for the transition.")
    to_state: str = Field(..., alias='to', description="The 'id' of the ending state for the transition.")
    rate_function_id: str = Field(..., description="The id' of the rate function to use for this transition")
    multiplier: float = Field(default=1.0, gt=0, description=" An optional multiplier for the rate function")

class ChannelModel(BaseModel):
    """
    Validates the entire structure for an ion channel model, including its states
    and the transitions between them.
    """
    channel_id: str = Field(..., min_length=1, description="A unique name for the channel model.")
    states: List[State] = Field(..., min_items=1, description="A list of all possible channel states.")
    rate_functions: List[RateFunction] = Field(..., min_items=1, description="A list of reusable transition rate equations")
    transitions: List[Transition] = Field(..., description="A list defining the transitions between states.")

    @field_validator('transitions')
    def check_transition_states_exist(cls, transitions, info):
        """
        Custom validator to ensure that every 'from' and 'to' field in a transition
        refers to a state 'id' that has been defined in the 'states' list.
        """
        # The 'info' object contains a 'values' dictionary with the model's data.
        values = info.data
        if 'states' not in values or 'rate_functions' not in values:
            return transitions 
            
        defined_state_ids = {state.id for state in values['states']}
        defined_function_ids = {func.id for func in values['rate_functions']}

        errors = []
        for i, transition in enumerate(transitions):
            if transition.from_state not in defined_state_ids:
                errors.append(f"Transition {i}: 'from_state' '{transition.from_state}' is not a defined state id.")
            if transition.to_state not in defined_state_ids:
                errors.append(f"Transition {i}: 'to_state' '{transition.to_state}' is not a defined state id.")
            if transition.rate_function_id not in defined_function_ids:
                errors.append(f"Transition {i}: 'rate_function_id' '{transition.rate_function_id}' is not a defined function id.")
        
        if errors:
            raise ValueError(". ".join(errors))

        return transitions 
    
    @field_validator(mode='after')
    def check_model_completeness(self) -> 'ChannelModel':
        if not self.states:
            return self
        
        state_ids = { s.id for s in self.states }
        transition_counts = defaultdict(lambda: {'incoming': 0, 'outgoing': 0})

        for t in self.transitions:
            if t.source_state_id not in state_ids:
                raise ValueError(f"Transition '{t.id}' references a non-existent source state '{t.source_state_id}'")
            if t.target_state_id not in state_ids:
                raise ValueError(f"Transition '{t.d}' references a non existant target state '{t.target_state_id}'")
            
            transition_counts[t.source_stae_id]['outgoing'] += 1
            transition_counts[t.target_state_id]['incoming'] += 1
        
        for state in self.states: 
            counts = transition_counts[state.id]
            if counts['incoming'] < 1:
                raise ValueError(f" state '{state.name}' ({state.id}) is incomplete: it must have at least 1 incoming transition")
                        if counts['outgoing'] < 1:
                raise ValueError(f" state '{state.name}' ({state.id}) is incomplete: it must have at least 1 outgoing transition")
            
        return self
    


# --- Stimulus Protocol Schemas ---


class FluxStep(BaseModel):

    type: Literal['Step', 'Ramp']
    value: float
    delta: float
    time: float
    deltaTime: float

class HoldingValues(BaseModel):
    """Defines the baseline, steady-state conditions of the simulation."""
    name: str
    value: float
    deelta: float
    units: str
    type: Literal['voltage', 'concentration']

class StimulusProtocolSchema(BaseModel):
    protocol_id: str
    holding_values: List[HoldingValue]
    sweep_duration_ms: int = 1000
    sweeps: int = 1
    
    @field_validator('holding_values')
    def check_for_duplicate_names(cls, values):
        names = set()
        for hv in values:
            if hv.name in names:
                raise ValueError(f"Duplicate holding value name found: '{hv.name}'. Names must be unique")
            names.add{hv.name}
        return values



