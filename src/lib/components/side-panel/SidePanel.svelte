<script>
	import ExperimentTable from './ExperimentTable.svelte';
	import ParametersTable from './ParametersTable.svelte';
	import ErrorConsole from './ErrorConsole.svelte';
	import StimulusModal from '../StimulusModal.svelte';

	let showModal = false;
</script>

<aside class="side-panel">
	<div class="panel-section">
		<ExperimentTable />
	</div>

	<div class="stimulus-section">
		<button class="stimulus-button" on:click={() => (showModal = true)}>Stimulus</button>
	</div>

	<div class="panel-section">
		<ParametersTable />
	</div>

	<div class="panel-section">
		<ErrorConsole />
	</div>
</aside>

{#if showModal}
	<StimulusModal on:close={() => (showModal = false)} />
{/if}

<style>
	.side-panel {
		padding: 1rem;
		background-color: #fff;
		height: 100%;
		border-right: 1px solid #dee2e6;
		/* MODIFIED: Use Flexbox for layout */
		display: flex;
		flex-direction: column;
		gap: 1.5rem; /* Adds space between the sections */
	}

	/* ADDED: New style for the growing sections */
	.panel-section {
		flex: 1 1 0; /* Allows the section to grow and shrink equally */
		min-height: 0; /* Crucial: allows the flex item to shrink smaller than its content */
		display: flex; /* Makes this a flex container so child component can fill it */
	}

	.stimulus-section {
		/* MODIFIED: The button section should not grow */
		flex-shrink: 0;
		text-align: center;
	}

	.stimulus-button {
		width: 100%;
		padding: 0.75rem;
		font-size: 1.1rem;
		font-weight: bold;
		color: #fff;
		background-color: #28a745;
		border: none;
		border-radius: 8px;
		cursor: pointer;
	}
	.stimulus-button:hover {
		background-color: #218838;
	}
</style>