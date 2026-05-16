const API_BASE = '';  // mismo origen

async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'  // para enviar cookies de sesión
    };
    if (body) options.body = JSON.stringify(body);
    const resp = await fetch(API_BASE + endpoint, options);
    const data = await resp.json();
    if (!resp.ok) throw data;
    return data;
}
