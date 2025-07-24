document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('admin-login-form').onsubmit = async (e) => {
        e.preventDefault();
        const username = e.target.username.value.trim();
        const password = e.target.password.value;

        const res = await fetch('/admin/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await res.json();
        const msg = document.getElementById('login-msg');

        if (res.ok) {
            localStorage.setItem('adminToken', data.access_token);
            window.location.href = '/admin';
        } else {
            msg.textContent = data.error || 'Login failed.';
            msg.style.color = 'red';
        }
    }
})