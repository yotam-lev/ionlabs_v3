<script>
    import { createEventDispatcher } from 'svelte';

    export let holdingValues = [];
    export let selectedStimulus = null;

    const dispatch = createEventDispatcher();

    // Define reasonable units for different types of measurements
    const unitOptions = {
      voltage: ['mV', 'V'],
      concentration: ['mM', 'µM', 'nM', 'pM'],
    };

    function selectStimulus(stimulus) {
        // This two-way binding will update the parent's selectedStimulus variable
        selectedStimulus = stimulus;
    }
</script>

<div class="holding-values-container">
    <h3>Holding Values</h3>
    <table>
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Value</th>
                <th>Delta</th>
                <th>Units</th>
                <th>Final Value</th>
            </tr>
        </thead>
        <tbody>
            {#each holdingValues as row (row.name)}
                <tr on:click={() => selectStimulus(row)} class:selected={selectedStimulus === row}>
                    <td>{selectedStimulus === row ? '▶' : ''}</td>
                    <td>{row.name}</td>
                    <td><input type="number" bind:value={row.value} class="value-input"/></td>
                    <td><input type="number" bind:value={row.delta} class="value-input"/></td>
                    <td>
                        <select bind:value={row.units}>
                            {#each unitOptions[row.type] || [row.units] as unit}
                                <option value={unit}>{unit}</option>
                            {/each}
                        </select>
                    </td>
                    <td>{row.value + row.delta}</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

<style>
    .holding-values-container {
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }

    h3 {
        margin-top: 0;
        color: #333;
        font-size: 1.1em;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }

    th {
        background-color: #eee;
        font-weight: bold;
    }

    tbody tr {
        cursor: pointer;
        transition: background-color 0.2s;
    }

    tbody tr:hover {
        background-color: #f0f0f0;
    }

    .selected {
        background-color: #d_e_9_f_f_f; /* A light blue to indicate selection */
        font-weight: bold;
    }
    
    .value-input {
        width: 80px;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px;
    }

    select {
        padding: 4px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: white;
    }
</style>
