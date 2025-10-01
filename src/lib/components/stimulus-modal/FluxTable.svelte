<script>
    export let stimulus;

    let currentPage = 1;

    // These are now derived from the stimulus prop
    $: fluxSteps = stimulus.fluxSteps;
    $: totalPages = fluxSteps.length > 0 ? fluxSteps.length : 1;

    function addRow() {
        stimulus.fluxSteps = [
            ...stimulus.fluxSteps,
            { type: 'Step', value: 0, delta: 0, time: 0, deltaTime: 0 }
        ];
        currentPage = stimulus.fluxSteps.length; // Go to the new row
    }

    function deleteRow(index) {
        stimulus.fluxSteps.splice(index, 1);
        stimulus.fluxSteps = stimulus.fluxSteps; // Trigger reactivity
        if (currentPage > stimulus.fluxSteps.length && currentPage > 1) {
            currentPage--;
        }
    }

    function goToPage(page) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
        }
    }

    // When the stimulus changes, reset to the first page
    $: if (stimulus) {
        currentPage = 1;
    }
</script>

{#if stimulus}
<div class="flux-table-container">
    <div class="controls-row">
        <div class="variable-label">Variable: {stimulus.name}</div>
        <div class="navigation-buttons">
            <button on:click={() => goToPage(1)} disabled={currentPage === 1}>&lt;&lt;</button>
            <button on:click={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>&lt;</button>
            <span>{currentPage} of {totalPages}</span>
            <button on:click={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>&gt;</button>
            <button on:click={() => goToPage(totalPages)} disabled={currentPage === totalPages}>&gt;&gt;</button>
            <button on:click={addRow}>➕</button>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th></th>
                <th>Type</th>
                <th>Value</th>
                <th>Delta</th>
                <th>Time</th>
                <th>DeltaTime</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {#if fluxSteps && fluxSteps[currentPage - 1]}
                {@const row = fluxSteps[currentPage - 1]}
                {@const i = currentPage - 1}
                <tr>
                    <td>▶</td>
                    <td>
                        <select bind:value={row.type}>
                            <option value="Step">Step</option>
                            <option value="Ramp">Ramp</option>
                        </select>
                    </td>
                    <td><input type="number" bind:value={row.value} /></td>
                    <td><input type="number" bind:value={row.delta} /></td>
                    <td><input type="number" bind:value={row.time} /></td>
                    <td><input type="number" bind:value={row.deltaTime} /></td>
                    <td><button on:click={() => deleteRow(i)}>🗑️</button></td>
                </tr>
            {/if}
        </tbody>
    </table>
</div>
{/if}

<style>
    .flux-table-container {
        border: 1px solid #ccc;
        padding: 10px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }

    .controls-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    }

    .variable-label {
        font-weight: bold;
        color: #333;
        font-size: 1.1em;
    }

    .navigation-buttons button {
        margin: 0 2px;
        padding: 3px 8px;
        cursor: pointer;
        background-color: #e0e0e0;
        border: 1px solid #bbb;
        border-radius: 3px;
    }

    .navigation-buttons button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .navigation-buttons span {
        margin: 0 5px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }

    th,
    td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }

    th {
        background-color: #eee;
        font-weight: bold;
    }

    input[type="number"],
    select {
        width: 90%; /* Adjust as needed */
        padding: 4px;
        border: 1px solid #ccc;
        border-radius: 3px;
    }
</style>
