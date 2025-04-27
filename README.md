# My Portfolio App

A Flask-based portfolio web application with user authentication and project management.

## Features

- User authentication (login, register, logout)
- Admin role with special permissions
- Portfolio project management (create, view, update, delete)
- YouTube video integration
- Responsive modern design

## Setup

1. Clone the repository:
   ```
   git clone <your-github-repo-url>
   cd <repository-name>
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Set environment variables:
   - Copy `.env.example` to `.env`
   - Modify `.env` with your settings
   - Load environment variables:
     ```
     # On Windows
     set FLASK_SECRET_KEY=your-secure-secret-key
     
     # On macOS/Linux
     export FLASK_SECRET_KEY=your-secure-secret-key
     ```
   - For production, set a strong, randomly generated secret key

4. Initialize the database:
   ```
   flask --app flaskr init-db
   ```

5. Create an admin user:
   ```
   flask --app flaskr create-admin <username>
   ```

6. Run the application:
   ```
   flask --app flaskr run --debug
   ```

7. Visit http://127.0.0.1:5000 in your browser

## Project Structure

- `flaskr/` - The main application package
  - `static/` - CSS and other static files
  - `templates/` - HTML templates
  - `__init__.py` - Application factory
  - `auth.py` - Authentication routes
  - `blog.py` - Portfolio routes
  - `db.py` - Database functions
  - `schema.sql` - Database schema

## Security Notes

- Always use a strong, unique secret key in production
- Never commit your `.env` file or secret keys to version control
- In production, set environment variables through your hosting platform

## License

This project is licensed under the MIT License - see the LICENSE file for details.
