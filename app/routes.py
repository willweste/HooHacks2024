from app import app

@app.route('/')
def home():
    return 'Welcome to Biometric Authentication App'

# Add more routes and views as needed