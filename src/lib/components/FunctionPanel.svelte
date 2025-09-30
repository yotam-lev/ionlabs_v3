<script>
    import { writable } from 'svelte/store';
  
    // A unique ID counter
    let nextId = 1;
  
    // Store for our functions
    const functions = writable([
      { id: nextId++, name: 'myFunction', formula: 'x * 2' }
    ]);
  
    // Function to add a new empty row
    function addFunction() {
      functions.update(currentFunctions => {
        return [...currentFunctions, { id: nextId++, name: '', formula: '' }];
      });
    }
  
    // Function to delete a row by its ID
    function deleteFunction(idToDelete) {
      functions.update(currentFunctions => 
        currentFunctions.filter(func => func.id !== idToDelete)
      );
    }
  </script>
  
  <div class="function-panel">
    <div class="panel-header">
      <h2>Function Panel</h2>
    </div>
    <div class="table-container">
      <div class="table-header">
        <div class="col index">#</div>
        <div class="col name">Name</div>
        <div class="col formula">f(x)</div>
        <div class="col action"><button class="add-btn" on:click={addFunction}>+ Add Function</button></div>
      </div>
      <div class="table-body">
        {#each $functions as func, i (func.id)}
          <div class="table-row">
            <div class="col index">{i + 1}</div>
            <div class="col name">
              <input type="text" bind:value={func.name} placeholder="e.g., doubleVal" />
            </div>
            <div class="col formula">
              <input type="text" bind:value={func.formula} placeholder="e.g., x * 2" />
            </div>
            <div class="col action">
              <button class="delete-btn" on:click={() => deleteFunction(func.id)}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
    <div class="panel-footer">
    </div>
  </div>
  
  <style>
    .function-panel {
      width: 360px;
      background-color: #ffffff;
      border-right: 1px solid #e5e7eb;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      height: 100vh;
    }
  
    .panel-header {
      padding: 1.25rem;
      border-bottom: 1px solid #e5e7eb;
      flex-shrink: 0;
    }
  
    .panel-header h2 {
      margin: 0;
      font-size: 1.25rem;
      color: #111827;
    }
  
    .table-container {
      flex-grow: 1;
      overflow-y: auto;
    }
  
    .table-header, .table-row {
      display: flex;
      align-items: center;
      padding: 0 1.25rem;
      border-bottom: 1px solid #f3f4f6;
    }
  
    .table-header {
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      color: #6b7280;
      padding-top: 1rem;
      padding-bottom: 1rem;
      background-color: #f9fafb;
    }
  
    .table-row {
      transition: background-color 0.2s ease;
    }
      
    .table-row:hover {
        background-color: #f9fafb;
    }
  
    .col {
      padding: 0.75rem 0.5rem;
    }
    .col.index { flex: 0 0 40px; text-align: center; color: #6b7280; }
    .col.name { flex: 1 1 120px; }
    .col.formula { flex: 1 1 150px; }
    .col.action { flex: 0 0 50px; text-align: right; }
  
    .col input[type="text"] {
      width: 100%;
      padding: 0.5rem;
      border: 1px solid transparent;
      border-radius: 0.375rem;
      background-color: transparent;
      font-size: 0.875rem;
      transition: all 0.2s ease;
    }
  
    .col input[type="text"]:focus {
      outline: none;
      border-color: #a5b4fc;
      background-color: #ffffff;
      box-shadow: 0 0 0 2px #c7d2fe;
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
  
    .panel-footer {
      padding: 1.25rem;
      border-top: 1px solid #e5e7eb;
      flex-shrink: 0;
    }
  
    .add-btn {
      width: 100%;
      padding: 0.75rem;
      font-size: 0.875rem;
      font-weight: 500;
      color: #4f46e5;
      background-color: #eef2ff;
      border: 1px solid transparent;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: all 0.2s ease-in-out;
    }
  
    .add-btn:hover {
      background-color: #e0e7ff;
      color: #4338ca;
    }
  </style>
  
  