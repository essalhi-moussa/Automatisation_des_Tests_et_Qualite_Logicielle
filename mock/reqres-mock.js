#!/usr/bin/env node
/**
 * Mock local de l'API Reqres (sans dependance).
 *
 * Pourquoi : l'API publique impose une limite de 20 requetes/minute et un quota journalier
 * de 40 requetes. Ce mock reproduit le contrat observe sur https://reqres.in afin de
 * pouvoir developper, rejouer la CI et mesurer la charge sans epuiser le quota.
 *
 * Usage : node mock/reqres-mock.js [port]  (defaut 3999)
 * Variables : RATE_LIMIT (requetes par fenetre, 0 = desactive), RATE_WINDOW_S (defaut 60),
 *             LATENCY_MS (latence artificielle, defaut 0).
 */
const http = require('http');
const { URL } = require('url');

const PORT = parseInt(process.argv[2] || process.env.PORT || '3999', 10);
const RATE_LIMIT = parseInt(process.env.RATE_LIMIT || '0', 10);
const RATE_WINDOW_S = parseInt(process.env.RATE_WINDOW_S || '60', 10);
const LATENCY_MS = parseInt(process.env.LATENCY_MS || '0', 10);

const NAMES = [
  ['George', 'Bluth'], ['Janet', 'Weaver'], ['Emma', 'Wong'], ['Eve', 'Holt'],
  ['Charles', 'Morris'], ['Tracey', 'Ramos'], ['Michael', 'Lawson'], ['Lindsay', 'Ferguson'],
  ['Tobias', 'Funke'], ['Byron', 'Fields'], ['George', 'Edwards'], ['Rachel', 'Howell'],
];
const USERS = NAMES.map(([first, last], i) => ({
  id: i + 1,
  email: `${first.toLowerCase()}.${last.toLowerCase()}@reqres.in`,
  first_name: first,
  last_name: last,
  avatar: `https://reqres.in/img/faces/${i + 1}-image.jpg`,
}));

let nextId = 100;
let windowStart = Date.now();
let windowCount = 0;

function send(res, status, body, extra = {}) {
  const payload = body === undefined ? '' : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', ...extra });
  res.end(payload);
}

function readBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (c) => (data += c));
    req.on('end', () => {
      try { resolve(data ? JSON.parse(data) : {}); } catch (e) { resolve(null); }
    });
  });
}

function rateLimit(res) {
  if (RATE_LIMIT <= 0) return false;
  const now = Date.now();
  if (now - windowStart > RATE_WINDOW_S * 1000) { windowStart = now; windowCount = 0; }
  windowCount += 1;
  const reset = Math.max(0, Math.ceil((windowStart + RATE_WINDOW_S * 1000 - now) / 1000));
  const headers = {
    'Ratelimit-Limit': String(RATE_LIMIT),
    'Ratelimit-Remaining': String(Math.max(0, RATE_LIMIT - windowCount)),
    'Ratelimit-Reset': String(reset),
  };
  if (windowCount > RATE_LIMIT) {
    send(res, 429, { error: 'Too many requests' }, headers);
    return true;
  }
  res.setHeader('Ratelimit-Limit', headers['Ratelimit-Limit']);
  res.setHeader('Ratelimit-Remaining', headers['Ratelimit-Remaining']);
  res.setHeader('Ratelimit-Reset', headers['Ratelimit-Reset']);
  return false;
}

async function handle(req, res) {
  if (rateLimit(res)) return;
  const url = new URL(req.url, `http://${req.headers.host}`);
  const parts = url.pathname.split('/').filter(Boolean); // ['api','users','2']
  if (parts[0] !== 'api') return send(res, 404, {});

  if (parts[1] === 'users' && req.method === 'GET' && parts.length === 2) {
    const perPage = parseInt(url.searchParams.get('per_page') || '6', 10);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const totalPages = Math.ceil(USERS.length / perPage);
    const data = USERS.slice((page - 1) * perPage, page * perPage);
    return send(res, 200, { page, per_page: perPage, total: USERS.length, total_pages: totalPages, data });
  }
  if (parts[1] === 'users' && parts.length === 3) {
    const id = parseInt(parts[2], 10);
    if (req.method === 'GET') {
      const user = USERS.find((u) => u.id === id);
      return user ? send(res, 200, { data: user }) : send(res, 404, {});
    }
    if (req.method === 'PUT' || req.method === 'PATCH') {
      const body = await readBody(req);
      if (body === null) return send(res, 400, { error: 'Invalid JSON' });
      return send(res, 200, { ...body, updatedAt: new Date().toISOString() });
    }
    if (req.method === 'DELETE') return send(res, 204);
  }
  if (parts[1] === 'users' && req.method === 'POST' && parts.length === 2) {
    const body = await readBody(req);
    if (body === null) return send(res, 400, { error: 'Invalid JSON' });
    return send(res, 201, { ...body, id: String(nextId++), createdAt: new Date().toISOString() });
  }
  if ((parts[1] === 'login' || parts[1] === 'register') && req.method === 'POST') {
    const body = await readBody(req);
    if (body === null) return send(res, 400, { error: 'Invalid JSON' });
    if (!body.email) return send(res, 400, { error: 'Missing email or username' });
    if (!body.password) return send(res, 400, { error: 'Missing password' });
    const known = USERS.find((u) => u.email === body.email);
    if (!known) {
      return send(res, 400, {
        error: parts[1] === 'login' ? 'user not found' : 'Note: Only defined users succeed registration',
      });
    }
    return send(res, 200, parts[1] === 'login'
      ? { token: 'QpwL5tke4Pnpja7X4' }
      : { id: known.id, token: 'QpwL5tke4Pnpja7X4' });
  }
  return send(res, 404, {});
}

http.createServer((req, res) => {
  const run = () => handle(req, res).catch(() => send(res, 500, { error: 'Erreur interne du mock' }));
  LATENCY_MS > 0 ? setTimeout(run, LATENCY_MS) : run();
}).listen(PORT, () => {
  console.log(`Mock Reqres sur http://localhost:${PORT} (rate limit: ${RATE_LIMIT || 'off'}/${RATE_WINDOW_S}s)`);
});
