import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    """Test user registration."""
    # Test that GET request displays the registration page
    assert client.get('/auth/register').status_code == 200
    
    # Test successful registration
    response = client.post(
        '/auth/register', data={'username': 'new', 'password': 'Password123'}
    )
    assert response.headers["Location"] == "/auth/login"
    
    # Verify user was added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'new'",
        ).fetchone() is not None

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'User test is already registered.'),
    ('new_user', 'short', b'Password must be at least 8 characters long.'),
    ('new_user', 'alllowercase', b'Password must contain at least one uppercase letter.'),
))
def test_register_validate_input(client, username, password, message):
    """Test validation for registration inputs."""
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password},
        follow_redirects=True  # Follow redirects to see flash messages
    )
    assert message in response.data

def test_login(client, auth):
    """Test user login."""
    # Test GET request displays login page
    assert client.get('/auth/login').status_code == 200
    
    # Test successful login
    response = auth.login()
    assert response.headers["Location"] == "/"
    
    # Check if session stores user id
    with client as c:
        c.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """Test validation for login inputs."""
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()
    
    with client:
        auth.logout()
        assert 'user_id' not in session