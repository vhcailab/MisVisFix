import json
import os
from django.conf import settings

# Define the path to the JSON file inside the app
PITFALLS_FILE = os.path.join(settings.BASE_DIR, "data", "pitfalls.json")

class PitfallManager:
    def __init__(self):
        self.pitfalls = self.load_pitfalls()

    def load_pitfalls(self):
        """Load pitfalls from a JSON file or return an empty dictionary if not found."""
        if os.path.exists(PITFALLS_FILE):
            with open(PITFALLS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_pitfalls(self):
        """Save the current pitfalls to the JSON file."""
        with open(PITFALLS_FILE, "w", encoding="utf-8") as file:
            json.dump(self.pitfalls, file, indent=4)

    def get_pitfalls(self):
        """Return the dictionary of pitfalls."""
        return self.pitfalls

    def add_pitfall(self, new_pitfall):
        """Dynamically add or update a pitfall."""
        if not isinstance(new_pitfall, dict) or len(new_pitfall) != 1:
            return "Invalid input format. Expected a dictionary with one key-value pair."

        key, value = list(new_pitfall.items())[0]  # Extract key and value

        if key in self.pitfalls:
            # Update the description while keeping the existing label
            self.pitfalls[key]["description"] = value["description"]
            action = "updated"
        else:
            # Add new pitfall
            self.pitfalls[key] = value
            action = "added"

        self.save_pitfalls()
        return f"Pitfall '{key}' {action} successfully."

    def remove_pitfall(self, key):
        """Remove an existing pitfall."""
        if key not in self.pitfalls:
            return f"Pitfall '{key}' does not exist."

        del self.pitfalls[key]
        self.save_pitfalls()
        return f"Pitfall '{key}' removed successfully."