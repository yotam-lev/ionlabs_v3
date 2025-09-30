<script lang="ts">
  import { writable } from "svelte/store";
  import { derived } from "svelte/store";
  import ConductanceModal from "./ConductanceModal.svelte";


  // Modal State
  let showConductanceModal = false;

  // --- State Management ---
  interface State {
    id: number;
    x: number;
    y: number;
    gateStatus: "open" | "closed";
  }

  interface Transition {
    id: number;
    from: number;
    to: number;
    rate_equation_id: string;
  }

  interface LinePair {
    pairKey: string;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    mx: number;
    my: number;
    topX: number;
    topY: number;
    bottomX: number;
    bottomY: number;
    forwardId: number | null;
    backwardId: number | null;
    forwardRate: string;
    backwardRate: string;
  }

  const states = writable<State[]>([]);
  const transitions = writable<Transition[]>([]); // [{ id, from, to, rate_equation_id }]
  const selectedStateId = writable<number | null>(null);
  const selectedTransitionId = writable<number | null>(null);

  let nextStateId: number = 1;
  let nextTransitionId: number = 1;

  // --- Interaction Modes ---
  let isAddingTransition: boolean = false;
  let transitionStartId: number | null = null;
  let symmetricDeleteEnabled: boolean = true; // UI toggle; with undirected links it's effectively normal delete

  // --- Dragging State ---
  let draggedStateId: number | null = null;
  let wasDragged: boolean = false;
  let dragOffsetX: number = 0;
  let dragOffsetY: number = 0;

  // --- Derived Store for Rendering Lines ---
  const transitionLines = derived<
    [typeof states, typeof transitions],
    LinePair[]
  >([states, transitions], ([$states, $transitions]) => {
    const stateMap = new Map($states.map((s) => [s.id, s]));
    const stateSize = 60; // from CSS
    const pairMap: Map<
      string,
      { forward: Transition | null; backward: Transition | null }
    > = new Map();
    for (const t of $transitions) {
      const key = `${Math.min(t.from, t.to)}-${Math.max(t.from, t.to)}`;
      const rec = pairMap.get(key) ?? { forward: null, backward: null };
      if (t.from <= t.to) rec.forward = t;
      else rec.backward = t;
      pairMap.set(key, rec);
    }
    const pairs: LinePair[] = [];
    for (const [pairKey, { forward, backward }] of pairMap.entries()) {
      const a = forward ?? backward!;
      const fromState = stateMap.get(Math.min(a.from, a.to));
      const toState = stateMap.get(Math.max(a.from, a.to));
      if (!fromState || !toState) continue;
      const x1 = fromState.x + stateSize / 2;
      const y1 = fromState.y + stateSize / 2;
      const x2 = toState.x + stateSize / 2;
      const y2 = toState.y + stateSize / 2;
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2;
      const dx = x2 - x1;
      const dy = y2 - y1;
      const len = Math.max(1, Math.hypot(dx, dy));
      const nx = -dy / len;
      const ny = dx / len;
      const offset = 14;
      const topX = mx + nx * offset;
      const topY = my + ny * offset;
      const bottomX = mx - nx * offset;
      const bottomY = my - ny * offset;
      pairs.push({
        pairKey,
        x1,
        y1,
        x2,
        y2,
        mx,
        my,
        topX,
        topY,
        bottomX,
        bottomY,
        forwardId: forward ? forward.id : null,
        backwardId: backward ? backward.id : null,
        forwardRate: forward?.rate_equation_id ?? "",
        backwardRate: backward?.rate_equation_id ?? "",
      });
    }
    return pairs;
  });

  // --- Functions ---
  function addState() {
    const newState = {
      id: nextStateId++,
      x: 100 + ((nextStateId - 1) % 10) * 20,
      y: 100 + ((nextStateId - 1) % 10) * 20,
      gateStatus: "closed" as const,
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
  function handleStateClick(clickedId: number) {
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
        const from = transitionStartId;
        const to = clickedId;
        transitions.update((current) => {
          const existsForward = current.some(
            (t) => t.from === from && t.to === to
          );
          const existsBackward = current.some(
            (t) => t.from === to && t.to === from
          );
          const additions = [];
          if (!existsForward)
            additions.push({
              id: nextTransitionId++,
              from,
              to,
              rate_equation_id: "",
            });
          if (!existsBackward)
            additions.push({
              id: nextTransitionId++,
              from: to,
              to: from,
              rate_equation_id: "",
            });
          return additions.length ? [...current, ...additions] : current;
        });
      }
      // Reset and exit transition mode after the second click
      isAddingTransition = false;
      transitionStartId = null;
    }
  }

  function selectTransition(id: number) {
    selectedTransitionId.set(id);
    selectedStateId.set(null);
  }

  function deleteSelectedTransition() {
    if (!$selectedTransitionId) return;
    const idToDelete = $selectedTransitionId;
    transitions.update((current) => {
      const target = current.find((t) => t.id === idToDelete);
      if (!target) return current;
      const partner = current.find(
        (t) => t.from === target.to && t.to === target.from
      );
      const partnerId = partner ? partner.id : null;
      return current.filter((t) => t.id !== idToDelete && t.id !== partnerId);
    });
    selectedTransitionId.set(null);
  }

  function updateTransitionRate(id: number, value: string) {
    transitions.update((current) =>
      current.map((t) => (t.id === id ? { ...t, rate_equation_id: value } : t))
    );
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
      current.filter((t) => t.from !== idToDelete && t.to !== idToDelete)
    );

    // Clear the selection
    selectedStateId.set(null);
  }

  // --- Drag and Drop Handlers ---
  function handleMouseDown(event: MouseEvent, id: number) {
    draggedStateId = id;
    wasDragged = false;

    const stateElement = event.currentTarget as HTMLElement | null;
    if (!stateElement) return;
    const stateRect = stateElement.getBoundingClientRect();
    dragOffsetX = event.clientX - stateRect.left;
    dragOffsetY = event.clientY - stateRect.top;

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp, { once: true });
  }

  function handleMouseMove(event: MouseEvent) {
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

    <button class= "action-button" aria-pressed={showConductanceModal}
    on:click={() => (showConductanceModal = true)}
    title="When on coductance modal is showing ">
    Conductance
    </button>



  </header>
  <main class="canvas" class:adding-transition={isAddingTransition}>
    <svg class="transition-svg">
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="8"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af" />
        </marker>
      </defs>
      {#each $transitionLines as line (line.pairKey)}
        <g>
          <line
            x1={line.x1}
            y1={line.y1}
            x2={line.x2}
            y2={line.y2}
            marker-start="url(#arrowhead)"
            marker-end="url(#arrowhead)"
            class:selected={$selectedTransitionId === line.forwardId ||
              $selectedTransitionId === line.backwardId}
            role="button"
            tabindex="0"
            on:click={() =>
              line.forwardId !== null
                ? selectTransition(line.forwardId)
                : line.backwardId !== null && selectTransition(line.backwardId)}
            on:keydown={(e) =>
              e.key === "Enter" &&
              (line.forwardId !== null
                ? selectTransition(line.forwardId)
                : line.backwardId !== null &&
                  selectTransition(line.backwardId))}
          />
          {#if line.forwardId !== null}
            <foreignObject
              x={line.topX - 30}
              y={line.topY - 14}
              width="60"
              height="28"
              style="overflow:visible;"
            >
              <div
                xmlns="http://www.w3.org/1999/xhtml"
                style="display:flex; align-items:center; justify-content:center;"
              >
                <input
                  type="text"
                  placeholder="***"
                  value={line.forwardRate}
                  on:click={(e) => e.stopPropagation()}
                  on:input={(e) =>
                    updateTransitionRate(
                      line.forwardId!,
                      (e.currentTarget as HTMLInputElement).value
                    )}
                  style="width: 56px; height: 22px; font-size: 12px; text-align: center; border: 1px solid #d1d5db; border-radius: 4px; background: #ffffffcc;"
                />
              </div>
            </foreignObject>
          {/if}
          {#if line.backwardId !== null}
            <foreignObject
              x={line.bottomX - 30}
              y={line.bottomY - 14}
              width="60"
              height="28"
              style="overflow:visible;"
            >
              <div
                xmlns="http://www.w3.org/1999/xhtml"
                style="display:flex; align-items:center; justify-content:center;"
              >
                <input
                  type="text"
                  placeholder="***"
                  value={line.backwardRate}
                  on:click={(e) => e.stopPropagation()}
                  on:input={(e) =>
                    updateTransitionRate(
                      line.backwardId!,
                      (e.currentTarget as HTMLInputElement).value
                    )}
                  style="width: 56px; height: 22px; font-size: 12px; text-align: center; border: 1px solid #d1d5db; border-radius: 4px; background: #ffffffcc;"
                />
              </div>
            </foreignObject>
          {/if}
        </g>
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
        role="button"
        tabindex="0"
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

<ConductanceModal 
    showModal = {showConductanceModal}
    on:close={() => (showConductanceModal = false)}
/>

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
