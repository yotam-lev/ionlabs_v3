<script>
  import { writable } from "svelte/store";
  import { derived } from "svelte/store";

  // --- State Management ---
  const states = writable([]);
  const transitions = writable([]);
  const selectedStateId = writable(null);
  const selectedTransitionId = writable(null);

  let nextStateId = 1;
  let nextTransitionId = 1;

  // --- Interaction Modes ---
  let isAddingTransition = false;
  let transitionStartId = null;
  let symmetricDeleteEnabled = true; // UI toggle; with undirected links it's effectively normal delete

  // --- Dragging State ---
  let draggedStateId = null;
  let wasDragged = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;

  // --- Derived Store for Rendering Lines ---
  const transitionLines = derived(
    [states, transitions],
    ([$states, $transitions]) => {
      const stateMap = new Map($states.map((s) => [s.id, s]));
      return $transitions
        .map((t) => {
          const state1 = stateMap.get(t.states[0]);
          const state2 = stateMap.get(t.states[1]);
          if (!state1 || !state2) return null;

          const stateSize = 60; // from CSS
          return {
            id: t.id,
            x1: state1.x + stateSize / 2,
            y1: state1.y + stateSize / 2,
            x2: state2.x + stateSize / 2,
            y2: state2.y + stateSize / 2,
          };
        })
        .filter(Boolean);
    }
  );

  // --- Functions ---
  function addState() {
    const newState = {
      id: nextStateId++,
      x: 100 + ((nextStateId - 1) % 10) * 20,
      y: 100 + ((nextStateId - 1) % 10) * 20,
      gateStatus: "closed",
    };
    states.update((current) => [...current, newState]);
  }

  function toggleGateStatus() {
    if ($selectedStateId === null) return;
    states.update((current) =>
      current.map((s) =>
        s.id === $selectedStateId
          ? { ...s, gateStatus: s.gateStatus === "closed" ? "open" : "closed" }
          : s
      )
    );
  }

  function toggleAddTransitionMode() {
    isAddingTransition = !isAddingTransition;
    transitionStartId = null;
    selectedStateId.set(null); // Deselect states when entering transition mode
    selectedTransitionId.set(null);
  }

  /**
   * Handles a click on a state. This can either select a state
   * or create a transition, depending on the current mode.
   */
  function handleStateClick(clickedId) {
    if (!isAddingTransition) {
      // Normal mode: select the state
      selectedStateId.set(clickedId);
      selectedTransitionId.set(null);
      return;
    }

    // Transition mode:
    if (transitionStartId === null) {
      // This is the first state clicked
      transitionStartId = clickedId;
    } else {
      // This is the second state clicked, create the transition
      if (transitionStartId !== clickedId) {
        const newTransitionStates = [transitionStartId, clickedId].sort(
          (a, b) => a - b
        );
        const exists = $transitions.some(
          (t) =>
            t.states[0] === newTransitionStates[0] &&
            t.states[1] === newTransitionStates[1]
        );

        if (!exists) {
          transitions.update((current) => [
            ...current,
            { id: nextTransitionId++, states: newTransitionStates },
          ]);
        }
      }
      // Reset and exit transition mode after the second click
      isAddingTransition = false;
      transitionStartId = null;
    }
  }

  function selectTransition(id) {
    selectedTransitionId.set(id);
    selectedStateId.set(null);
  }

  function deleteSelectedTransition() {
    if (!$selectedTransitionId) return;
    const idToDelete = $selectedTransitionId;
    transitions.update((current) => current.filter((t) => t.id !== idToDelete));
    selectedTransitionId.set(null);
  }

  function toggleSymmetricDelete() {
    symmetricDeleteEnabled = !symmetricDeleteEnabled;
  }

  /**
   * Deletes the currently selected state and any transitions connected to it.
   */
  function deleteSelectedState() {
    if ($selectedStateId === null) return;
    const idToDelete = $selectedStateId;

    // Remove the state itself
    states.update((current) => current.filter((s) => s.id !== idToDelete));

    // Remove any transitions that were connected to that state
    transitions.update((current) =>
      current.filter((t) => !t.states.includes(idToDelete))
    );

    // Clear the selection
    selectedStateId.set(null);
  }

  // --- Drag and Drop Handlers ---
  function handleMouseDown(event, id) {
    draggedStateId = id;
    wasDragged = false;

    const stateElement = event.currentTarget;
    const stateRect = stateElement.getBoundingClientRect();
    dragOffsetX = event.clientX - stateRect.left;
    dragOffsetY = event.clientY - stateRect.top;

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp, { once: true });
  }

  function handleMouseMove(event) {
    if (draggedStateId === null) return;
    wasDragged = true; // Flag that a drag has occurred

    const canvas = document.querySelector(".canvas");
    if (!canvas) return;
    const canvasRect = canvas.getBoundingClientRect();

    let newX = event.clientX - canvasRect.left - dragOffsetX;
    let newY = event.clientY - canvasRect.top - dragOffsetY;

    // Constrain the state within the canvas boundaries
    const stateSize = 60;
    newX = Math.max(0, Math.min(newX, canvasRect.width - stateSize));
    newY = Math.max(0, Math.min(newY, canvasRect.height - stateSize));

    states.update((current) =>
      current.map((s) =>
        s.id === draggedStateId ? { ...s, x: newX, y: newY } : s
      )
    );
  }

  function handleMouseUp() {
    // If the mouse was not dragged, treat it as a click
    if (draggedStateId !== null && !wasDragged) {
      handleStateClick(draggedStateId);
    }

    // Clean up drag state
    draggedStateId = null;
    window.removeEventListener("mousemove", handleMouseMove);
  }
