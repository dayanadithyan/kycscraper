import os
import pytest
from unittest.mock import patch
from config import get_config, get_env_list, get_env_dict

def test_get_config_defaults():
    """Test that default config values are returned when no env vars are set"""
    config = get_config()
    
    assert config["BASE_URL"] == "https://eservices.elections.gov.lk/api/kyc-lga/search?nic="
    assert config["TIMEOUT"] == 15
    assert isinstance(config["USER_AGENTS"], list)
    assert len(config["USER_AGENTS"]) > 0
    assert config["CONNECTION_LIMIT"] == 3
    assert config["CONCURRENCY_LIMIT"] == 2
    assert config["RESPECT_ROBOTS_TXT"] is True

def test_get_env_list():
    """Test parsing comma-separated environment variables into lists"""
    default = ["default1", "default2"]
    
    # Test with no env var
    result = get_env_list("NON_EXISTENT_VAR", default)
    assert result == default
    
    # Test with env var
    with patch.dict(os.environ, {"TEST_LIST": "item1,item2,item3"}):
        result = get_env_list("TEST_LIST", default)
        assert result == ["item1", "item2", "item3"]
    
    # Test with empty env var
    with patch.dict(os.environ, {"TEST_LIST": ""}):
        result = get_env_list("TEST_LIST", default)
        assert result == default

def test_get_env_dict():
    """Test parsing JSON environment variables into dicts"""
    default = {"key": "value"}
    
    # Test with no env var
    result = get_env_dict("NON_EXISTENT_VAR", default)
    assert result == default
    
    # Test with valid JSON
    with patch.dict(os.environ, {"TEST_DICT": '{"key1": "value1", "key2": 2}'}):
        result = get_env_dict("TEST_DICT", default)
        assert result == {"key1": "value1", "key2": 2}
    
    # Test with invalid JSON
    with patch.dict(os.environ, {"TEST_DICT": 'not json'}):
        result = get_env_dict("TEST_DICT", default)
        assert result == default

def test_config_override():
    """Test that environment variables override default config values"""
    with patch.dict(os.environ, {
        "BASE_URL": "https://test-api.example.com/",
        "TIMEOUT": "30",
        "CONNECTION_LIMIT": "5",
        "CONCURRENCY_LIMIT": "10",
        "MIN_DELAY": "0.5",
        "MAX_DELAY": "1.5",
        "RESPECT_ROBOTS_TXT": "false"
    }):
        config = get_config()
        
        assert config["BASE_URL"] == "https://test-api.example.com/"
        assert config["TIMEOUT"] == 30
        assert config["CONNECTION_LIMIT"] == 5
        assert config["CONCURRENCY_LIMIT"] == 10
        assert config["MIN_DELAY"] == 0.5
        assert config["MAX_DELAY"] == 1.5
        assert config["RESPECT_ROBOTS_TXT"] is False