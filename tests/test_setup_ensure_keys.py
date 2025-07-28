"""Test the setup route _ensure_keys_exist function."""
import pytest

from app.blueprints.setup.routes import _ensure_keys_exist
from app.models import Settings


@pytest.fixture(autouse=True)
def clear_settings(app):
    """Clear all settings before each test."""
    with app.app_context():
        from app.extensions import db
        Settings.query.delete()
        db.session.commit()
    yield
    with app.app_context():
        Settings.query.delete()
        db.session.commit()


def test_ensure_keys_exist_empty_database(app):
    """Test _ensure_keys_exist with an empty database."""
    with app.app_context():
        # Ensure no settings exist initially
        assert Settings.query.count() == 0
        
        # Call the function
        _ensure_keys_exist()
        
        # Check that all default keys were created
        expected_keys = [
            "server_type",
            "admin_username", 
            "admin_password",
            "server_verified",
            "server_url",
            "api_key",
            "server_name",
            "libraries",
            "overseerr_url",
            "ombi_api_key",
            "discord_id",
            "custom_html",
        ]
        
        assert Settings.query.count() == len(expected_keys)
        
        # Verify all keys exist
        for key in expected_keys:
            setting = Settings.query.filter_by(key=key).first()
            assert setting is not None
            assert setting.key == key
            assert setting.value is None


def test_ensure_keys_exist_with_existing_keys(app):
    """Test _ensure_keys_exist when some keys already exist."""
    with app.app_context():
        # Create some existing settings
        existing_setting = Settings()
        existing_setting.key = "server_type"
        existing_setting.value = "plex"
        
        from app.extensions import db
        db.session.add(existing_setting)
        db.session.commit()
        
        initial_count = Settings.query.count()
        assert initial_count == 1
        
        # Call the function
        _ensure_keys_exist()
        
        # Check that no duplicate was created for existing key
        server_type_settings = Settings.query.filter_by(key="server_type").all()
        assert len(server_type_settings) == 1
        assert server_type_settings[0].value == "plex"  # Value should be preserved
        
        # Check that all other keys were created
        expected_keys = [
            "server_type",
            "admin_username", 
            "admin_password",
            "server_verified",
            "server_url",
            "api_key",
            "server_name",
            "libraries",
            "overseerr_url",
            "ombi_api_key",
            "discord_id",
            "custom_html",
        ]
        
        assert Settings.query.count() == len(expected_keys)


def test_ensure_keys_exist_idempotent(app):
    """Test that _ensure_keys_exist can be called multiple times safely."""
    with app.app_context():
        # Call the function twice
        _ensure_keys_exist()
        _ensure_keys_exist()
        
        # Check that no duplicates were created
        expected_keys = [
            "server_type",
            "admin_username", 
            "admin_password",
            "server_verified",
            "server_url",
            "api_key",
            "server_name",
            "libraries",
            "overseerr_url",
            "ombi_api_key",
            "discord_id",
            "custom_html",
        ]
        
        assert Settings.query.count() == len(expected_keys)
        
        # Verify no duplicate keys exist
        for key in expected_keys:
            settings = Settings.query.filter_by(key=key).all()
            assert len(settings) == 1