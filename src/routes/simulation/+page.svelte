<script>


	import SidePanel from '$lib/components/side-panel/SidePanel.svelte';
    import SimulationGraphContainer from '$lib/components/SimulationGraphContainer.svelte';
	
</script>

<div class="app-layout">
	<div class="sidebar-container">
		<SidePanel />
	</div>
	<main class="main-content">
		<SimulationGraphContainer />
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial,
			sans-serif;
		background-color: #e9ecef;
	}
	.app-layout {
		display: grid;
		grid-template-columns: 380px 1fr; /* Fixed sidebar, flexible content */
		height: 100vh;
		width: 100vw;
	}
	.sidebar-container {
		grid-column: 1 / 2;
		height: 100vh;
		overflow-y: auto;
	}
	.main-content {
		grid-column: 2 / 3;
		height: 100vh;
		overflow-y: auto;
		background-color: #ffffff;
	}
</style>