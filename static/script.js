//  Backend URL (Change if needed)
// Automatically detect if running locally or on Render
const BACKEND_URL = window.location.hostname.includes("render.com")
    ? window.location.origin  // Uses the Render domain dynamically
    : "http://127.0.0.1:5000";  // Fallback for local testing


//  Login Function
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
            showUploadSection();
        }
    })
    .catch(error => console.error("❌ Fehler beim Login:", error));
}

//  Show Upload Section after Login
function showUploadSection() {
    document.getElementById("uploadSection").classList.remove("hidden");
}

//  Upload File Function
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

//  Run C Program Function
function runCProgram() {
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

    fetch(`${BACKEND_URL}/run`, {
        method: "POST",
        body: formData,
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("runStatus").innerText = `❌ Fehler: ${data.error}`;
        } else {
            document.getElementById("runStatus").innerText = `✅ Ausgabe: ${data.output}`;
        }
    })
    .catch(error => console.error("❌ Fehler beim Ausführen:", error));
}
