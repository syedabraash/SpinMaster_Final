import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Change this in production

# Configuration
UPLOAD_FOLDER = "uploads"
USER_DB = "users.json"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------
# Helper Functions
# ---------------------------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

# ---------------------------
# Home Page & Match Analysis
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None

    if request.method == "POST":
        video = request.files.get("video")
        if video:
            video_filename = video.filename
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_filename)
            video.save(video_path)

            # Import here to avoid circular imports
            from pose_to_csv import generate_csv_from_video
            from csv_analyzer import analyze_csv

            csv_path = video_path.replace(".mp4", ".csv")
            try:
                generate_csv_from_video(video_path, csv_path)
                feedback = analyze_csv(csv_path)
            except Exception as e:
                feedback = {"error": str(e)}

    return render_template("index.html", feedback=feedback)

# ---------------------------
# Login & Register Page
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_users()
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        action = request.form["action"]

        if action == "Register":
            if username in users:
                message = "Username already exists."
            else:
                users[username] = {
                    "password": generate_password_hash(password)
                }
                save_users(users)
                message = "Registered successfully. Please log in."

        elif action == "Login":
            user = users.get(username)
            if user and check_password_hash(user["password"], password):
                session["user"] = username
                return redirect(url_for("index"))
            else:
                message = "Invalid username or password."

    return render_template("login.html", message=message)

# ---------------------------
# Logout Route
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# ---------------------------
# Leaderboard Page
# ---------------------------
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

# ---------------------------
# Training Modules Page
# ---------------------------
@app.route("/training")
def training():
    return render_template("training.html")

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
