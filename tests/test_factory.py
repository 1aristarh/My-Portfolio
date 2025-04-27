from flaskr import create_app

def test_config():
    """Test that testing config works."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    """Test hello route works."""
    response = client.get('/hello')
    assert response.data == b'Hello, World!'