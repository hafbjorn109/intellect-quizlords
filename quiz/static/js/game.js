document.addEventListener("DOMContentLoaded", () => {

    let socket = io();
    let playerId = null;
    let jwtToken = null;
    let isReady = false;

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
                username: name
            });

            await loadPlayers();
        } catch (err) {
            console.error('Join error:', err)
        }
    }

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
                li.textContent = `${p.name} - ${p.is_ready ? 'Ready' : 'Not Ready'}`;
                ul.appendChild(li);
            });
        } catch (err) {
            console.error('Error loading players:', err)
        }
    }

    async function toggleReady() {
        isReady = !isReady;

        try {
            const res = await fetch(`/sessions/${sessionCode}/players/${playerId}/ready`, {
               method: 'PUT',
               headers: {
                   'Content-Type': 'application/json'
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

    async function setupRound() {
        const categoryId = document.getElementById('category-select').value;

        try {
            const res = await fetch(`/sessions/${sessionCode}/rounds/setup`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({category_id: parseInt(categoryId)})
            });

            const data = await res.json();
            if (data.error) {
                alert(JSON.stringify(data.error));
                return;
            }

            if (data.game_over) {
                alert('Game Over!');
                await showScoreboard();
                return;
            }

            document.getElementById("category-pick-section").style.display = "none";

        } catch (err) {
            console.error('Error setting up round:', err);
        }
    }

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

    async function showScoreboard() {
        try {
            const res = await fetch(`/sessions/${sessionCode}/scoreboard`);
            const data = await res.json();

            const section = document.createElement('div');
            section.innerHTML = '<h2> Final Scoreboard</h2><ul></ul>'
            const ul = section.querySelector('ul');

            data.forEach(p => {
                const li = document.createElement('li');
                li.textContent = `${p.name} - ${p.score} pts`;
                ul.appendChild(li);
            });
            document.body.innerHTML = '';
            document.body.appendChild(section);

        } catch (err) {
            console.error('Could not fetch scoreboeard:', err)
        }
    }

    // Socket listeners
    socket.on('round_started', data => {
        console.log("Round started:", data);

        document.getElementById("category-pick-section").style.display = "none";
        document.getElementById("question-text").textContent = data.question.text;
        document.getElementById("question-section").style.display = "block";

        document.getElementById("round-header").textContent =
            `Round ${data.round_number} of 10`;
    });

    socket.on('player_joined', async (data) => {
        console.log('Player joined:', data);
        await loadPlayers();
    });

    socket.on('player_ready_updated', async (data) => {
        console.log('Ready status updated:', data);
        await loadPlayers();
    })

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

    // Global functions to bind to HTML buttons
    window.joinSession = joinSession;
    window.toggleReady = toggleReady;
    window.setupRound = setupRound;
});


