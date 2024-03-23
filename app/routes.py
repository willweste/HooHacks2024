from flask import Response, render_template, request, jsonify, redirect, url_for, flash
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    get_jwt_identity,
)

def setup_routes(app):
    @app.route("/")
    @jwt_required()
    def index():
        current_user = get_jwt_identity()
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            # Extract data from the form
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

            # Create a new User instance with the form data and hashed password
            new_user = User(username=username, email=email, password=hashed_password)

            # Try to add the new user to the session and commit it to the database
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful. Please login.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                print(f"Error adding user: {e}")
                flash("An error occurred while registering. Please try again.", "danger")
                return redirect(url_for("register"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            # Extract username and password from the form
            username = request.form.get("username")
            password = request.form.get("password")

            # Check if the user exists in the database by username
            user = User.query.filter_by(username=username).first()

            # If the user exists and the password is correct
            if user and bcrypt.check_password_hash(user.password, password):
                # Create access token
                access_token = create_access_token(identity=user.id)
                # Create redirect response to index page
                response = redirect(url_for("index"))
                # Set access cookies on the redirect response
                set_access_cookies(response, access_token)
                # Return the redirect response with the cookies set
                return response
            else:
                flash("Invalid username or password. Please try again.", "danger")
                return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/logout", methods=["GET"])
    @jwt_required()
    def logout():
        response = redirect(url_for("login"))
        unset_jwt_cookies(response)
        flash("You have been logged out.", "success")
        return response