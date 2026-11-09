// node --test api/test-newsletter-contribute.js
// Mocked fetch only: nothing here reaches Supabase. .vercelignore keeps this file out of the deploy.
const test = require('node:test');
const assert = require('node:assert/strict');
const handler = require('./newsletter-contribute.js');
const { issueMonth, codeOk, validate } = handler._internal;

const CODE = 'foundry-testcode1';
const ENV = {
  NEWSLETTER_CONTRIB_CODES: `other-code, ${CODE}`,
  SUPABASE_NEWSLETTER_URL: 'https://example.supabase.co',
  SUPABASE_NEWSLETTER_SERVICE_KEY: 'service-key-test',
};

function good(over = {}) {
  return {
    invite_code: CODE, name: 'Ada Builder', email: 'ada@example.com', role: 'MBA 2027',
    section_type: 'project', title: 'We shipped a scheduler', body: 'A short honest account of what we built and what broke.',
    links: ['https://example.com/demo'], edition: 'mba', website: '', started_at: Date.now() - 10000, consent: true, ...over,
  };
}

function mockRes() {
  return {
    statusCode: 0, headers: {}, body: '',
    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
    end(b) { this.body = b; },
    json() { return JSON.parse(this.body); },
  };
}

async function call(body, { method = 'POST', env = ENV, fetchImpl, headers = {} } = {}) {
  const saved = { ...process.env };
  Object.assign(process.env, env);
  const calls = [];
  const realFetch = global.fetch;
  global.fetch = async (url, init) => {
    calls.push({ url, init });
    if (fetchImpl) return fetchImpl(url, init, calls);
    if (init.method === 'GET') return { ok: true, json: async () => [] };
    return { ok: true, json: async () => [{ id: '11111111-2222-3333-4444-555555555555' }] };
  };
  const res = mockRes();
  try {
    await handler({ method, body, headers: { 'x-forwarded-for': '203.0.113.9, 10.0.0.1', ...headers } }, res);
  } finally {
    global.fetch = realFetch;
    for (const k of Object.keys(env)) delete process.env[k];
    Object.assign(process.env, saved);
  }
  return { res, out: res.json(), calls };
}

test('a valid submission inserts one row and returns only ok and id', async () => {
  const { res, out, calls } = await call(good());
  assert.equal(res.statusCode, 200);
  assert.deepEqual(out, { ok: true, id: '11111111-2222-3333-4444-555555555555' });
  assert.equal(res.headers['cache-control'], 'no-store');
  const insert = calls.find((c) => c.init.method === 'POST');
  assert.ok(insert.url.startsWith('https://example.supabase.co/rest/v1/newsletter_contributions'));
  assert.equal(insert.init.headers.apikey, 'service-key-test');
  const row = JSON.parse(insert.init.body);
  assert.equal(row.contributor_name, 'Ada Builder');
  assert.equal(row.contributor_email, 'ada@example.com');
  assert.equal(row.edition, 'mba');
  assert.equal(row.status, 'submitted');
  assert.equal(row.consent_public, true);
  assert.match(row.issue_month, /^\d{4}-\d{2}$/);
  assert.match(row.ip_hash, /^[0-9a-f]{64}$/);
  assert.ok(!('invite_code' in row) && !JSON.stringify(row).includes(CODE), 'the code is never stored');
  assert.ok(!res.body.includes(CODE), 'the code is never echoed');
});

test('a wrong or missing invite code is refused without touching the database', async () => {
  for (const code of ['nope', '', undefined, `${CODE}x`]) {
    const { res, out, calls } = await call(good({ invite_code: code }));
    assert.equal(res.statusCode, 403);
    assert.equal(out.ok, false);
    assert.equal(calls.length, 0);
    if (code) assert.ok(!res.body.includes(code));
  }
});

test('no codes configured means nobody gets in', async () => {
  const { res } = await call(good(), { env: { ...ENV, NEWSLETTER_CONTRIB_CODES: ' , ' } });
  assert.equal(res.statusCode, 403);
});

test('the honeypot answers like a success and stores nothing', async () => {
  const { res, out, calls } = await call(good({ website: 'http://spam.example' }));
  assert.equal(res.statusCode, 200);
  assert.equal(out.ok, true);
  assert.equal(calls.length, 0);
});

test('a form sent under 3 seconds after render, or with no timestamp, is refused', async () => {
  for (const started of [Date.now(), Date.now() - 1000, undefined, 'abc']) {
    const { res, calls } = await call(good({ started_at: started }));
    assert.equal(res.statusCode, 400);
    assert.equal(calls.length, 0);
  }
});

test('only POST is allowed', async () => {
  const { res } = await call(good(), { method: 'GET' });
  assert.equal(res.statusCode, 405);
});

