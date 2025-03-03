import subprocess
import sys

def test_cholesky(input_file, expected_file):
    try:
        # 1. Kompilieren mit make
        make_command = ["make"]
        subprocess.run(make_command, check=True)

        # 2. Ausführen des kompilierten Programms
        run_command = ["./main.out", input_file, expected_file]
        subprocess.run(run_command, check=True)

        return True  # Wenn alles erfolgreich war, gib True zurück

    except subprocess.CalledProcessError:
        return False  # Wenn ein Fehler auftritt, gib False zurück
    except FileNotFoundError:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    input_file = "aufgabe2.dat"
    expected_file = "expected.txt"

test_cholesky(input_file, expected_file)
        