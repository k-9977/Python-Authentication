const API_URL = "http://127.0.0.1:5000";




const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const message = document.getElementById("message");

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Registration successful! Redirecting...";
                message.className = "success";

                setTimeout(() => {
                    window.location.href = "index.html";
                }, 1000);

            } else {
                message.textContent = data.error || "Registration failed.";
                message.className = "error";
            }

        } catch (error) {
            console.error(error);
            message.textContent = "Unable to connect to the server.";
            message.className = "error";
        }
    });
}




const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const message = document.getElementById("message");

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {

                // Save JWT token
                localStorage.setItem("access_token", data.access_token);

                message.textContent = "Login successful! Redirecting...";
                message.className = "success";

                setTimeout(() => {
                    window.location.href = "dashboard.html";
                }, 500);

            } else {
                message.textContent = data.error || "Login failed.";
                message.className = "error";
            }

        } catch (error) {
            console.error(error);
            message.textContent = "Unable to connect to the server.";
            message.className = "error";
        }
    });
}



const userId = document.getElementById("userId");

if (userId) {

    const token = localStorage.getItem("access_token");

    // No token → go back to login
    if (!token) {
        window.location.href = "index.html";
    } else {

        async function loadUser() {

            try {

                const response = await fetch(`${API_URL}/me`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                const data = await response.json();

                if (response.ok) {

                    document.getElementById("userId").textContent =
                        data.id;

                    document.getElementById("username").textContent =
                        data.username;

                    document.getElementById("email").textContent =
                        data.email;

                } else {

                    // Token is invalid/revoked
                    localStorage.removeItem("access_token");
                    window.location.href = "index.html";
                }

            } catch (error) {

                console.error(error);

                document.getElementById("message").textContent =
                    "Unable to connect to the server.";

                document.getElementById("message").className = "error";
            }
        }

        loadUser();
    }
}




const logoutButton = document.getElementById("logoutButton");

if (logoutButton) {

    logoutButton.addEventListener("click", async function () {

        const token = localStorage.getItem("access_token");

        if (!token) {
            window.location.href = "index.html";
            return;
        }

        try {

            const response = await fetch(`${API_URL}/logout`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const data = await response.json();

            console.log(data);

        } catch (error) {

            console.error(error);

        } finally {

            // Remove JWT from browser
            localStorage.removeItem("access_token");

            // Return to login
            window.location.href = "index.html";
        }
    });
}