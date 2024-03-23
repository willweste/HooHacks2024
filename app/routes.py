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
from datetime import datetime
import base64
import os
from PIL import Image
from io import BytesIO

from werkzeug.utils import secure_filename
import os


def setup_routes(app):
    @app.route("/")
    @jwt_required()
    def index():
        current_user = get_jwt_identity()
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            image = request.files['image']
            if image:
                # Read the image in binary format
                image_data = image.read()
            else:
                flash("Image upload failed.", "danger")
                return redirect(url_for("register"))

            # Create a new User instance including the binary image data
            new_user = User(username=username, email=email, password=hashed_password, image_data=image_data)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful. Please login.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                print(f"Error adding user: {e}")
                db.session.rollback()
                flash("An error occurred while registering. Please try again.", "danger")
                return redirect(url_for("register"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            login_method = request.form.get("login_method")

            if login_method == "traditional":
                password = request.form.get("password")
                user = User.query.filter_by(username=username).first()
                if user and bcrypt.check_password_hash(user.password, password):
                    # Create access token and log the user in
                    access_token = create_access_token(identity=username)
                    response = redirect(url_for("index"))
                    set_access_cookies(response, access_token)
                    return response
                else:
                    flash("Invalid username or password.", "danger")

            elif login_method == "facial":
                image_data = request.form.get("image")
                if image_data:
                    image_data = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_data))
                    # Ensure the 'takenUserImages' directory exists
                    image_dir = os.path.join(app.config['UPLOAD_FOLDER'], '..', 'takenUserImages')
                    os.makedirs(image_dir, exist_ok=True)
                    # Save the image with a unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{username}_{timestamp}.png"
                    filepath = os.path.join(image_dir, filename)
                    image.save(filepath)
                    flash("Facial recognition login attempt recorded.", "info")
                    # Implement your facial recognition authentication logic here
                else:
                    flash("No image captured for facial recognition login.", "danger")
            else:
                flash("Invalid login method.", "danger")

        return render_template("login.html")

    @app.route("/logout", methods=["GET"])
    @jwt_required()
    def logout():
        response = redirect(url_for("login"))
        unset_jwt_cookies(response)
        flash("You have been logged out.", "success")
        return response