"""
Configuration loader for RAG system.
Loads config.yaml and provides easy access to all settings.
"""
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Singleton config loader"""
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        """Load config.yaml from project root"""
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent / "config.yaml",  # Same dir as config_loader.py
            Path(__file__).parent.parent / "config.yaml",  # Parent dir
            Path.cwd() / "config.yaml",  # Current working directory
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError(
                f"Config file not found. Tried: {[str(p) for p in possible_paths]}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            cls._config = yaml.safe_load(f)
    
    @classmethod
    def get(cls, *keys: str, default: Any = None) -> Any:
        """
        Get config value by dot-separated path.
        
        Examples:
            Config.get('retrieval', 'semantic_top_k')
            Config.get('llm', 'model_name')
        """
        if cls._config is None:
            cls._load_config()
        
        value = cls._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    @classmethod
    def get_all(cls) -> Dict:
        """Get entire config dict"""
        if cls._config is None:
            cls._load_config()
        return cls._config
    
    @classmethod
    def reload(cls):
        """Reload config from disk"""
        cls._load_config()


# Convenience function
def get_config(*keys, default=None):
    """Shortcut for Config.get()"""
    return Config.get(*keys, default=default)
