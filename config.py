"""
Configuration loader for RAG system.
"""
import yaml
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

_config_cache = None

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yaml.
    Cached after first load.
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}\n"
            f"Please create config.yaml in project root."
        )
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _config_cache = yaml.safe_load(f)
    
    return _config_cache

def get_config(key_path: str, default=None) -> Any:
    """
    Get config value using dot notation.
    
    Examples:
        get_config("retrieval.semantic_top_k")  # Returns 10
        get_config("llm.temperature")  # Returns 0.1
    """
    config = load_config()
    
    keys = key_path.split(".")
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value

def reload_config():
    """
    Force reload configuration from disk.
    Useful for testing or runtime config changes.
    """
    global _config_cache
    _config_cache = None
    return load_config()
