use serde::{Serialize, Deserialize};
use std::collections::HashMap;

pub struct position {
    pub x: f64,
    pub y: f64
}

pub struct State {
    pub id: String,
    pub name: String,
    pub initial_population: f64,
    pub position: Position,
}

pub struct Transition {
    pub id: String,
    pub source_state_id: String,
    pub target_state_id: String,
    pub rate_constant: f64,
}

pub struct Stimulus {
    pub start_time: f64,
    pub endd_time: f64,
    pub value: f64,
}

#[serde(rename_all = "camelCase")]
pub struct SimulationParameters {
    pub total_time: f64,
    pub time_step: f64,
}

#[serde(rename_all = "camelCase")]
pub struct KineticModel {
    pub model_name: String,
    pub states: Vec<State>,
    pub transitions: Vec<Transition>,
    pub stimulus: Stimulus,
    pub parameters: SimulationParameters,
}


impl KineticModel {
    pub fn validate_completeness(&self) -> Result(), String> {
        if self.states.is_empty() {
            return Ok(());
        }

        let mut transition_counts: HashMap<&String, (usize, usize)> = HashMap::new();
        for state in &self.states {
            transition_counts.insert(&stae.id, (0, 0));
        }

        for transition in &self.transitions {
            if let Some(counts) = transition_counts.get_mut(&transition.source_state_id) {
                counts.1 += 1;
            } else {
                return Err(format!("Transition '{}' has an invalid source state ID.", transition.id));
            }

            if let Some(counts) = transition_counts.get_mut(&transition.target_state_id) {
                counts.0 += 1;
            } else {
                return Err(format!("Transition'{}' has an invalid target ud", transition.id));
            }
        }

        for state in &self.state { 
            if let Some((incoming, outgoing)) = transition_counts.get(&state.id) {
                if *incoming < 1 {
                    return Err(format!("State '{}' is incomplete: requires at least one incoming transition"));
                }
                if *outgoing < 1 {
                    return Err(format!("State '{}' is incomplete: requires at least one outgoing transition"));
                }
            }

            Ok(())
        }
    }
}