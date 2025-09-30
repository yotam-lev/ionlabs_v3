/**
 * This file exports a mock version of the Tauri `core` API.
 * It's used during local development (pnpm dev) when the real Tauri backend isn't running.
 * This allows the Svelte frontend to be developed in a standard web browser
 * without crashing when it tries to call a backend command.
 */

// This is our fake implementation of the Tauri 'core' API object.
export const core = {
    /**
     * This is a mock of the 'invoke' function. It intercepts calls that would
     * normally go to the Rust backend and returns pre-defined sample data instead.
     * @param command The name of the backend command being called (e.g., 'run_simulation_command').
     * @param payload The data being sent to the command.
     * @returns A Promise that resolves with a JSON string, mimicking a real backend response.
     */
    invoke: async (command: string, payload?: any): Promise<string> => {
      console.log(`[Mock API] Invoked command: "${command}" with payload:`, payload);
  
      // Use a switch statement to handle different backend commands you might have.
      switch (command) {
        case 'run_simulation_command':
          // Simulate a network/processing delay to make the UI feel more realistic.
          await new Promise(resolve => setTimeout(resolve, 800));
  
          // Return a JSON string of successful simulation data.
          // This data should have the same structure as your real backend response.
          return JSON.stringify({
            time_ms: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            total_current_pA: [0, 0, -50, -52, -48, 0, 0, 5, 6, 4, 0],
            voltage_mV: [-80, -80, 40, 40, 40, -80, -80, -80, -80, -80, -80],
          });
  
        // Example of how to simulate an error from the backend:
        /*
        case 'some_other_command':
          await new Promise(resolve => setTimeout(resolve, 500));
          // Rejecting the promise simulates a failure in the backend.
          return Promise.reject({ error: "Simulated backend failure!" });
        */
  
        // If the command is not recognized by the mock, throw an error.
        default:
          throw new Error(`[Mock API] Unhandled command: "${command}"`);
      }
    },
  };
  