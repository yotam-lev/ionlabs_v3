<div class="card">
	<div class="card-header">
		<h3>Parameters</h3>
	</div>
	<div class="table-container">
		<table>
			<tbody>
				<tr>
					<td>Add Noise</td>
					<td><input type="checkbox" /></td>
				</tr>
				<tr>
					<td>Name</td>
					<td><input type="text" placeholder="e.g., Exp_Alpha" /></td>
				</tr>
				<tr>
					<td>NChannels</td>
					<td><input type="number" value="8" /></td>
				</tr>
				<tr>
					<td>SamplesSweep</td>
					<td><input type="number" value="1024" /></td>
				</tr>
				<tr>
					<td>SimulationType</td>
					<td><input type="text" placeholder="e.g., MonteCarlo" /></td>
				</tr>
				<tr>
					<td>Standard Deviation</td>
					<td><input type="number" step="0.01" value="0.5" /></td>
				</tr>
				<tr>
					<td>Sweeps</td>
					<td><input type="number" value="100" /></td>
				</tr>
				<tr>
					<td>Temperature</td>
					<td><input type="number" step="0.1" value="25 .0" /></td>
				</tr>
				<tr>
					<td>TimeSweeps</td>
					<td><input type="number" value="50" /></td>
				</tr>
			</tbody>
		</table>
	</div>
</div>

<style>
	.card {
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
        width: 100%;
        display: flex;
        flex-direction: column;
		border-radius: 8px;
	}
	.card-header {
		padding: 0.75rem 1rem;
		background-color: #e9ecef;
		border-bottom: 1px solid #dee2e6;
        flex-shrink: 0;
	}
	h3 {
		margin: 0;
		font-size: 1.1rem;
	}
	.table-container {
		padding: 1rem;
        flex: 1 1 auto;
        overflow-y: auto;
	}
	table {
		width: 100%;
	}
	td {
		padding: 0.6rem 0;
	}
	td:first-child {
		font-weight: 500;
		white-space: nowrap;
		padding-right: 1rem;
	}
	input {
		width: 100%;
		padding: 0.4rem;
		border: 1px solid #ced4da;
		border-radius: 4px;
		box-sizing: border-box;
	}
	input[type='checkbox'] {
		width: auto;
	}
</style>