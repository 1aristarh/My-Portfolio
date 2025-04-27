import sqlite3
import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    """Test database connection is created and closed properly."""
    with app.app_context():
        db = get_db()
        assert db is get_db()  # Should return the same connection

    # Verify connection is closed after context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    """Test the init-db command."""
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    # Mock os.path.exists and os.unlink to prevent file access errors
    def fake_exists(path):
        return False  # Pretend file doesn't exist
    
    def fake_unlink(path):
        pass  # Do nothing instead of deleting file

    # Replace the actual functions with our test functions
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    monkeypatch.setattr('os.path.exists', fake_exists)
    monkeypatch.setattr('os.unlink', fake_unlink)
    
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called