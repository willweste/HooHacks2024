import time
from app import create_app, db
from sqlalchemy import exc

app = create_app()

def wait_for_db():
    retry = 0
    max_retries = 10
    while retry < max_retries:
        try:
            with app.app_context():
                db.engine.execute('SELECT 1')
            break
        except exc.OperationalError:
            retry += 1
            time.sleep(5)
    else:
        raise RuntimeError('Database connection failed after multiple retries.')

if __name__ == "__main__":
    wait_for_db()
    app.run(host='0.0.0.0', port=5000)