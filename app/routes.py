import numpy as np
from flask import Response, render_template, request, jsonify, redirect, url_for, flash, current_app
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
from facial_recognition import perform_facial_recognition
import cv2

def generate_frames(username):
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break

        recognized_user = perform_facial_recognition(username, frame)
        if recognized_user:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()
    cv2.destroyAllWindows()

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
                # Save the image in the userImages folder
                image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{username}.jpg")
                image.save(image_path)
            else:
                flash("Image upload failed.", "danger")
                return redirect(url_for("register"))

            # Create a new User instance
            new_user = User(username=username, email=email, password=hashed_password)

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

    @app.route('/facial_login', methods=['POST'])
    def facial_login():
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        camera.release()

        if ret:
            print("Frame captured successfully.")
            recognized_user_id = perform_facial_recognition(frame)
            if recognized_user_id:
                access_token = create_access_token(identity=recognized_user_id)
                response = redirect(url_for("index"))
                set_access_cookies(response, access_token)
                print("User logged in successfully.")
                return response
            else:
                print("Facial recognition failed.")
                flash("Facial recognition failed. Please try again.", "danger")
        else:
            print("Failed to capture frame from the camera.")
            flash("Failed to capture frame from the camera.", "danger")

        return redirect(url_for("login"))
