<script> 
    import KineticModelPage from './kinetic-model/+page.svelte';
</script>
  
  <div class="home-container">
      <h1>Welcome to the Ion Channel Modeler</h1>
      <p>Select an option below to get started.</p>
    
      <div class="button-container">
        <button class="primary-button">
            <a href = "/kinetic-model">
                Create new Model
            </a>

        </button>
        <button class="secondary-button">
          Load Existing Model
        </button>
        <button class="secondary-button">
          Load Model From Computer
        </button>
      </div>
    </div>
    
    <style>
      .home-container {
        max-width: 800px;
        margin: 4rem auto;
        padding: 3rem;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e0e0e0;
      }
    
      h1 {
        font-size: 2.5rem;
        color: #333;
        margin-bottom: 0.5rem;
      }
    
      p {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 3rem;
      }
    
      .button-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: center;
      }
    
      button {
        width: 100%;
        max-width: 320px;
        padding: 14px 24px;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        border: 1px solid transparent;
      }
    
      .primary-button {
        color: #fff;
        background-color: #007bff;
        border-color: #007bff;
      }
    
      .primary-button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
      }
    
      .secondary-button {
        color: #333;
        background-color: #f8f9fa;
        border-color: #dee2e6;
      }
    
      .secondary-button:hover {
        background-color: #e2e6ea;
        border-color: #dae0e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }
    </style>
  