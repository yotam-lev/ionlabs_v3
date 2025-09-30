<script lang="ts">
    // The <Link> component from the router has been removed to avoid errors.
    // We now use standard HTML <a> tags.
  </script>
  
  <nav>
    <div class="nav-container">
      <!-- This is now a standard link. -->
      <a href="/" class="brand">IonModeler</a>
      <div class="nav-links">
        <!-- This is also a standard link. -->
        <a href="/kinetic-model">Kinetic Model</a>
        <a href="/simulation">Simulation</a>
        <a href="/">Home</a>
      </div>
    </div>
  </nav>
  
  <style>
    nav {
      background-color: #ffffff;
      padding: 0 2rem;
      border-bottom: 1px solid #e0e0e0;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
  
    .nav-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto;
      height: 60px;
    }
    
    .brand {
      font-weight: bold;
      font-size: 1.25rem;
      text-decoration: none;
      color: #333;
    }
  
    .nav-links a {
      text-decoration: none;
      color: #555;
      margin-left: 1.5rem;
      transition: color 0.2s;
    }
  
    .nav-links a:hover {
      color: #007bff;
    }
  </style>
  