</script>

<div class="builder-container">
  <header class="top-bar">
    <button class="action-button" on:click={addState}>Add State</button>
    <button
      class="action-button"
      on:click={toggleGateStatus}
      disabled={!$selectedStateId}>Toggle Gate</button
    >
    <button
      class="action-button"
      on:click={deleteSelectedState}
      disabled={!$selectedStateId}>Delete Selected</button
    >
    <button
      class="action-button green"
      on:click={toggleAddTransitionMode}
      class:active={isAddingTransition}
    >
      {#if isAddingTransition}
        {#if transitionStartId}
          Select Target State...
        {:else}
          Select Start State...
        {/if}
      {:else}
        Add Transition
      {/if}
    </button>
    <button
      class="action-button"
      on:click={deleteSelectedTransition}
      disabled={!$selectedTransitionId}>Delete Selected Transition</button
    >
    <button
      class="action-button"
      aria-pressed={symmetricDeleteEnabled}
      on:click={toggleSymmetricDelete}
      title="When on, deleting a transition also deletes reverse (requires directed model)"
    >
      {symmetricDeleteEnabled
        ? "Symmetric Delete: On"
        : "Symmetric Delete: Off"}
    </button>
  </header>
  <main class="canvas" class:adding-transition={isAddingTransition}>
    <svg class="transition-svg">
      {#each $transitionLines as line (line.id)}
        <line
          x1={line.x1}
          y1={line.y1}
          x2={line.x2}
          y2={line.y2}
          class:selected={$selectedTransitionId === line.id}
          on:click={() => selectTransition(line.id)}
        />
      {/each}
    </svg>

    {#each $states as state (state.id)}
      <div
        class="state"
        class:open={state.gateStatus === "open"}
        class:closed={state.gateStatus === "closed"}
        class:selected={$selectedStateId === state.id && !isAddingTransition}
        class:transition-start={transitionStartId === state.id}
        class:dragging={draggedStateId === state.id}
        style="left: {state.x}px; top: {state.y}px;"
        on:mousedown={(e) => handleMouseDown(e, state.id)}
      >
        {state.id}
      </div>
    {/each}

    {#if $states.length === 0}
      <p class="placeholder-text">Click "Add State" to begin.</p>
    {/if}
  </main>
</div>

<style>
  :global(body, html) {
    margin: 0;
    padding: 0;
    font-family: "Inter", sans-serif;
    background-color: #f0f2f5;
    overflow: hidden;
  }

  .builder-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    height: 100vh;
    background-color: #ffffff;
  }

  .top-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.5rem;
    background-color: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    flex-shrink: 0;
  }

  .action-button {
    padding: 0.625rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    background-color: #f9fafb;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
  }
  .action-button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .action-button:hover:not(:disabled) {
    background-color: #f3f4f6;
  }

  .action-button.green {
    background-color: #dcfce7;
    color: #166534;
    border-color: #bbf7d0;
  }

  .action-button.green:hover:not(:disabled) {
    background-color: #bbf7d0;
  }

  .action-button.green.active {
    background-color: #86efac;
    border-color: #22c55e;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
  }

  .canvas {
    flex-grow: 1;
    margin: 1.5rem;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    background-color: #f8fafc;
    overflow: hidden;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .canvas.adding-transition .state {
    cursor: crosshair;
  }

  .placeholder-text {
    color: #9ca3af;
    font-size: 1.125rem;
  }

  .transition-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: auto;
  }

  .transition-svg line {
    stroke: #9ca3af;
    stroke-width: 3px;
    stroke-linecap: round;
    cursor: pointer;
  }

  .transition-svg line.selected {
    stroke: #f59e0b;
    stroke-width: 4px;
  }

  .state {
    position: absolute;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #374151;
    cursor: grab;
    border: 3px solid;
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 10;
    user-select: none; /* Prevents text selection during drag */
  }

  .state.dragging {
    cursor: grabbing;
    z-index: 20; /* Bring to front */
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  }

  .state.closed {
    border-color: #ef4444;
  }
  .state.open {
    border-color: #22c55e;
  }

  .state.selected {
    box-shadow: 0 0 0 4px #60a5fa;
  }

  .state.transition-start {
    box-shadow: 0 0 0 4px #f472b6;
  }
</style>
