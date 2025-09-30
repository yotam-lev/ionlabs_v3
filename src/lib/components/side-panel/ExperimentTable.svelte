<script lang="ts">
	import { writable } from 'svelte/store';

	// A unique ID counter, starting after the initial data
	let nextId = 7;

	// Initial data for the experiments
	const initialExperiments = [
		{ id: 1, name: 'Baseline Study' },
		{ id: 2, name: 'Voltage Step Test' },
		{ id: 3, name: 'Frequency Response' },
		{ id: 4, name: 'Thermal Drift Analysis' },
		{ id: 5, name: 'Long-term Stability' },
		{ id: 6, name: 'Noise Floor Test' }
	];

	// Create a writable store to hold the experiments
	const experiments = writable(initialExperiments);

	// Function to add a new experiment
	function addExperiment() {
		const newExperiment = { id: nextId++, name: 'New Experiment' };
		experiments.update((current) => [...current, newExperiment]);
	}

	// Function to delete an experiment by its ID
	function deleteExperiment(idToDelete: number) {
		experiments.update((current) => current.filter((exp) => exp.id !== idToDelete));
	}
</script>

<div class="card">
	<div class="card-header">
		<h3>Experiments</h3>
		<button class="add-button" on:click={addExperiment}>+ Add New</button>
	</div>
	<div class="table-container">
		<table>
			<thead>
				<tr>
					<th>No.</th>
					<th>Name</th>
					<th class="action-col" />
				</tr>
			</thead>
			<tbody>
				{#each $experiments as exp, i (exp.id)}
					<tr>
						<td>{i + 1}</td>
						<td>{exp.name}</td>
						<td class="action-col">
							<button
								class="delete-btn"
								aria-label={`Delete ${exp.name}`}
								on:click={() => deleteExperiment(exp.id)}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="16"
									height="16"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
									><polyline points="3 6 5 6 21 6" /><path
										d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
									/><line x1="10" y1="11" x2="10" y2="17" /><line
										x1="14"
										y1="11"
										x2="14"
										y2="17"
									/></svg
								>
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.card {
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		width: 100%;
		/* MODIFIED: The card is now a flex container to manage its children's height */
		display: flex;
		flex-direction: column;
		/* Set a max-height for the whole card if needed, e.g., 300px */
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background-color: #e9ecef;
		border-bottom: 1px solid #dee2e6;
		/* Ensures header does not shrink */
		flex-shrink: 0;
	}
	h3 {
		margin: 0;
		font-size: 1.1rem;
	}
	.add-button {
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 5px;
		padding: 0.4rem 0.8rem;
		cursor: pointer;
		font-weight: bold;
	}
	.add-button:hover {
		background-color: #0056b3;
	}
	.table-container {
		padding: 0 0.5rem;
		/* MODIFIED: Set a max-height to show ~3-4 rows and enable scrolling */
		max-height: 180px;
		overflow-y: auto;
	}
	table {
		width: 100%;
		border-collapse: collapse;
	}
	th,
	td {
		text-align: left;
		padding: 0.75rem 0.5rem; /* Increased padding slightly for better spacing */
		border-bottom: 1px solid #dee2e6;
	}
	th {
		font-weight: 600;
	}
	tbody tr:last-child td {
		border-bottom: none;
	}

	/* ADDED: Styles for the new delete button and its column */
	.action-col {
		width: 50px;
		text-align: right;
	}
	.delete-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #9ca3af;
		transition: all 0.2s ease;
	}
	.delete-btn:hover {
		background-color: #fee2e2;
		color: #ef4444;
	}
</style>