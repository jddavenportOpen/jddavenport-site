// Google Calendar booking core. Zero external dependencies (Node 18+ global fetch).
// Auth: OAuth refresh token for jddavenport46@gmail.com with calendar scope,
// stored as BOOKING_GOOGLE_* env vars on the Vercel project.
// Privacy contract: nothing in this module ever returns event titles, attendees,
// or any calendar detail to the visitor. Only free/busy derived open slots.

const CONFIG = {
  timezone: 'America/Denver',
  weekdays: [1, 2, 3, 4, 5], // Mon-Fri (0 = Sunday)
  startHour: 9,
  endHour: 17,
  durationMinutes: 30,
  slotStepMinutes: 30,
  bufferMinutes: 10,   // padding around existing busy blocks
  minNoticeHours: 4,
  maxDaysAhead: 14,
};

// ---------- OAuth ----------

let cachedToken = null; // { accessToken, expiresAt }

async function getAccessToken() {
  if (cachedToken && Date.now() < cachedToken.expiresAt - 60_000) {
    return cachedToken.accessToken;
  }
  const clientId = process.env.BOOKING_GOOGLE_CLIENT_ID;
  const clientSecret = process.env.BOOKING_GOOGLE_CLIENT_SECRET;
  const refreshToken = process.env.BOOKING_GOOGLE_REFRESH_TOKEN;
  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error('booking_not_configured');
  }
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });
  const data = await res.json();
  if (!data.access_token) {
    throw new Error('oauth_refresh_failed: ' + (data.error || 'unknown'));
  }
  cachedToken = {
    accessToken: data.access_token,
    expiresAt: Date.now() + (data.expires_in || 3600) * 1000,
  };
  return cachedToken.accessToken;
}

// ---------- Timezone math (DST-safe, no deps) ----------

function tzOffsetMs(date, tz) {
  const dtf = new Intl.DateTimeFormat('en-US', {
    timeZone: tz, hour12: false,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
  const p = Object.fromEntries(dtf.formatToParts(date).map((x) => [x.type, x.value]));
  const asUTC = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second);
  return asUTC - date.getTime();
}

// Convert wall-clock (dateStr 'YYYY-MM-DD', h:m in tz) to a UTC Date. Two-pass for DST edges.
function zonedToUtc(dateStr, h, m, tz) {
  const [y, mo, d] = dateStr.split('-').map(Number);
  const guess = new Date(Date.UTC(y, mo - 1, d, h, m, 0));
  const off1 = tzOffsetMs(guess, tz);
  const result = new Date(guess.getTime() - off1);
  const off2 = tzOffsetMs(result, tz);
  return new Date(guess.getTime() - off2);
}

function dateStrInTz(date, tz) {
  const dtf = new Intl.DateTimeFormat('en-CA', {
    timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
  });
  return dtf.format(date); // YYYY-MM-DD
}

function weekdayOfDateStr(dateStr) {
  const [y, mo, d] = dateStr.split('-').map(Number);
  return new Date(Date.UTC(y, mo - 1, d)).getUTCDay();
}

function addDaysToDateStr(dateStr, days) {
  const [y, mo, d] = dateStr.split('-').map(Number);
  const dt = new Date(Date.UTC(y, mo - 1, d + days));
  return dt.toISOString().slice(0, 10);
}

// ---------- Calendar API ----------

async function getBusyPeriods(timeMinIso, timeMaxIso) {
  const token = await getAccessToken();
  const res = await fetch('https://www.googleapis.com/calendar/v3/freeBusy', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ timeMin: timeMinIso, timeMax: timeMaxIso, items: [{ id: 'primary' }] }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error('freebusy_failed: ' + JSON.stringify(data.error || data).slice(0, 200));
  const busy = (data.calendars && data.calendars.primary && data.calendars.primary.busy) || [];
  return busy.map((b) => ({ start: new Date(b.start).getTime(), end: new Date(b.end).getTime() }));
}

async function hasUpcomingBookingForEmail(email) {
  const token = await getAccessToken();
  const params = new URLSearchParams({
    privateExtendedProperty: `jdbook_guest=${email.toLowerCase()}`,
    timeMin: new Date().toISOString(),
    singleEvents: 'true',
    maxResults: '1',
  });
  const res = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/primary/events?${params}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  const data = await res.json();
  if (!res.ok) throw new Error('events_list_failed');
  return (data.items || []).length > 0;
}

async function createBookingEvent({ startIso, name, email, notes }) {
  const token = await getAccessToken();
  const start = new Date(startIso);
  const end = new Date(start.getTime() + CONFIG.durationMinutes * 60_000);
  const body = {
    summary: `JD x ${name} (intro call)`,
    description:
      `Booked via jddavenport.com/book\n\nName: ${name}\nEmail: ${email}` +
      (notes ? `\nContext: ${notes}` : ''),
    start: { dateTime: start.toISOString(), timeZone: CONFIG.timezone },
    end: { dateTime: end.toISOString(), timeZone: CONFIG.timezone },
    attendees: [{ email }],
    reminders: { useDefault: true },
    extendedProperties: { private: { jdbook_guest: email.toLowerCase(), jdbook_source: 'jddavenport.com' } },
    conferenceData: {
      createRequest: {
        requestId: 'jdbook-' + Math.random().toString(36).slice(2, 12),
        conferenceSolutionKey: { type: 'hangoutsMeet' },
      },
    },
  };
  const res = await fetch(
    'https://www.googleapis.com/calendar/v3/calendars/primary/events?sendUpdates=all&conferenceDataVersion=1',
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }
  );
  const data = await res.json();
  if (!res.ok) throw new Error('event_insert_failed: ' + JSON.stringify(data.error || data).slice(0, 200));
  return { id: data.id, meetLink: data.hangoutLink || null };
}

