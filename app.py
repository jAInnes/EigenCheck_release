from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
import json
import random
import string
import subprocess
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, supports_credentials=True)  
app.secret_key = "supersecretkey"

# Configuration
UPLOAD_FOLDER = "uploads"
USER_DB = "users.json"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = False  
app.config["SESSION_COOKIE_SAMESITE"] = "None"  
app.config["SESSION_COOKIE_SECURE"] = True  

# Ensure necessary directories exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ========================== SERVE FRONTEND ==========================

@app.route("/")
def index():
    """Serve the main frontend page."""
    return render_template("index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files like CSS and JavaScript."""
    return send_from_directory("static", path)


# ========================== USER AUTHENTICATION ==========================

def generate_password(length=8):
    """Generate a random password."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def create_test_users(count=5):
    """Create test users with randomly generated passwords."""
    users = {f"testuser{i}": generate_password() for i in range(1, count + 1)}
    return users


def load_users():
    """Load or initialize the user database."""
    if not os.path.exists(USER_DB):
        print("users.json not found, creating it now...")
        users = {"users": create_test_users(5)}
        with open(USER_DB, "w") as f:
            json.dump(users, f, indent=4)

        print("Test users created:")
        for username, password in users["users"].items():
            print(f"User: {username} | Password: {password}")

        return users["users"]

    try:
        with open(USER_DB, "r") as f:
            users = json.load(f)
            if "users" not in users:
                raise KeyError

        print("Loaded users:")
        for username, password in users["users"].items():
            print(f"User: {username} | Password: {password}")

        return users["users"]

    except (json.JSONDecodeError, KeyError):
        print("users.json was corrupted. Resetting it...")
        users = {"users": {"admin": "password123"}}
        with open(USER_DB, "w") as f:
            json.dump(users, f, indent=4)

        return users["users"]


# Load users at startup
users = load_users()


@app.route("/login", methods=["POST"])
def login():
    """Handle user login."""
    data = request.json
    users = load_users()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "Fehlende Anmeldedaten", "status": "error"}), 400

    if data["username"] in users and users[data["username"]] == data["password"]:
        session["logged_in"] = True
        session["username"] = data["username"]
        session.permanent = True  
        return jsonify({"message": "Login erfolgreich", "status": "success", "username": data["username"]})

    return jsonify({"message": "Falscher Benutzername oder Passwort", "status": "error"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    """Handle user logout."""
    session.clear()
    return jsonify({"message": "Logout erfolgreich", "status": "success"})


@app.route("/status", methods=["GET"])
def check_status():
    """Check if a user is logged in."""
    if "logged_in" in session and session["logged_in"]:
        return jsonify({"logged_in": True, "username": session["username"]})
    return jsonify({"logged_in": False})


# ========================== FILE UPLOAD & RETRIEVAL ==========================

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads (only for logged-in users)."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    if "file" not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    return jsonify({"message": f"Datei {filename} erfolgreich hochgeladen"}), 200


@app.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """Allow logged-in users to download files."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ========================== COMPILATION & EXECUTION ==========================

@app.route("/run", methods=["POST"])
def run_c_program():
    """Compile and execute an uploaded C program."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    if "file" not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    filename = secure_filename(file.filename)
    if not filename.endswith(".c"):
        return jsonify({"error": "Nur C-Dateien erlaubt!"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    executable = filepath.replace(".c", "")
    compile_cmd = ["gcc", filepath, "-o", executable]
    run_cmd = [executable]

    try:
        # Compile the C program
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if compile_result.returncode != 0:
            return jsonify({"error": "Kompilierungsfehler", "details": compile_result.stderr})

        # Run the compiled executable
        run_result = subprocess.run(run_cmd, capture_output=True, text=True)
        return jsonify({"message": "Programm erfolgreich ausgeführt", "output": run_result.stdout})

    except Exception as e:
        return jsonify({"error": str(e)})


# ========================== DEBUGGING & SERVER START ==========================

@app.route("/routes", methods=["GET"])
def list_routes():
    """Return a list of all available routes (for debugging)."""
    output = []
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        output.append(f"{rule.endpoint}: {rule.rule} ({methods})")
    return jsonify({"routes": output})


# Run Flask on Render with dynamic port assignment
port = int(os.environ.get("PORT", 5000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
