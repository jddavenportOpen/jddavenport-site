// POST /api/newsletter-contribute
//
// The one write door for the AI Foundry monthly newsletter. A Foundry member submits a
// section from /newsletter/contribute; this function checks it and inserts one row into
// public.newsletter_contributions with the service key. Leads review every row before
// anything is drafted, and only JD approves a send, through a separate gate. Nothing
// here sends mail or notifies anyone.
//
// Contract (shared with the monthly assembler; change it only with that lane):
//   body  {invite_code, name, email, role, section_type, title, body, links[], edition,
//          website (honeypot, must be empty), started_at (ms epoch),
//          consent (must be true: permission to print the section with the name)}
//   200   {ok:true, id}
//   4xx   {ok:false, error}
// It never echoes the invite code and never returns rows.
//
// Env (Vercel, production):
//   NEWSLETTER_CONTRIB_CODES         comma-separated invite codes
//   SUPABASE_NEWSLETTER_URL          https://<ref>.supabase.co
//   SUPABASE_NEWSLETTER_SERVICE_KEY  service-role key (the table has RLS on and no anon grant)

const crypto = require('crypto');

const LIMITS = { name: 100, email: 254, role: 120, title: 120, body: 2500, link: 500, links: 5 };
const MIN_BODY = 20;
const SECTION_TYPES = ['project', 'lesson', 'event', 'spotlight', 'tool', 'other'];
const EDITIONS = ['mba', 'general', 'both'];
const MIN_FILL_MS = 3000;
const RATE_LIMIT = 5; // submissions per hashed IP per hour, best effort
const MAX_BODY_BYTES = 20000;
const UPSTREAM_TIMEOUT_MS = 8000;
// Links must point at the public internet. The assembler checks every link from JD's
// machine, so a loopback, LAN, tailnet or bare-IP host is refused here (the assembler
// also resolves and refuses non-public addresses; this is the first layer).
const PRIVATE_HOST_SUFFIXES = ['.local', '.internal', '.lan', '.home.arpa', '.ts.net', '.localhost'];
function publicHost(hostname) {
  const h = String(hostname || '').toLowerCase().replace(/\.$/, '');
  if (!h || h === 'localhost' || !h.includes('.')) return false;
  if (h.startsWith('[') || /^[0-9.]+$/.test(h) || /^0x/i.test(h)) return false; // IPv6 or IPv4 literal
  if (/^[0-9a-f:]+$/i.test(h) && h.includes(':')) return false;
  return !PRIVATE_HOST_SUFFIXES.some((s) => h.endsWith(s));
}
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[A-Za-z]{2,}$/;

function send(res, status, payload) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex');
  res.end(JSON.stringify(payload));
}

