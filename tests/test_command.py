import pytest
from flaskr.db import get_db

def test_create_admin_command(runner, app, monkeypatch):
    """Test create-admin command."""
    class MockPasswordGetter:
        def __init__(self):
            self.prompts = []
            self.inputs = ["testpass", "testpass"]  # Password and confirmation match
        
        def get_password(self, prompt):
            self.prompts.append(prompt)
            return self.inputs.pop(0)
    
    mock = MockPasswordGetter()
    monkeypatch.setattr('flaskr.command.get_password', mock.get_password)
    
    # Execute the command
    result = runner.invoke(args=['create-admin', 'testadmin'])
    assert 'Admin user' in result.output
    assert 'created successfully' in result.output
    
    # Verify admin was created in database
    with app.app_context():
        admin = get_db().execute(
            "SELECT * FROM user WHERE username = 'testadmin'"
        ).fetchone()
        assert admin is not None
        assert admin['role'] == 'admin'

def test_create_admin_password_mismatch(runner, monkeypatch):
    """Test create-admin command with mismatched passwords."""
    class MockPasswordGetter:
        def __init__(self):
            self.inputs = ["testpass", "wrongpass"]  # Password and confirmation don't match
        
        def get_password(self, prompt):
            return self.inputs.pop(0)
    
    mock = MockPasswordGetter()
    monkeypatch.setattr('flaskr.command.get_password', mock.get_password)
    
    # Execute the command
    result = runner.invoke(args=['create-admin', 'testadmin'])
    assert "Passwords don't match" in result.output