import pytest
from flaskr.db import get_db

def test_index(client, auth):
    """Test the index page."""
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" not in response.data  # No register link in base.html
    
    # When logged in
    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'test body' in response.data
    assert b'href="/1/update"' not in response.data  # Regular user can't edit

def test_index_admin(client, auth):
    """Test admin features on index page."""
    # Login as admin
    auth.login(username='admin', password='test')
    response = client.get('/')
    assert b'Add New Project' in response.data
    assert b'href="/1/update"' in response.data  # Admin can edit

def test_posts_page(client, auth):
    """Test the posts page requires login."""
    response = client.get('/posts')
    # Should show access restricted message
    assert b'Access Restricted' in response.data
    
    # After login
    auth.login()
    response = client.get('/posts')
    assert b'My Projects' in response.data
    assert b'test title' in response.data

def test_create(client, auth, app):
    """Test creating a post (admin only)."""
    # Regular user can't create posts
    auth.login()
    response = client.get('/create')
    assert response.status_code == 403
    
    # Admin can create posts
    auth.logout()
    auth.login(username='admin', password='test')
    assert client.get('/create').status_code == 200
    
    response = client.post(
        '/create',
        data={'title': 'created', 'body': 'test created post', 'youtube_id': 'abc123'}
    )
    assert response.headers["Location"] == "/posts"
    
    # Verify post was added to database
    with app.app_context():
        count = get_db().execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 3  # 2 from data.sql + 1 new

def test_update(client, auth, app):
    """Test updating a post (admin only)."""
    # Regular user can't update
    auth.login()
    response = client.get('/1/update')
    assert response.status_code == 403
    
    # Admin can update
    auth.logout()
    auth.login(username='admin', password='test')
    assert client.get('/1/update').status_code == 200
    
    response = client.post(
        '/1/update',
        data={'title': 'updated', 'body': 'updated body', 'youtube_id': 'xyz789'}
    )
    assert response.headers["Location"] == "/posts"
    
    # Verify post was updated in database
    with app.app_context():
        post = get_db().execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'
        assert post['body'] == 'updated body'
        assert post['youtube_id'] == 'xyz789'

def test_delete(client, auth, app):
    """Test deleting a post (admin only)."""
    # Regular user can't delete
    auth.login()
    response = client.post('/1/delete')
    assert response.status_code == 403
    
    # Admin can delete
    auth.logout()
    auth.login(username='admin', password='test')
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/posts"
    
    # Verify post was deleted from database
    with app.app_context():
        post = get_db().execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None

def test_post_view(client, auth):
    """Test viewing a single post."""
    # Not logged in - should redirect to login
    response = client.get('/1')
    assert response.headers["Location"] == "/auth/login"
    
    # Logged in - should show post
    auth.login()
    response = client.get('/1')
    assert b'test title' in response.data
    assert b'test body' in response.data
    assert b'dQw4w9WgXcQ' in response.data  # YouTube video ID

def test_post_view_not_found(client, auth):
    """Test viewing a non-existent post."""
    auth.login()
    response = client.get('/99')  # Post doesn't exist
    assert response.status_code == 404