// ---------- Slot computation ----------

function computeSlotsForRange(busy, todayStr, nowMs) {
  const tz = CONFIG.timezone;
  const minStartMs = nowMs + CONFIG.minNoticeHours * 3600_000;
  const days = [];
  for (let i = 0; i <= CONFIG.maxDaysAhead; i++) {
    const dateStr = addDaysToDateStr(todayStr, i);
    if (!CONFIG.weekdays.includes(weekdayOfDateStr(dateStr))) continue;
    const dayStart = zonedToUtc(dateStr, CONFIG.startHour, 0, tz).getTime();
    const dayEnd = zonedToUtc(dateStr, CONFIG.endHour, 0, tz).getTime();
    const slots = [];
    for (let t = dayStart; t + CONFIG.durationMinutes * 60_000 <= dayEnd; t += CONFIG.slotStepMinutes * 60_000) {
      if (t < minStartMs) continue;
      const slotStart = t - CONFIG.bufferMinutes * 60_000;
      const slotEnd = t + (CONFIG.durationMinutes + CONFIG.bufferMinutes) * 60_000;
      const conflict = busy.some((b) => slotStart < b.end && slotEnd > b.start);
      if (!conflict) slots.push(new Date(t).toISOString());
    }
    days.push({ date: dateStr, slots });
  }
  return days;
}

async function getAvailability() {
  const tz = CONFIG.timezone;
  const now = new Date();
  const todayStr = dateStrInTz(now, tz);
  const rangeStart = zonedToUtc(todayStr, 0, 0, tz);
  const rangeEndStr = addDaysToDateStr(todayStr, CONFIG.maxDaysAhead + 1);
  const rangeEnd = zonedToUtc(rangeEndStr, 0, 0, tz);
  const busy = await getBusyPeriods(rangeStart.toISOString(), rangeEnd.toISOString());
  return computeSlotsForRange(busy, todayStr, now.getTime());
}

// A slot is bookable only if it appears in a fresh availability computation.
async function isSlotAvailable(startIso) {
  const days = await getAvailability();
  const target = new Date(startIso).toISOString();
  return days.some((d) => d.slots.includes(target));
}

module.exports = {
  CONFIG,
  getAvailability,
  isSlotAvailable,
  hasUpcomingBookingForEmail,
  createBookingEvent,
};
