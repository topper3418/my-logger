import platform
from app.routes import app

if __name__ == '__main__':
    if platform.system() == 'Windows':
        from waitress import serve
        serve(app, port=5000)
    else:
        import os
        os.system('gunicorn app.routes:app')
