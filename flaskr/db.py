import sqlite3
from datetime import datetime
import click
from flask.cli import with_appcontext
from flask import current_app, g
import os

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

        # Enable foreign key constraints
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Check if tables exist
    tables = db.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name IN ('user', 'post')
    """).fetchall()
    
    # Only initialize if tables don't exist
    if not tables:
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
    else:
        # Add missing columns if tables exist
        try:
            db.execute("ALTER TABLE user ADD COLUMN role TEXT NOT NULL DEFAULT 'read_only'")
            db.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    # Delete existing database file
    db_path = current_app.config['DATABASE']
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    init_db()
    click.echo('Initialized the database.')

def migrate_db():
    """Migrate existing database to new schema."""
    db = get_db()
    updates_applied = False
    
    # Check if youtube_id column exists in post table
    column_check = db.execute("""
        SELECT count(*) as count FROM pragma_table_info('post') 
        WHERE name='youtube_id'
    """).fetchone()
    
    if column_check['count'] == 0:
        # Column doesn't exist, add it
        try:
            db.execute("ALTER TABLE post ADD COLUMN youtube_id TEXT")
            db.commit()
            click.echo('Added youtube_id column to post table.')
            updates_applied = True
        except sqlite3.OperationalError as e:
            click.echo(f'Error adding youtube_id column: {e}')
    else:
        click.echo('YouTube ID column already exists in post table.')
    
    # Add other migrations here...
    
    if updates_applied:
        click.echo('Database migration completed successfully.')
    else:
        click.echo('Database already up to date.')

@click.command('migrate-db')
def migrate_db_command():
    """Migrate existing database to new schema."""
    migrate_db()

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(migrate_db_command)  # Add migration command