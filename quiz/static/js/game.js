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
                alert(players.error);
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
                alert(data.error);
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

    // Socket listeners
    socket.on('player_joined', async (data) => {
        console.log('Player joined:', data);
        await loadPlayers();
    });

    socket.on('player_ready_updated', async (data) => {
        console.log('Ready status updated:', data);
        await loadPlayers();
    })

    // Global functions to bind to HTML buttons
    window.joinSession = joinSession;
    window.toggleReady = toggleReady;
});


