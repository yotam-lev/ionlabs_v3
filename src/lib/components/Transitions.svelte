<script lang="ts">
  // The component takes the coordinates of the start and end points.
  export let x1: number;
  export let y1: number;
  export let x2: number;
  export let y2: number;
  export let isSelected: boolean = false;
  export let onClick: ((event: MouseEvent) => void) | undefined = undefined;

  // A unique ID for the arrowhead marker, to prevent conflicts if you have multiple SVGs.
  const markerId = `arrowhead-${Math.random().toString(36).substring(2, 9)}`;

  // $: reactive statements in Svelte re-run whenever their dependencies change.
  // Here, we recalculate the angle of the line whenever the node coordinates change.
  $: angle = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;

  // This calculates the new endpoint for the line so it stops at the edge of the
  // destination node's circle (radius 35px) instead of its center.
  $: endX = x2 - 40 * Math.cos((angle * Math.PI) / 180);
  $: endY = y2 - 40 * Math.sin((angle * Math.PI) / 180);
</script>

<!-- 
  This is a Svelte <g> element, which is the SVG equivalent of a <div>.
  It groups the line and its arrowhead together.
-->
<g class="transition-group">
  <!-- 
      We define the arrowhead shape here inside <defs>.
      'markerUnits="strokeWidth"' makes the arrow scale with the line thickness.
      'orient="auto"' automatically rotates the arrow to follow the line's direction.
    -->
  <defs>
    <marker
      id={markerId}
      markerWidth="10"
      markerHeight="7"
      refX="8"
      refY="3.5"
      orient="auto"
    >
      <polygon points="0 0, 10 3.5, 0 7" fill="#52525b" />
    </marker>
  </defs>

  <!--
      The main line element.
      - It starts at the center of the first node (x1, y1).
      - It ends at our calculated point on the edge of the second node (endX, endY).
      - 'marker-end' applies our defined arrowhead.
    -->
  <line
    {x1}
    {y1}
    x2={endX}
    y2={endY}
    stroke={isSelected ? "#f59e0b" : "#52525b"}
    stroke-width={isSelected ? "4" : "3"}
    marker-end="url(#{markerId})"
    class:selected={isSelected}
    role="button"
    tabindex="0"
    on:click={onClick}
    on:keydown={(e) => e.key === "Enter" && onClick && onClick(e as any)}
    style="cursor: pointer;"
  />
</g>
