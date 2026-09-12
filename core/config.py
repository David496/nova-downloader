import json
import os
import sys

def get_storage_path(filename):
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        candidate = os.path.join(exe_dir, filename)
        try:
            test_file = os.path.join(exe_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("1")
            os.remove(test_file)
            return candidate
        except Exception:
            appdata = os.getenv("APPDATA") or os.path.expanduser("~")
            target_dir = os.path.join(appdata, "NovaDownloader")
            os.makedirs(target_dir, exist_ok=True)
            return os.path.join(target_dir, filename)
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root_dir, filename)

CONFIG_PATH = get_storage_path("config.json")

DEFAULT_CONFIG = {
    "theme": "dark",
    "language": "es",
    "download_dir": os.path.expanduser("~/Downloads"),
    "embed_metadata": True,
    "download_subtitles": False,
    "subtitle_lang": "es",
    "embed_subtitles": True
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
                elif k == "download_dir" and (not config[k] or not os.path.exists(config[k])):
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
