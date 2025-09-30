"""
Defines the Pydantic data models for validating the ion channel model and 
stimulus protocol JSON files. This ensures that the simulation engine 
only receives data with the correct structure, types, and constraints.
"""

import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator

# --- Channel Model Schemas ---

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

class ChannelModelSchema(BaseModel):
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


# --- Stimulus Protocol Schemas ---

class HoldingValues(BaseModel):
    """Defines the baseline, steady-state conditions of the simulation."""
    voltage_mV: float
    internal_K_mM: float
    external_K_mM: float
    volume_internal_L: Optional[float] = Field(
        None, gt=0, description="Optional: The internal (cell) volume in Liters."
    )
    volume_external_L: Optional[float] = Field(
        None, gt=0, description="Optional: The external (bath) volume in Liters."
    )

class ProtocolEpoch(BaseModel):
    """Defines a specific change to a variable for a set duration."""
    variable: str
    start_time_ms: float = Field(..., ge=0)
    duration_ms: float = Field(..., gt=0)
    value: float

class StimulusProtocolSchema(BaseModel):
    """The complete schema for defining an experimental stimulus protocol."""
    protocol_id: str
    holding_values: HoldingValues
    epochs: List[ProtocolEpoch]

    @field_validator('epochs')
    def check_epoch_variables_are_valid(cls, epochs, info):
        """
        A custom validator to ensure that the 'variable' in each epoch
        corresponds to a valid parameter in the HoldingValues model.
        """
        values = info.data
        if 'holding_values' not in values:
            return epochs # Initial validation pass
            
        # The 'holding_values' object is a Pydantic model, so we call .dict() to get its fields
        valid_vars = set(values['holding_values'].dict().keys())
        errors = []
        for i, epoch in enumerate(epochs):
            if epoch.variable not in valid_vars:
                errors.append(f"Epoch {i}: '{epoch.variable}' is not a valid variable. Must be one of {valid_vars}.")
        
        if errors:
            raise ValueError(". ".join(errors))

        return epochs

