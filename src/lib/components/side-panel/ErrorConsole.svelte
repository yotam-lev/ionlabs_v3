<div class="error-console">
	<h4>Error Console</h4>
	<div class="console-output">
		<pre><code>No errors to display.</code></pre>
	</div>
</div>

<style>
	.error-console {
		border: 1px solid #dee2e6;
		border-radius: 8px;
		background-color: #212529;
		color: #f8f9fa;
		font-family: monospace;
		/* MODIFIED: Make the component fill its parent and arrange its children */
		width: 100%;
		display: flex;
		flex-direction: column;
	}
	h4 {
		margin: 0;
		padding: 0.75rem 1rem;
		background-color: #343a40;
		border-bottom: 1px solid #495057;
		font-size: 1rem;
		border-top-left-radius: 7px;
		border-top-right-radius: 7px;
		/* MODIFIED: Prevent header from shrinking */
		flex-shrink: 0;
	}
	.console-output {
		padding: 1rem;
		min-height: 100px;
		white-space: pre-wrap;
		word-wrap: break-word;
		/* MODIFIED: Allow this container to grow and scroll if content overflows */
		flex: 1 1 auto;
		overflow-y: auto;
	}
	code {
		color: #adb5bd;
	}
</style>