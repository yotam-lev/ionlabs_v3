<script>
	import HoldingValueTable from './stimulus-modal/HoldingValueTable.svelte';

    import FluxTable from './stimulus-modal/FluxTable.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    function closeModal() {
        dispatch('close');
    }

    // The modal now owns the state for the holding values
    let holdingValues = [
        {
            name: 'Voltage',
            value: 0,
            delta: 0,
            units: 'mV',
            type: 'voltage', // Used to determine which units are "reasonable"
            fluxSteps: [
                { type: 'Step', value: 0, delta: 0, time: 1000, deltaTime: 0 },
            ]
        },
        {
            name: 'External-Br',
            value: 100,
            delta: 0,
            units: 'mM',
            type: 'concentration',
            fluxSteps: [
                { type: 'Step', value: 100, delta: 0, time: 1000, deltaTime: 0 },
                { type: 'Ramp', value: 50, delta: 0, time: 500, deltaTime: 0 },
            ]
        },
        {
            name: 'Internal-Br',
            value: 100,
            delta: 0,
            units: 'mM',
            type: 'concentration',
            fluxSteps: [
                { type: 'Step', value: 100, delta: 0, time: 1000, deltaTime: 0 },
            ]
        },
    ];

    // Keep track of the currently selected stimulus, defaulting to the first one
    let selectedStimulus = holdingValues[0];

</script>

<div class="modal-backdrop" on:click={closeModal}>
    <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
            <h2>Stimulus Configuration</h2>
            <button class="close-button" on:click={closeModal}>×</button>
        </div>
        
        <div class="modal-body">
            <div class="header">
                <button>Fix Problems</button>
                <span>Sweep Duration (ms): <input type="number" value="1000"/></span>
                <span>Sweeps: <input type="number" value="1" /></span>
            </div>

            <!-- Pass the data down and bind the selection back up to the parent -->
            <HoldingValueTable 
                bind:holdingValues 
                bind:selectedStimulus 
            />

            <!-- The FluxTable is now driven by the selectedStimulus -->
            {#if selectedStimulus}
                <FluxTable stimulus={selectedStimulus} />
            {/if}

            <div class="footer">
                <button on:click={closeModal}>Close</button>
            </div>
        </div>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
    }
    .modal-content {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        width: 90%;
        max-width: 800px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    h2 {
        margin: 0;
        font-size: 1.5rem;
    }
    .close-button {
        background: none;
        border: none;
        font-size: 2rem;
        line-height: 1;
        cursor: pointer;
        color: #6c757d;
    }
    .modal-body {
        padding-top: 0.5rem;
    }
    .header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    .footer {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #e9ecef;
    }
</style>
