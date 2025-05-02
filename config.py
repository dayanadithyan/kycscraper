"""Configuration module with environment variable support"""

import os
from typing import Dict, Any, List

# Default configuration
DEFAULT_CONFIG = {
    "USER_AGENTS": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ],
    "HEADERS_TEMPLATE": {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    },
    "BASE_URL": "https://eservices.elections.gov.lk/api/kyc-lga/search?nic=",
    "TIMEOUT": 15,
    "PROXIES": [None],  # Add proxy URLs if needed
    "REQUIRED_KEYS": ["nic", "name", "status"],
    "CONNECTION_LIMIT": 3,
    "CONCURRENCY_LIMIT": 2,
    "MIN_DELAY": 1.5,
    "MAX_DELAY": 3.5,
    "RESPECT_ROBOTS_TXT": True
}

def get_env_list(env_name: str, default: List) -> List:
    """Parse a comma-separated environment variable into a list"""
    env_value = os.getenv(env_name)
    if not env_value:
        return default
    return [item.strip() for item in env_value.split(",")]

def get_env_dict(env_name: str, default: Dict) -> Dict:
    """Parse a JSON string environment variable into a dict"""
    import json
    env_value = os.getenv(env_name)
    if not env_value:
        return default
    try:
        return json.loads(env_value)
    except json.JSONDecodeError:
        return default

def get_config() -> Dict[str, Any]:
    """Get configuration with environment variable overrides"""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    if os.getenv("BASE_URL"):
        config["BASE_URL"] = os.getenv("BASE_URL")
    
    if os.getenv("TIMEOUT"):
        config["TIMEOUT"] = int(os.getenv("TIMEOUT"))
    
    if os.getenv("USER_AGENTS"):
        config["USER_AGENTS"] = get_env_list("USER_AGENTS", config["USER_AGENTS"])
    
    if os.getenv("PROXIES"):
        config["PROXIES"] = get_env_list("PROXIES", config["PROXIES"])
    
    if os.getenv("REQUIRED_KEYS"):
        config["REQUIRED_KEYS"] = get_env_list("REQUIRED_KEYS", config["REQUIRED_KEYS"])
    
    if os.getenv("HEADERS_TEMPLATE"):
        config["HEADERS_TEMPLATE"] = get_env_dict("HEADERS_TEMPLATE", config["HEADERS_TEMPLATE"])
    
    if os.getenv("CONNECTION_LIMIT"):
        config["CONNECTION_LIMIT"] = int(os.getenv("CONNECTION_LIMIT"))
    
    if os.getenv("CONCURRENCY_LIMIT"):
        config["CONCURRENCY_LIMIT"] = int(os.getenv("CONCURRENCY_LIMIT"))
    
    if os.getenv("MIN_DELAY"):
        config["MIN_DELAY"] = float(os.getenv("MIN_DELAY"))
    
    if os.getenv("MAX_DELAY"):
        config["MAX_DELAY"] = float(os.getenv("MAX_DELAY"))
    
    if os.getenv("RESPECT_ROBOTS_TXT"):
        config["RESPECT_ROBOTS_TXT"] = os.getenv("RESPECT_ROBOTS_TXT").lower() in ("true", "1", "yes")
    
    return config