// The issue a submission lands in: the current month in Denver, or next month from the 26th,
// because the assembler drafts on the 25th.
function issueMonth(now = new Date()) {
  const parts = {};
  for (const p of new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Denver', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now)) parts[p.type] = p.value;
  let y = Number(parts.year);
  let m = Number(parts.month);
  if (Number(parts.day) >= 26) {
    m += 1;
    if (m === 13) { m = 1; y += 1; }
  }
  return `${y}-${String(m).padStart(2, '0')}`;
}

// Constant-time check against every configured code. Hashing first gives equal-length
// buffers, and the loop never exits early, so timing says nothing about which code or
// how much of one matched.
function codeOk(given, configured) {
  const codes = String(configured || '').split(',').map((c) => c.trim()).filter(Boolean);
  if (!codes.length || typeof given !== 'string' || !given) return false;
  const g = crypto.createHash('sha256').update(given.trim()).digest();
  let ok = false;
  for (const c of codes) {
    const h = crypto.createHash('sha256').update(c).digest();
    if (crypto.timingSafeEqual(g, h)) ok = true;
  }
  return ok;
}

function clean(v) {
  return typeof v === 'string' ? v.trim() : '';
}

// Returns {row} or {error}. Never includes the invite code in either.
function validate(b) {
  const name = clean(b.name);
  const email = clean(b.email).toLowerCase();
  const role = clean(b.role);
  const title = clean(b.title);
  const body = clean(b.body);
  const sectionType = clean(b.section_type);
  const edition = clean(b.edition) || 'both';
  if (b.consent !== true) return { error: 'Tick the box so leads can print it with your name.' };
  if (!name) return { error: 'Add your name.' };
  if (name.length > LIMITS.name) return { error: `Name is limited to ${LIMITS.name} characters.` };
  if (!email || email.length > LIMITS.email || !EMAIL_RE.test(email)) return { error: 'Add a valid email address.' };
  if (role.length > LIMITS.role) return { error: `Role is limited to ${LIMITS.role} characters.` };
  if (!SECTION_TYPES.includes(sectionType)) return { error: 'Pick what kind of section this is.' };
  if (!EDITIONS.includes(edition)) return { error: 'Pick an edition.' };
  if (!title) return { error: 'Add a title.' };
  if (title.length > LIMITS.title) return { error: `Title is limited to ${LIMITS.title} characters.` };
  if (body.length < MIN_BODY) return { error: `Write at least ${MIN_BODY} characters.` };
  if (body.length > LIMITS.body) return { error: `The section is limited to ${LIMITS.body} characters.` };
  let links = b.links == null ? [] : b.links;
  if (!Array.isArray(links)) return { error: 'Links must be a list.' };
  links = links.map(clean).filter(Boolean);
  if (links.length > LIMITS.links) return { error: `Add at most ${LIMITS.links} links.` };
  for (const l of links) {
    let u;
    try { u = new URL(l); } catch (e) { return { error: 'Each link must be a full http or https address.' }; }
    if ((u.protocol !== 'https:' && u.protocol !== 'http:') || l.length > LIMITS.link
        || u.username || u.password || !publicHost(u.hostname)) {
      return { error: 'Each link must be a full http or https address.' };
    }
  }
  return {
    row: {
      edition,
      contributor_name: name,
      contributor_email: email,
      contributor_role: role || null,
      section_type: sectionType,
      title,
      body,
      links,
      status: 'submitted',
      consent_public: true,
    },
  };
}

function clientIp(req) {
  const xff = req.headers['x-forwarded-for'];
  if (xff) return String(xff).split(',')[0].trim();
  return String(req.headers['x-real-ip'] || (req.socket && req.socket.remoteAddress) || '');
}

// Keyed hash, so the stored value cannot be reversed by hashing every IPv4 address.
function hashIp(ip, secret) {
  return crypto.createHmac('sha256', String(secret)).update(`newsletter-contrib:${ip}`).digest('hex');
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  let raw = '';
  if (typeof req.body === 'string') raw = req.body;
  else if (Buffer.isBuffer(req.body)) raw = req.body.toString('utf8');
  else {
    raw = await new Promise((resolve, reject) => {
      let data = '';
      req.on('data', (c) => {
        data += c;
        if (data.length > MAX_BODY_BYTES) reject(new Error('too large'));
      });
      req.on('end', () => resolve(data));
      req.on('error', reject);
    });
  }
  if (raw.length > MAX_BODY_BYTES) throw new Error('too large');
  return JSON.parse(raw || '{}');
}

async function supabase(base, key, path, init) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), UPSTREAM_TIMEOUT_MS);
  try {
    return await fetch(`${base.replace(/\/+$/, '')}/rest/v1/${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        'Content-Type': 'application/json',
        ...(init && init.headers),
      },
    });
  } finally {
    clearTimeout(t);
  }
}

async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return send(res, 405, { ok: false, error: 'Use POST.' });
  }
  let b;
  try {
    b = await readBody(req);
  } catch (e) {
    return send(res, 400, { ok: false, error: 'Send the form as JSON.' });
  }
  if (!b || typeof b !== 'object' || Array.isArray(b)) return send(res, 400, { ok: false, error: 'Send the form as JSON.' });

  // Honeypot: a person never sees this field. Answer like a success and store nothing,
  // so a bot learns nothing from the response.
  if (clean(b.website)) return send(res, 200, { ok: true, id: crypto.randomUUID() });

  const started = Number(b.started_at);
  if (!Number.isFinite(started) || Date.now() - started < MIN_FILL_MS) {
    return send(res, 400, { ok: false, error: 'That was quick. Take a second look and submit again.' });
  }

  if (!codeOk(b.invite_code, process.env.NEWSLETTER_CONTRIB_CODES)) {
    return send(res, 403, { ok: false, error: "That invite code didn't work. Ask a Foundry lead for the current one." });
  }

  const v = validate(b);
  if (v.error) return send(res, 400, { ok: false, error: v.error });

  const base = process.env.SUPABASE_NEWSLETTER_URL;
  const key = process.env.SUPABASE_NEWSLETTER_SERVICE_KEY;
  if (!base || !key) return send(res, 503, { ok: false, error: 'Contributions are closed right now. Try again later.' });

  const ipHash = hashIp(clientIp(req), key);
  try {
    const since = new Date(Date.now() - 3600 * 1000).toISOString();
    const q = `newsletter_contributions?select=id&ip_hash=eq.${ipHash}&created_at=gte.${encodeURIComponent(since)}&limit=${RATE_LIMIT}`;
    const r = await supabase(base, key, q, { method: 'GET' });
    if (r.ok) {
      const recent = await r.json();
      if (Array.isArray(recent) && recent.length >= RATE_LIMIT) {
        return send(res, 429, { ok: false, error: 'Too many submissions from here this hour. Try again later.' });
      }
    }
    // A failed rate-limit read does not block a real contributor: the limit is best effort.
  } catch (e) {
    /* best effort */
  }

  const row = { ...v.row, issue_month: issueMonth(), ip_hash: ipHash };
  try {
    const r = await supabase(base, key, 'newsletter_contributions?select=id', {
      method: 'POST',
      headers: { Prefer: 'return=representation' },
      body: JSON.stringify(row),
    });
    if (!r.ok) return send(res, 502, { ok: false, error: 'We could not save that. Try again in a minute.' });
    const out = await r.json();
    const id = Array.isArray(out) && out[0] && out[0].id;
    if (!id) return send(res, 502, { ok: false, error: 'We could not save that. Try again in a minute.' });
    return send(res, 200, { ok: true, id });
  } catch (e) {
    return send(res, 502, { ok: false, error: 'We could not save that. Try again in a minute.' });
  }
}

module.exports = handler;
module.exports._internal = { issueMonth, codeOk, validate, hashIp, publicHost, LIMITS };
