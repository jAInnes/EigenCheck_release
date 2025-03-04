import subprocess
import sys
import os

def test_cholesky(username):
    """Run Cholesky decomposition test for a specific user."""
    user_folder = os.path.join("uploads", username)

    if not os.path.exists(user_folder):
        print(f"❌ User folder {user_folder} not found!")
        return False

    input_file = os.path.join(user_folder, "aufgabe2.dat")
    expected_file = os.path.join(user_folder, "expected.txt")
    main_exec = os.path.join(user_folder, "main.out")

    try:
        # 1. Run `make` inside user's folder
        make_command = ["make", "-C", user_folder]
        subprocess.run(make_command, check=True)

        # 2. Execute compiled `main.out`
        run_command = [main_exec, input_file, expected_file]
        subprocess.run(run_command, check=True)

        print("✅ Test erfolgreich ausgeführt")
        return True

    except subprocess.CalledProcessError:
        print("❌ Fehler während der Ausführung von make oder main.out")
        return False
    except FileNotFoundError:
        print("❌ Datei nicht gefunden!")
        return False
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Bitte einen Benutzernamen angeben!")
        sys.exit(1)

    username = sys.argv[1]
    test_cholesky(username)
