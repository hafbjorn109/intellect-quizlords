document.addEventListener("DOMContentLoaded", () => {
    const joinBtn = document.getElementById("join-btn");
    const createBtn = document.getElementById("create-btn");

    joinBtn.addEventListener("click", joinGame);
    createBtn.addEventListener("click", createGame);

    /**
     * Redirects the player to an existing game session using the code entered in the input field.
     * Displays an alert if the code is missing.
     */
    function joinGame() {
        const code = document.getElementById("code-input").value.trim();
        if (!code) {
            alert("Please enter a session code.");
            return;
        }
        window.location.href = `/game/${code}`;
    }

    /**
     * Sends a POST request to create a new game session.
     * Redirects the user to the newly created session's URL on success.
     * Displays an error message if creation fails.
     */
    async function createGame() {
        try {
            const res = await fetch("/sessions", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            const data = await res.json();

            if (!data.code) {
                alert("Could not create game session.");
                return;
            }

            window.location.href = `/game/${data.code}`;
        } catch (err) {
            console.error("Error creating session:", err);
            alert("Something went wrong.");
        }
    }
});
