document.addEventListener("DOMContentLoaded", () => {

    let socket = io();
    let playerId = null;
    let jwtToken = null;
    let isReady = false;
    let currentRoundId = null;

    /**
     * Joins the current player to the game session using their name.
     * Sends POST request to backend and emits `join` via socket.
     * Updates view to show the lobby.
     */
    async function joinSession() {
        const name = document.getElementById('player-name').value;

        try {
            const res = await fetch(`/sessions/${sessionCode}/join`,{
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name })
            });

            const data = await res.json();

            if (data.error) {
                alert(JSON.stringify(data.error));
                return;
            }

            playerId = data.player.id;
            jwtToken = data.access_token;

            document.getElementById('join-section').style.display = 'none';
            document.getElementById('lobby-section').style.display = 'block';

            socket.emit('join', {
                room: sessionCode,
                username: name,
                player_id: playerId
            });

            await loadPlayers();
        } catch (err) {
            console.error('Join error:', err)
        }
    }

    /**
     * Fetches the list of players in the session and updates the player list UI.
     */
    async function loadPlayers() {
        try {
            const res = await fetch(`/sessions/${sessionCode}/players`);
            const players = await res.json();

            if (players.error) {
                alert(JSON.stringify(players.error));
                return;
            }

            const ul = document.getElementById('player-list');
            ul.innerHTML = '';

            players.forEach(p => {
                const li = document.createElement('li');
                const statusIcon = p.is_connected ? '🟢' : '🔴';
                const readyText = p.is_ready ? 'Ready' : 'Not Ready';
                li.textContent = `${statusIcon} ${p.name} - ${readyText}`;
                ul.appendChild(li);
            });

        } catch (err) {
            console.error('Error loading players:', err)
        }
    }

    /**
     * Toggles the ready status of the player, updates backend, UI, and emits socket event.
     */
    async function toggleReady() {
        isReady = !isReady;

        try {
            const res = await fetch(`/sessions/${sessionCode}/players/${playerId}/ready`, {
               method: 'PUT',
               headers: {
                   'Content-Type': 'application/json',
                   'Authorization': `Bearer ${jwtToken}`
               },
                body: JSON.stringify({ is_ready: isReady })
            });

            const data = await res.json();

            if (data.error) {
                alert(JSON.stringify(data.error));
                return;
            }

            await loadPlayers();
            document.getElementById('ready-button').textContent = isReady ? "Not Ready" : 'Ready';

            socket.emit('player_ready_changed', {
                room: sessionCode,
                player_id: playerId,
                is_ready: isReady
            })
        } catch (err) {
            console.error('Error toggling ready:', err)
        }
    }

    /**
     * Sends a category choice to the backend to start the round.
     * Hides the category picker after selection.
     */
    async function setupRound() {
        const categoryId = document.getElementById('category-select').value;

        try {
            const res = await fetch(`/sessions/${sessionCode}/rounds/setup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({category_id: parseInt(categoryId)})
            });

            const data = await res.json();
            if (data.error) {
                alert(JSON.stringify(data.error));
                return;
            }

            if (data.game_over) {
                return;
            }

            document.getElementById('category-pick-section').style.display = 'none';

        } catch (err) {
            console.error('Error setting up round:', err);
        }
    }

    /**
     * Fetches all available categories from backend and populates the <select> dropdown.
     */
    async function loadCategories() {
        try {
            const res = await fetch('/categories');
            const data = await res.json();

            if (data.errors) {
                alert(JSON.stringify(data.error));
                return;
            }

            const select = document.getElementById('category-select');
            select.innerHTML = '';

            data.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                select.appendChild(option);
            })

        } catch (err) {
            console.error('Error loading categories:', err)
        }
    }

    /**
     * Submits selected answer to backend, shows result and disables answer buttons.
     */
    async function submitAnswer(answerId) {
        if (!currentRoundId || !playerId) {
            alert('Missing round or player info');
            return;
        }

        try {
            const res = await fetch(`/sessions/${sessionCode}/rounds/answer`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwtToken}`
                },
                body: JSON.stringify({
                    round_id: currentRoundId,
                    player_id: playerId,
                    answer_id: answerId
                })
            });

            const data = await res.json();
            if (data.error) {
                alert(data.error);
                return;
            }

            // Disable all buttons
            document.querySelectorAll("#answer-options button").forEach(btn => {
                btn.disabled = true;
            });

            if (data.is_correct) {
                alert("Correct!");
            } else {
                alert("Incorrect!");
            }

        } catch (err) {
            console.error("Error submitting answer:", err);
        }
    }

    /**
     * Updates the scoreboard section with current scores.
     */
    function updateScoreboard(players) {
        const list = document.getElementById('scoreboard-list');
        list.innerHTML = '';

        players.forEach(p => {
            const li = document.createElement('li');
            li.textContent = `${p.name}: ${p.score} pts`;
            list.appendChild(li);
        });

        document.getElementById('scoreboard-section').style.display = 'block';
    }

    // Socket listeners
    socket.on('round_started', data => {
        console.log("Round started:", data);

        document.getElementById("category-pick-section").style.display = "none";
        document.getElementById("lobby-section").style.display = "none";

        const q = data.question;
        currentRoundId = data.question.round_id || data.round_id;

        document.getElementById("question-text").textContent = q.text;
        const container = document.getElementById("answer-options");
        container.innerHTML = "";

        q.answers.forEach(answer => {
            const btn = document.createElement("button");
            btn.textContent = answer.text;
            btn.onclick = () => submitAnswer(answer.id);
            btn.dataset.answered = "false";
            container.appendChild(btn);
        });

        document.getElementById("question-section").style.display = "block";
    });

    // Handles when a new player joins the session.
    socket.on('player_joined', async (data) => {
        console.log('Player joined:', data);
        await loadPlayers();
    });

    // Updates the readiness status of a player in the lobby.
    socket.on('player_ready_updated', async (data) => {
        console.log('Ready status updated:', data);
        await loadPlayers();
    });

    /**
     * Handles the event when the game officially starts.
     * Displays chooser info and shows category selection if applicable.
     */
    socket.on('game_started', async (data) => {
        console.log('Game started!');

        document.getElementById('lobby-section').style.display = 'none';

        document.getElementById('chooser-display').textContent = `Chooser: ${data.chooser.name}`;
        document.getElementById('round-header').textContent = `Round ${data.round_number} of 10`;
        document.getElementById('round-section').style.display = 'block';

        if (data.chooser.id === playerId) {
            await loadCategories();
            document.getElementById('category-pick-section').style.display = 'block';
        }
    });

    // Handles transition to the next chooser and round.
    socket.on('chooser_turn', async (data) => {
        document.getElementById('question-section').style.display = 'none';
        document.getElementById('category-pick-section').style.display = 'none';
        document.getElementById('round-header').textContent = `Round ${data.round_number} of 10`;
        document.getElementById('chooser-display').textContent = `New chooser: ${data.chooser.name}`;

        updateScoreboard(data.scoreboard);

        if (data.chooser.id === playerId) {
            await loadCategories();
            document.getElementById('category-pick-section').style.display = 'block'
        }
    });

    // Displays the final scoreboard and ends the game view.
    socket.on('game_over', data => {
        const scoreboard = data.scoreboard;

        document.getElementById('scoreboard-section').style.display = 'none';
        document.getElementById('category-pick-section').style.display = 'none';
        document.getElementById('question-section').style.display = 'none';
        document.getElementById('chooser-display').style.display = 'none';
        document.getElementById('round-header').style.display = 'none';
        document.getElementById('round-section').style.display = 'none';

        const gameOverHeader = document.createElement('h2');
        gameOverHeader.innerHTML = 'Game Over - Final Scoreboard';
        document.body.appendChild(gameOverHeader)

        const table = document.createElement('table');
        table.classList.add('scoreboard-table');

        const headerRow = table.insertRow();
        headerRow.innerHTML = '<th>Player</th><th>Score</th>';

        scoreboard.forEach(player => {
            const row = table.insertRow();
            row.innerHTML = `<td>${player.name}</td><td>${player.score}</td>`;
        });

        document.body.appendChild(table);
    });

    // Updates player list when someone leaves the session.
    socket.on('player_left', async (data) => {
        console.log('Player left:', data);
        await loadPlayers();
    });

    /**
     * Emits a 'leave' event to the server before the player closes or reloads the tab.
     *
     * This ensures the server is explicitly notified that the player has left,
     * allowing it to update connection status and remove the player from the room.
     */
    window.addEventListener('beforeunload', () => {
        if (playerId && sessionCode) {
            socket.emit('leave', {
                room: sessionCode,
                player_id: playerId
            });
        }
    });

    // Global functions to bind to HTML buttons
    window.joinSession = joinSession;
    window.toggleReady = toggleReady;
    window.setupRound = setupRound;
});


