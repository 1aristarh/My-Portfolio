# flaskr/commands.py
import click
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext
from flaskr.db import get_db
import getpass  # Import at module level for patching during testing

def get_password(prompt="Enter password: "):
    """Wrapper function for getpass.getpass to make testing easier"""
    return getpass.getpass(prompt)

@click.command('create-admin')
@click.argument('username')
@with_appcontext
def create_admin(username):
    """Create an admin user."""
    db = get_db()
    
    password = get_password("Enter password: ")
    confirm = get_password("Confirm password: ")
    
    if password != confirm:
        click.echo("Passwords don't match!")
        return
    
    try:
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), "admin"),
        )
        db.commit()
        click.echo(f"Admin user '{username}' created successfully!")
    except db.IntegrityError:
        click.echo(f"Error: User '{username}' already exists!")
    except Exception as e:
        click.echo(f"Error: {str(e)}")