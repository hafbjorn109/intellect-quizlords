document.addEventListener("DOMContentLoaded", () => {
    const joinBtn = document.getElementById("join-btn");
    const createBtn = document.getElementById("create-btn");

    joinBtn.addEventListener("click", joinGame);
    createBtn.addEventListener("click", createGame);

    function joinGame() {
        const code = document.getElementById("code-input").value.trim();
        if (!code) {
            alert("Please enter a session code.");
            return;
        }
        window.location.href = `/game/${code}`;
    }

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
