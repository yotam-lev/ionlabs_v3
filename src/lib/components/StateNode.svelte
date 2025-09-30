<script lang="ts">
  import { onDestroy } from "svelte";

  // Props for the component
  export let label: string = "S1";
  // IMPORTANT: These are now two-way bound from the parent.
  // When the node is dragged, the parent's data updates automatically.
  export let x: number = 0;
  export let y: number = 0;
  export let isSelected: boolean = false;

  let dragging = false;
  let offsetX: number;
  let offsetY: number;

  function onMouseDown(event: MouseEvent) {
    dragging = true;
    // We calculate the offset from the element's top-left corner
    offsetX = event.clientX - x;
    offsetY = event.clientY - y;

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }

  function onMouseMove(event: MouseEvent) {
    if (!dragging) return;
    // By updating these props, Svelte's `bind:` directive
    // automatically informs the parent of the new position.
    x = event.clientX - offsetX;
    y = event.clientY - offsetY;
  }

  function onMouseUp() {
    dragging = false;
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  }

  // Clean up event listeners when the component is destroyed
  onDestroy(() => {
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  });
</script>

<div
  class="state-node"
  class:dragging
  class:selected={isSelected}
  style="left: {x}px; top: {y}px;"
  role="button"
  tabindex="0"
  on:mousedown={onMouseDown}
>
  <div class="label">{label}</div>
</div>

<style>
  .state-node {
    position: absolute;
    width: 45px;
    height:45px;
    background-color: #3b82f6; /* Blue */
    color: white;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: grab;
    user-select: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition:
      transform 0.1s ease-out,
      box-shadow 0.1s ease-out,
      border-color 0.2s;
    border: 3px solid #1e40af; /* Darker blue border */
    z-index: 10; /* Ensure nodes are above transitions */
  }

  .state-node:hover {
    transform: scale(1.05);
  }

  .state-node.selected {
    border-color: #f59e0b; /* A bright orange/amber to indicate selection */
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.5);
  }

  .state-node.dragging {
    cursor: grabbing;
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
    transform: scale(1.1);
    z-index: 1000;
  }

  .label {
    font-family: sans-serif;
    font-weight: bold;
    font-size: 1.2rem;
  }
</style>
