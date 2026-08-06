// POST /api/book-create
// Creates the meeting: validates the slot server-side against live free/busy,
// enforces one upcoming booking per email, then inserts a Google Calendar
// event with the guest as attendee. Google sends the invite email with the
// Meet link to both sides, so no separate email service is needed.

const {
  isSlotAvailable,
  hasUpcomingBookingForEmail,
  createBookingEvent,
  CONFIG,
} = require('./lib/google-booking');

// Best-effort per-IP throttle (survives warm invocations, resets on cold start).
const ipHits = new Map();
function throttled(ip) {
  const now = Date.now();
  const hits = (ipHits.get(ip) || []).filter((t) => now - t < 60_000);
  hits.push(now);
  ipHits.set(ip, hits);
  return hits.length > 8;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (throttled(ip)) {
    return res.status(429).json({ error: 'Too many requests. Slow down and try again.' });
  }

  try {
    const body = req.body || {};
    const name = String(body.name || '').trim().slice(0, 100);
    const email = String(body.email || '').trim().toLowerCase().slice(0, 200);
    const notes = String(body.notes || '').trim().slice(0, 500);
    const start = String(body.start || '').trim();
    const honeypot = String(body.company_website || '').trim();

    // Bots fill hidden fields. Pretend it worked.
    if (honeypot) {
      return res.status(200).json({ ok: true });
    }

    if (!name || name.length < 2) {
      return res.status(400).json({ error: 'Please enter your name.' });
    }
    if (!EMAIL_RE.test(email)) {
      return res.status(400).json({ error: 'Please enter a valid email.' });
    }
    const startDate = new Date(start);
    if (!start || isNaN(startDate.getTime())) {
      return res.status(400).json({ error: 'Invalid time selected.' });
    }
    const maxAheadMs = (CONFIG.maxDaysAhead + 2) * 86_400_000;
    if (startDate.getTime() < Date.now() || startDate.getTime() > Date.now() + maxAheadMs) {
      return res.status(400).json({ error: 'That time is outside the booking window.' });
    }

    // One upcoming meeting per email. Keeps the calendar honest.
    if (await hasUpcomingBookingForEmail(email)) {
      return res.status(409).json({
        error: 'You already have an upcoming meeting booked. Need to change it? Email jddavenport46@gmail.com.',
      });
    }

    // Re-verify against live free/busy so a stale page cannot double-book.
    if (!(await isSlotAvailable(startDate.toISOString()))) {
      return res.status(409).json({ error: 'That slot was just taken. Pick another time.' });
    }

    const event = await createBookingEvent({
      startIso: startDate.toISOString(),
      name,
      email,
      notes,
    });

    return res.status(200).json({
      ok: true,
      start: startDate.toISOString(),
      duration_minutes: CONFIG.durationMinutes,
      meet_link: event.meetLink,
    });
  } catch (err) {
    console.error('[book-create]', err.message);
    const notConfigured = err.message === 'booking_not_configured';
    return res.status(notConfigured ? 503 : 500).json({
      error: notConfigured
        ? 'Booking is not configured yet.'
        : 'Something went wrong creating the meeting. Try again, or email jddavenport46@gmail.com.',
    });
  }
};
