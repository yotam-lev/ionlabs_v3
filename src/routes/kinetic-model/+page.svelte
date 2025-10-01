<script lang="ts">
    import BuilderCanvas from "$lib/components/BuilderCanvas.svelte";
    import FunctionPanel from "$lib/components/FunctionPanel.svelte";


        




</script>



<div class = "page-container">
    <h1>
        Kinetic Model Builder
    </h1>

    <div class="main-layout">
        <FunctionPanel />
        <BuilderCanvas />
    </div>
</div>

<style>
    h1 {
        text-align: center;
        margin: 1.5rem;
    }

    .page-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }


    .main-layout {
    display: flex;
    flex-direction: row;
    flex-grow: 1;
    overflow: hidden;
    }
</style>