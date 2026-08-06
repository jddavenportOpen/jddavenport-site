// GET /api/book-slots
// Returns open 30-minute slots for the next two weeks, computed from
// Google Calendar free/busy. Never exposes event details, only open times.

const { getAvailability, CONFIG } = require('./lib/google-booking');

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  try {
    const days = await getAvailability();
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=120');
    return res.status(200).json({
      timezone: CONFIG.timezone,
      duration_minutes: CONFIG.durationMinutes,
      days,
    });
  } catch (err) {
    console.error('[book-slots]', err.message);
    const notConfigured = err.message === 'booking_not_configured';
    return res.status(notConfigured ? 503 : 500).json({
      error: notConfigured
        ? 'Booking is not configured yet.'
        : 'Could not load availability. Try again in a minute.',
    });
  }
};
