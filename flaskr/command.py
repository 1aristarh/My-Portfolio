# flaskr/commands.py
import click
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext  # <-- Add this
from flaskr.db import get_db

@click.command('create-admin')  # <-- Simple @click.command, no current_app
@click.argument('username')
@with_appcontext  # <-- This provides the app context when command runsflask
def create_admin(username):
    """Create an admin user."""
    from getpass import getpass
    db = get_db()
    
    password = getpass("Enter password: ")
    confirm = getpass("Confirm password: ")
    
    if password != confirm:
        click.echo("Passwords don't match!")  # Better than print()
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