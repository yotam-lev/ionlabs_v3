<script lang="ts">
    // We only import the components we want to display. No router needed.
    
    import Navbar from '$lib/components/Navbar.svelte'; 
    import HomePage from './+page.svelte';
    import KineticModePage from './kinetic-model/+page.svelte';
  </script>
  
  <!-- 
    This is now extremely simple.
    We display the Navbar, and right after it, we display the Home component.
  -->
  <Navbar />
  
  <main>
    <slot />
  </main>
  
  <style>
    /* Your styles are perfectly fine and do not need to be changed. */
    :global(body) {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      background-color: #f0f2f5;
    }
  
    main {
      padding: 1.5rem;
    }
  </style>
  