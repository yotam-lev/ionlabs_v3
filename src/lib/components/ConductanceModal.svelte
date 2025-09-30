<!--
  ConductanceModal.svelte
  A modal for setting the permeation model and defining ion conductances or permeabilities.
-->
<script lang="ts">
  import { createEventDispatcher } from "svelte";

  // This prop will be used to show or hide the modal from the parent component
  export let showModal = false;

  const dispatch = createEventDispatcher();

  // --- State Management ---

  // 'ohm' for Ohm's Law, 'ghk' for Goldman-Hodgkin-Katz
  let selectedModel = "ohm";

  // List of ions for the dropdown
  const ionOptions = [
    "Na⁺",
    "K⁺",
    "Cl⁻",
    "Ca²⁺",
    "Mg²⁺",
    "Br⁻",
    "F⁻",
    "I⁻",
    "Li⁺",
    "Cs⁺",
    "Rb⁺",
    "H⁺",
    "OH⁻",
    "HCO₃⁻",
    "SO₄²⁻",
  ];

  // The master list of conductance/permeability entries
  let entries = [{ id: 1, ion: "K⁺", value: 1.0 }];
  let nextId = 2;

  // --- Functions ---

  function addEntry() {
    const newEntry = {
      id: nextId++,
      ion: ionOptions[0],
      value: 1.0,
    };
    entries = [...entries, newEntry];
  }

  function removeEntry(id: number) {
    entries = entries.filter((entry) => entry.id !== id);
  }

  function handleClose() {
    dispatch("close");
  }

  function handleSubmit() {
    // In a real app, you would dispatch the data to the parent here.
    console.log("Submitting data:", { model: selectedModel, entries });
    handleClose();
  }

  // Reactive properties that depend on the selected model
  $: tableHeader = selectedModel === "ohm" ? "Conductance" : "Permeability";
  $: units = selectedModel === "ohm" ? "pS" : "10⁻¹⁵ cm³/s";
  $: type = selectedModel === "ohm" ? "Ohmic" : "GHK";
</script>

<!-- The modal is only rendered if showModal is true -->
{#if showModal}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="modal-backdrop" on:click={handleClose}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-content" on:click|stopPropagation>
      <header class="modal-header">
        <h2>Permeation Model</h2>
        <button class="close-button" on:click={handleClose}>&times;</button>
      </header>

      <div class="modal-body">
        <!-- Permeation Model Selection -->
        <fieldset class="permeation-model">
          <legend>Permeation Model</legend>
          <div class="model-list">
            <label class="model-row">
              <div class="model-name">
                <input type="radio" bind:group={selectedModel} value="ohm" />
                <span>Ohm's Law</span>
              </div>
              <div class="model-formula" aria-label="Ohm's law formula">
                I = g · (V − E)
              </div>
            </label>
            <label class="model-row">
              <div class="model-name">
                <input type="radio" bind:group={selectedModel} value="ghk" />
                <span>Goldman-Hodgkin-Katz</span>
              </div>
              <div class="model-formula" aria-label="GHK equation">
                E = (RT / zF) · ln( (P_K[K^+]<sub>o</sub> + P_Na[Na^+]<sub
                  >o</sub
                >
                + P_Cl[Cl^-]<sub>i</sub>) / (P_K[K^+]<sub>i</sub> + P_Na[Na^+]<sub
                  >i</sub
                >
                + P_Cl[Cl^-]<sub>o</sub>) )
              </div>
            </label>
          </div>
        </fieldset>

        <!-- Add Conductances Table -->
        <fieldset class="add-conductances">
          <legend>Add {tableHeader}s</legend>
          <div class="table-toolbar">
            <button
              on:click={addEntry}
              class="add-button"
              aria-label="Add entry">+</button
            >
            <!-- Add pagination controls if needed -->
          </div>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Ion</th>
                  <th>{tableHeader}</th>
                  <th>Units</th>
                  <th>Type</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {#each entries as entry (entry.id)}
                  <tr>
                    <td>{entry.id}</td>
                    <td>
                      <select bind:value={entry.ion}>
                        {#each ionOptions as ion}
                          <option value={ion}>{ion}</option>
                        {/each}
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.1"
                        bind:value={entry.value}
                      />
                    </td>
                    <td>{units}</td>
                    <td>{type}</td>
                    <td>
                      <button
                        class="remove-button"
                        aria-label={`Remove entry ${entry.id}`}
                        on:click={() => removeEntry(entry.id)}
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </fieldset>
      </div>

      <footer class="modal-footer">
        <button class="secondary-button" on:click={handleClose}>Cancel</button>
        <button class="primary-button" on:click={handleSubmit}>OK</button>
      </footer>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-content {
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 90%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #ddd;
    background-color: #f1f3f5;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #888;
  }

  .modal-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  fieldset {
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 1rem;
  }

  legend {
    font-weight: 600;
    padding: 0 0.5rem;
  }

  .model-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .model-row {
    display: grid;
    grid-template-columns: auto 1fr;
    align-items: center;
    gap: 1rem;
  }

  .model-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
  }

  .model-formula {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
    font-size: 0.9rem;
    color: #374151;
    white-space: nowrap;
    overflow-x: auto;
  }

  .table-toolbar {
    margin-bottom: 0.5rem;
  }

  .add-button {
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .table-container {
    max-height: 200px;
    overflow-y: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f1f3f5;
    position: sticky;
    top: 0;
  }

  input,
  select {
    width: 100%;
    padding: 4px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .remove-button {
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    cursor: pointer;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid #ddd;
  }

  button {
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid transparent;
    cursor: pointer;
  }

  .primary-button {
    background-color: #007bff;
    color: white;
  }

  .secondary-button {
    background-color: #6c757d;
    color: white;
  }
</style>
