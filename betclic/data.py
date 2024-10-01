import pandas as pd
from typing import Dict, Any

class DataManager:
    """Manages data storage, retrieval, and comparison."""

    def __init__(self):
        self.previous_data = None

    def store_data(self, data = Dict[str, Any]):
        """Stores the fetched data."""
        # Implement data storage logic here (in-memory or persistent)
        # For example, using pandas DataFrame:
        self.previous_data = pd.DataFrame(data)

    def compare_data(self, new_data =  Dict[str, Any]) -> Dict[str, Any]:
        """Compares new data with previous data and returns the changes."""
        # Implement data comparison logic
        # ... (Compare self.previous_data with new_data)
        # Return a dictionary highlighting the changes
        changes = {}  # Your comparison logic here
        return changes
