from flask import Flask, request, jsonify, send_from_directory, session, render_template
import os
import json
import random
import string
import subprocess
from werkzeug.utils import secure_filename
from flask_cors import CORS
import shutil  
import glob

def load_config():
    """Lädt Konfiguration aus `properties.txt`."""
    config = {}
    if os.path.exists("properties.txt"):
        with open("properties.txt", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):  # Kommentare & leere Zeilen ignorieren
                    key, value = line.strip().split("=")
                    config[key.strip()] = value.strip()
    return config

# ✅ Lese Konfiguration aus `properties.txt`
config = load_config()

# ✅ Setze globale Variablen mit Standardwerten, falls nicht in `properties.txt`
COMPILATION_FOLDER = config.get("COMPILATION_FOLDER", "compilation")
UPLOAD_FOLDER = config.get("UPLOAD_FOLDER", "uploads")
USER_DB = config.get("USER_DB", "users.json")
INPUT_FILE = config.get("INPUT_FILE", "aufgabe2.dat")
EXPECTED_FILE = config.get("EXPECTED_FILE", "expected.txt")
USE_STATIC_LIB = config.get("USE_STATIC_LIB", "false").lower() == "true"
LIB_FOLDER = config.get("LIB_FOLDER", "lib")

# ✅ Stelle sicher, dass die Verzeichnisse existieren
os.makedirs(COMPILATION_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def compile_lib_folder():
    """Kompiliert die Bibliothek aus dem konfigurierten lib-Verzeichnis."""
    lib_path = config.get("LIB_FOLDER", "lib")
    make_result = subprocess.run(["make", "-C", lib_path], capture_output=True, text=True)
    if make_result.returncode == 0:
        print("✅ Bibliothek erfolgreich kompiliert.")
    else:
        print("❌ Fehler beim Kompilieren der Bibliothek:", make_result.stderr)


# Beim Start:
compile_lib_folder()


def compile_global_files():
    if not os.path.exists(COMPILATION_FOLDER):
        os.makedirs(COMPILATION_FOLDER)

    try:
        make_command = ["make", "-C", COMPILATION_FOLDER]
        make_result = subprocess.run(make_command, capture_output=True, text=True)

        if make_result.returncode != 0:
            print("❌ Fehler beim globalen Kompilieren:", make_result.stderr)
        else:
            print("✅ Globale Dateien erfolgreich kompiliert.")
    except Exception as e:
        print(f"❌ Fehler beim globalen Kompilieren: {str(e)}")

compile_global_files()


# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="templates/static")

CORS(app, supports_credentials=True)  
app.secret_key = "supersecretkey"

# Configuration

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = False  
app.config["SESSION_COOKIE_SAMESITE"] = "None"  
app.config["SESSION_COOKIE_SECURE"] = True  

# Ensure necessary directories exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


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
        users["users"]["admin"] = "adminpassword"  # Add admin user
        with open(USER_DB, "w") as f:
            json.dump(users, f, indent=4)

        # ✅ Print test users and their passwords
        print("Test users created:")
        for username, password in users["users"].items():
            print(f"User: {username} | Password: {password}")

        return users["users"]

    try:
        with open(USER_DB, "r") as f:
            users = json.load(f)
            if "users" not in users:
                raise KeyError

        # Ensure admin user is present
        if "admin" not in users["users"]:
            users["users"]["admin"] = "adminpassword"
            with open(USER_DB, "w") as f:
                json.dump(users, f, indent=4)

        # ✅ Print loaded users and passwords
        print("Loaded users:")
        for username, password in users["users"].items():
            print(f"User: {username} | Password: {password}")

        return users["users"]

    except (json.JSONDecodeError, KeyError):
        print("users.json was corrupted. Resetting it...")
        users = {"users": {"admin": "adminpassword"}}
        with open(USER_DB, "w") as f:
            json.dump(users, f, indent=4)

        return users["users"]
    
def check_user_files(users):
    """Check if users have uploaded files."""
    user_files = {}
    for username in users:
        if username != "admin":
            file_path = f"uploads/{username}/*.c"
            files = glob.glob(file_path)
            file_exists = len(files) > 0
            print(f"Checking path: {file_path}, Exists: {file_exists}")  # Debugging output
            user_files[username] = file_exists
    return user_files
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
        if data["username"] == "admin":
            user_files = check_user_files(users)
            return jsonify({"message": "Admin Login erfolgreich", "status": "success", "username": data["username"], "users": users, "user_files": user_files})
        return jsonify({"message": "Login erfolgreich", "status": "success", "username": data["username"]})

    return jsonify({"message": "Falscher Benutzername oder Passwort", "status": "error"}), 401
@app.route("/users", methods=["GET"])
def get_users():
    """Get the list of users."""
    users = load_users()
    return jsonify({"users": users})


# ========================== FILE UPLOAD & RETRIEVAL ==========================



@app.route("/upload", methods=["POST"])
def upload_file():
    """Ersetzt vorherige Dateien und speichert den neuesten Upload als `user_code.c`."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    username = session.get("username")
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], username)
    
    # ✅ Lösche alte Dateien vor jedem Upload
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    os.makedirs(user_folder, exist_ok=True)

    if "file" not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    # ✅ Speichere alle `.c`-Dateien, aber benenne sie in `user_code.c` um
    filename = secure_filename(file.filename)
    if not filename.endswith(".c"):
        return jsonify({"error": "Nur C-Dateien erlaubt!"}), 400

    filepath = os.path.join(user_folder, "user_code.c")
    file.save(filepath)

    return jsonify({"message": f"Datei erfolgreich hochgeladen und gespeichert als `user_code.c`", "path": filepath}), 200






@app.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """Allow logged-in users to download files."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ========================== COMPILATION & EXECUTION ==========================
@app.route("/run", methods=["POST"])
def run_c_program():
    """Kompiliert `user_code.c` des Users und führt `main.out` mit diesem aus."""
    if "logged_in" not in session or not session["logged_in"]:
        return jsonify({"error": "Nicht eingeloggt"}), 401

    username = session.get("username")
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    
    user_file = os.path.join(user_folder, "user_code.c")
    user_object = os.path.join(user_folder, "user_code.o")
    user_executable = os.path.join(user_folder, "main_user.out")

    if not os.path.exists(user_file):
        return jsonify({"error": "Es wurde keine C-Datei hochgeladen!"}), 400

    try:
        # ✅ Kompiliere user_code.c
        lib_path = config.get("LIB_FOLDER", "lib")  # Das kann z. B. lib sein
        compile_cmd = ["gcc", "-I" + lib_path, "-c", "-fPIC", user_file, "-o", user_object]

        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)

        if compile_result.returncode != 0:
            return jsonify({
                "error": "Fehler beim Kompilieren von user_code.c",
                "details": compile_result.stderr
            })

        # ✅ Kompiliere main.c aus der Aufgaben-Config
        main_object = os.path.join(user_folder, "main.o")
        main_c_path = os.path.join(COMPILATION_FOLDER, "main.c")
        compile_main = [
             "gcc", "-I" + lib_path, "-c", "-fPIC",
             os.path.join(COMPILATION_FOLDER, "main.c"),
             "-o", main_object
]

        main_result = subprocess.run(compile_main, capture_output=True, text=True)

        if main_result.returncode != 0:
            return jsonify({
                "error": "Fehler beim Kompilieren von main.c",
                "details": main_result.stderr
            })

        # ✅ Verlinke mit libmatrix.a (aus lib_path)
        lib_path = config.get("LIB_FOLDER", "lib")
        if USE_STATIC_LIB:
          link_command = [
              "gcc", "-o", user_executable, main_object, user_object,
               os.path.join(LIB_FOLDER, "libmatrix.a"), "-lm"
    ]
        else:
         # Verlinke alle .o-Dateien im Compilation-Ordner (z. B. ausgabe.o, matrix_vector.o, ...)
          object_files = [
                  os.path.join(COMPILATION_FOLDER, f)
                  for f in os.listdir(COMPILATION_FOLDER)
                  if f.endswith(".o")
    ]
          link_command = [
             "gcc", "-o", user_executable, main_object, user_object
          ] + object_files + ["-lm"]




        link_result = subprocess.run(link_command, capture_output=True, text=True)

        if link_result.returncode != 0:
            return jsonify({
                "error": "Fehler beim Linken mit libmatrix.a",
                "details": link_result.stderr
            })

        # ✅ Programm ausführen mit INPUT_FILE (und optional EXPECTED_FILE)
        input_file = os.path.join(COMPILATION_FOLDER, INPUT_FILE)

        if EXPECTED_FILE.lower() == "none" or EXPECTED_FILE.strip() == "":
            run_command = [user_executable, input_file]
        else:
            expected_file = os.path.join(COMPILATION_FOLDER, EXPECTED_FILE)
            run_command = [user_executable, input_file, expected_file]

        run_result = subprocess.run(run_command, capture_output=True, text=True)

        stdout_output = run_result.stdout.strip() if run_result.stdout.strip() else "⚠️ Keine Ausgabe"
        stderr_output = run_result.stderr.strip() if run_result.stderr.strip() else "✅ Kein Fehler"

        return jsonify({
            "message": "Programm erfolgreich ausgeführt",
            "stdout": stdout_output,
            "stderr": stderr_output
        })

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


port = int(os.environ.get("PORT", 5000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)

