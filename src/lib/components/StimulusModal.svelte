<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	function closeModal() {
		dispatch('close');
	}
</script>

<div class="modal-backdrop" on:click={closeModal}>
	<div class="modal-content" on:click|stopPropagation>
		<div class="modal-header">
			<h2>Stimulus Configuration</h2>
			<button class="close-button" on:click={closeModal}>×</button>
		</div>
		<div class="modal-body">
			<p>Stimulus settings and options will be configured here.</p>
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
		max-width: 500px;
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
</style>