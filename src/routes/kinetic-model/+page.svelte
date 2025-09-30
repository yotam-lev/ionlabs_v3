<script lang="ts">
    import BuilderCanvas from "$lib/components/BuilderCanvas.svelte";
    import FunctionPanel from "$lib/components/FunctionPanel.svelte";
    import { invoke } from '@tauri-apps/api/tauri';
    import { kineticModelStore } from "$lib/modelStore";
    import { get } from 'svelte/store';



    let feedbackMessage: string= ' ';
    let isSaving: boolean = false;

    async function handleSave() {
        isSaving = true;
        feedbackMessage = ' ';
    }




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