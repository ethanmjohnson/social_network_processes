import json
import os

def load_config(config_path="config.json"):
    """Loads the configuration file and returns a dictionary."""
    with open(config_path, "r") as f:
        config = json.load(f)

    # Resolve absolute paths
    config["project_root"] = os.path.abspath(config["project_root"])
    return config
