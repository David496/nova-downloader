import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

DEFAULT_CONFIG = {
    "theme": "dark",
    "language": "es",
    "download_dir": os.path.expanduser("~/Downloads")
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Ensure all keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG

def save_config(config_dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

config = load_config()
