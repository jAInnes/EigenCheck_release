// Backend URL (Change if needed)
const BACKEND_URL = "http://127.0.0.1:5000";

// Login Function
function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    fetch(`${BACKEND_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loginStatus").innerText = data.message;
        if (data.status === "success") {
            sessionStorage.setItem("loggedIn", "true");
            sessionStorage.setItem("username", data.username);
            if (data.username === "admin") {
                showAdminSection(data.users);
            } else {
                showUploadSection();
            }
        }
    })
    .catch(error => console.error("❌ Fehler beim Login:", error));
}

// Show Upload Section after Login
function showUploadSection() {
    document.getElementById("uploadSection").classList.remove("hidden");
}

// Show Admin Section
function showAdminSection(users) {
    document.getElementById("adminSection").classList.remove("hidden");
    document.getElementById("uploadSection").classList.add("hidden");
    document.getElementById("runSection").classList.add("hidden");

    let userList = document.getElementById("userList");
    userList.innerHTML = "";
    for (let username in users) {
        if (username !== "admin") {
            let listItem = document.createElement("li");
            listItem.innerText = `User: ${username} | Password: ${users[username]}`;
            userList.appendChild(listItem);
        }
    }
}

// Upload File Function
function uploadFile() {
    if (sessionStorage.getItem("loggedIn") !== "true") {
        alert("Bitte zuerst einloggen!");
        return;
    }

    let fileInput = document.getElementById("fileInput").files[0];
    if (!fileInput) {
        alert("Bitte eine Datei auswählen!");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        body: formData,
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("uploadStatus").innerText = data.message;
        if (!data.error) {
            document.getElementById("runSection").classList.remove("hidden");
        }
    })
    .catch(error => console.error("❌ Fehler beim Hochladen:", error));
}

// Run C Program Function
function runCProgram() {
    if (sessionStorage.getItem("loggedIn") !== "true") {
        alert("Bitte zuerst einloggen!");
        return;
    }

    fetch(`${BACKEND_URL}/run`, {
        method: "POST",
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        let outputText = "";
        if (data.error) {
            outputText = `❌ Fehler: ${data.error}\n\n🔴 stderr:\n${data.stderr || "Keine Fehlermeldung"}\n🟢 stdout:\n${data.stdout || "Keine Ausgabe"}`;
        } else {
            outputText = `✅ Programm erfolgreich ausgeführt\n\n🟢 stdout:\n${data.stdout}\n🔴 stderr:\n${data.stderr}`;
        }
        document.getElementById("runStatus").innerText = outputText;
    })
    .catch(error => console.error("❌ Fehler beim Ausführen:", error));
}