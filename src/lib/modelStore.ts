import { writable, derived } from "svelte/store";

export const kineticModelStore = writable({
    model_name: "New Model",
    states: [],
    transition: [],
    stimulus: {start_time: 0, end_time: 100, value: -80 },
    paramaters: { total_time: 200, time_step: 0.1}
});


export const modelValidation = derived(kineticModelStore, ($model) => {
    const issues =[];
    if (!$model ||!$model.states || $model.states.length === 0) {
        return { isValid: false, issues: ['Model must have at least one state.'] };
    }

    const stateIds = new Set($model.states.map(s => s.id));
    const transitionCounts = new Map();
    stateIds.forEach(id => transitionCounts.set(id, { incoming: 0, outgoing: 0 }));

    for (const t of $model.transitions) {
        if (stateIds.has(t.source_state_id)) {
            transitionCounts.get(t.source_state_id).outgoing++;
        }
        if (stateIds.has(t.target_state_id)) {
            transitionCounts.get(t.target_state_id).incoming++;
        }
    }

    for (const state of $model.states) {
        const counts = transitionCounts.get(state.id);
        if (counts.incoming < 1) {
            issues.push(`State '${state.name}' needs at least one incoming transition.`);
        }
        if (counts.outgoing < 1) {
            issues.push(`State '${state.name}' needs at least one outgoing transition.`);
        }
    }

    return {
        isValid: issues.length === 0,
        issues: issues
    };
});