test('field validation: lengths, email, enums and links', async () => {
  const cases = [
    { name: '' }, { name: 'x'.repeat(101) }, { email: 'not-an-email' }, { email: 'a@b' },
    { title: '' }, { title: 'x'.repeat(121) }, { body: 'too short' }, { body: 'x'.repeat(2501) },
    { section_type: 'ad' }, { edition: 'everyone' }, { role: 'x'.repeat(121) },
    { links: 'https://example.com' }, { links: ['javascript:alert(1)'] }, { links: ['ftp://example.com/x'] },
    { links: ['not a url'] }, { links: Array.from({ length: 6 }, (_, i) => `https://example.com/${i}`) },
  ];
  for (const c of cases) {
    const { res, out, calls } = await call(good(c));
    assert.equal(res.statusCode, 400, JSON.stringify(c).slice(0, 60));
    assert.equal(out.ok, false);
    assert.equal(calls.length, 0);
  }
});

test('edition defaults to both, five links is fine, blank links are dropped', () => {
  const v = validate(good({ edition: '', links: ['https://a.example', ' ', 'http://b.example', 'https://c.example', 'https://d.example', 'https://e.example'] }));
  assert.ok(v.row, v.error);
  assert.equal(v.row.edition, 'both');
  assert.equal(v.row.links.length, 5);
});

test('the per-IP rate limit returns 429 after 5 in an hour', async () => {
  const fetchImpl = async (url, init) => {
    if (init.method === 'GET') return { ok: true, json: async () => [1, 2, 3, 4, 5].map((i) => ({ id: String(i) })) };
    throw new Error('must not insert');
  };
  const { res, calls } = await call(good(), { fetchImpl });
  assert.equal(res.statusCode, 429);
  assert.equal(calls.length, 1);
  assert.match(calls[0].url, /ip_hash=eq\.[0-9a-f]{64}/);
  assert.ok(!calls[0].url.includes('203.0.113.9'), 'the raw IP never leaves the function');
});

test('a failed rate-limit read does not block, a failed insert is a 502 with no rows', async () => {
  const fetchImpl = async (url, init) => {
    if (init.method === 'GET') return { ok: false, json: async () => ({}) };
    return { ok: false, json: async () => ({ message: 'secret detail' }) };
  };
  const { res, out } = await call(good(), { fetchImpl });
  assert.equal(res.statusCode, 502);
  assert.equal(out.ok, false);
  assert.ok(!res.body.includes('secret detail'));
});

test('missing Supabase env is a 503, not a crash', async () => {
  const { res } = await call(good(), { env: { NEWSLETTER_CONTRIB_CODES: CODE } });
  assert.equal(res.statusCode, 503);
});

test('a string body (no JSON parser upstream) is parsed', async () => {
  const { res } = await call(JSON.stringify(good()));
  assert.equal(res.statusCode, 200);
});

test('issue month is the Denver month, or next month from the 26th', () => {
  assert.equal(issueMonth(new Date('2026-11-09T18:00:00Z')), '2026-11');
  assert.equal(issueMonth(new Date('2026-11-25T18:00:00Z')), '2026-11');
  assert.equal(issueMonth(new Date('2026-11-26T18:00:00Z')), '2026-12');
  assert.equal(issueMonth(new Date('2026-12-28T12:00:00Z')), '2027-01');
  // 2026-12-01 03:00 UTC is still Nov 30 in Denver
  assert.equal(issueMonth(new Date('2026-12-01T03:00:00Z')), '2026-12');
  assert.equal(issueMonth(new Date('2026-11-26T05:00:00Z')), '2026-11');
});

test('codeOk matches exactly and trims the submitted code', () => {
  assert.equal(codeOk(`  ${CODE} `, `a,${CODE}`), true);
  assert.equal(codeOk(CODE.toUpperCase(), CODE), false);
  assert.equal(codeOk(null, CODE), false);
});

test('a POST without consent true is refused before the database', async () => {
  for (const consent of [undefined, false, 'true', 1, null]) {
    const { res, out, calls } = await call(good({ consent }));
    assert.equal(res.statusCode, 400, String(consent));
    assert.equal(out.ok, false);
    assert.match(out.error, /Tick the box/);
    assert.equal(calls.length, 0);
  }
});

test('links to loopback, LAN, tailnet or bare IP hosts are refused', () => {
  for (const l of ['http://127.0.0.1:9333/json', 'http://localhost/', 'http://100.100.100.100/',
    'http://10.0.0.5/', 'http://192.168.1.1/', 'http://[::1]/', 'http://mini.tail1234.ts.net/',
    'http://printer.local/', 'http://db.internal/', 'http://router.lan/', 'http://nas.home.arpa/',
    'http://0x7f000001/', 'http://2130706433/', 'http://intranet/', 'https://user:pw@example.com/']) {
    const v = validate(good({ links: [l] }));
    assert.equal(v.error, 'Each link must be a full http or https address.', l);
  }
  assert.ok(validate(good({ links: ['https://github.com/a/b', 'http://example.org/x'] })).row);
});
