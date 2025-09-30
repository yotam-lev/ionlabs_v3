import sys
import os
import json
import numpy as np

# Add the script's own directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemas import ChannelModelSchema, StimulusProtocolSchema
from simulation import SimulationEngine

# Helper class to convert numpy arrays in the result to lists
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def run_simulation():
    try:
        # Read the model and protocol JSON from standard input
        input_data = json.load(sys.stdin)
        
        # Validate the data using your Pydantic schemas
        model = ChannelModelSchema(**input_data['model'])
        protocol = StimulusProtocolSchema(**input_data['protocol'])
        
        # Initialize and run the engine
        engine = SimulationEngine(model, protocol)
        results = engine.run(duration_ms=input_data['duration_ms'], steps=input_data['steps'])
        
        # Print the final results dictionary as a JSON string to stdout
        # Use the custom encoder to handle numpy arrays
        print(json.dumps(results, cls=NumpyEncoder))

    except Exception as e:
        # If anything goes wrong, print the error to stderr and exit
        print(f"Python Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    run_simulation()