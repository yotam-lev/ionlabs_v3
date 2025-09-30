use serde::{Serialize, Deserialize};

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