document.addEventListener("DOMContentLoaded", () => {
    // Toggle password visibility
    const togglePasswordButton = document.getElementById("togglePassword");
    const passwordField = document.getElementById("password");

    togglePasswordButton.addEventListener("click", () => {
        passwordField.type = passwordField.type === "password" ? "text" : "password";
    });

    // Handle form submission (JSON-based)
    document.getElementById("loginForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const roleInput = document.querySelector('input[name="role"]:checked');
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const messageEl = document.getElementById("message");

        if (!roleInput || !email || !password) {
            messageEl.style.color = "red";
            messageEl.textContent = "Please fill in all fields.";
            return;
        }

        const role = roleInput.value;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                messageEl.style.color = "green";
                messageEl.textContent = "Login successful! Redirecting...";

                // Save the user email, username, and role to sessionStorage for session use
                sessionStorage.setItem("user_email", data.email);
                sessionStorage.setItem("user_name", data.username);
                sessionStorage.setItem("user_role", role);
                console.log("Stored user_email:", sessionStorage.getItem("user_email"));
                console.log("Stored user_name:", sessionStorage.getItem("user_name"));

                setTimeout(() => {
                    if (role === "admin") {
                        window.location.href = "/admin.html";
                    } else {
                        window.location.href = "/index.html";
                    }
                }, 1000);

            } else {
                messageEl.style.color = "red";
                messageEl.textContent = data.detail || "Login failed";
            }
        } catch (error) {
            console.error("Error:", error);
            messageEl.style.color = "red";
            messageEl.textContent = "An error occurred. Please try again.";
        }
    });
});
