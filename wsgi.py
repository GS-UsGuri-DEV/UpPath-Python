"""
wsgi.py

Entry point para servidores WSGI (Gunicorn, uWSGI, etc).
"""

from src.api.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
