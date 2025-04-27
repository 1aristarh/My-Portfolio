from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

def is_admin():
    """Check if current user is admin"""
    # Convert SQLite Row to dict if needed
    user = dict(g.user) if hasattr(g.user, 'keys') else g.user
    return user.get('role') == 'admin'

@bp.route('/')
def index():
    db = get_db()
    user = {'username': 'Guest'}  # Default to guest user
    
    if g.user is not None:
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (g.user['id'],)
        ).fetchone() or user  # Fallback to guest if no user found
    
    # Get the most recent project
    featured_project = db.execute(
        'SELECT p.id, title, body, created, author_id, username, youtube_id'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC LIMIT 1'
    ).fetchone()
    
    from datetime import datetime
    return render_template('blog/index.html', user=user, featured_project=featured_project)


@bp.route('/posts',  methods=('GET', 'POST'))
def posts():
    """Show all posts - now requires login"""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, youtube_id'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/posts.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new portfolio item (admin only)"""
    if not is_admin():
        abort(403, "Only admin can create portfolio items")
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        youtube_id = request.form.get('youtube_id', '')
        print(f"DEBUG - Creating post with Title: '{title}', YouTube ID: '{youtube_id}'")
        
        error = None  # Initialize error variable
        
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, youtube_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], youtube_id)
            )
            db.commit()
            return redirect(url_for('blog.posts'))

    return render_template('blog/create.html')

def get_post(id):
    """Get a post - now requires login"""
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, youtube_id'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post (admin only)"""
    if not is_admin():
        abort(403, "Only admin can update portfolio items")
    
    post = get_post(id)
    print(f"DEBUG - Loaded post for editing - Title: '{post['title']}', YouTube ID: '{post['youtube_id'] if 'youtube_id' in post and post['youtube_id'] else ''}'")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        youtube_id = request.form.get('youtube_id', '')
        print(f"DEBUG - Updating post with Title: '{title}', YouTube ID: '{youtube_id}'")
        
        error = None  # Initialize error variable
        
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, youtube_id = ?'
                ' WHERE id = ?',
                (title, body, youtube_id, id)
            )
            db.commit()
            return redirect(url_for('blog.posts'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post (admin only)"""
    if not is_admin():
        abort(403, "Only admin can delete portfolio items")
    
    get_post(id)  # Verify post exists
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.posts'))

@bp.route('/<int:id>', methods=('GET', 'POST'))
@login_required
def post(id):
    """Show a single post"""
    post = get_post(id)
    return render_template('blog/post.html', post=post)
