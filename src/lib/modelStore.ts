import { writable } from "svelte/store";

export const kineticModelStore = writable({
    model_name: "New Model",
    states:,
    transition:,
    stimulus: {start_time: 0, end_time: 100, value: -80 },
    paramaters: { total_time: 200, time_step: 0.1}
});