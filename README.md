# jddavenport.com

Source for my personal site — [jddavenport.com](https://jddavenport.com).

Static HTML + CSS, no build step, deployed on Vercel. The only dynamic part is
the `/book` page, which talks to two serverless functions that read my Google
Calendar for real availability and write the meeting back.

## Layout

```
index.html          landing page
book.html           /book  — self-serve scheduling UI
teardown.html       /teardown — writeup
resume.pdf          /resume.pdf
vercel.json         rewrites (/book, /teardown) — no build command, output is the repo root
images/, public/    headshot, OG image, build screenshots
api/
  book-slots.js     GET  — free/busy → open slots
  book-create.js    POST — creates the calendar event + sends confirmation
  lib/
    google-booking.js  Google Calendar OAuth + free/busy
    smtp.js            minimal SMTP client for the confirmation email
```

## Running it

```bash
npm i -g vercel
vercel dev
```

The booking functions need three environment variables — a Google OAuth client
with the Calendar scope, plus a refresh token for the calendar you want to book
against:

```
BOOKING_GOOGLE_CLIENT_ID=
BOOKING_GOOGLE_CLIENT_SECRET=
BOOKING_GOOGLE_REFRESH_TOKEN=
```

The rest of the site is static — open `index.html` directly if you only care
about the pages.

## Related

- [bookjd](https://github.com/jddavenportOpen/bookjd) — the standalone,
  self-hostable version of the booking app (Next.js + Supabase + Stripe). This
  repo has the lightweight in-page version; `bookjd` is the full product.

## License

MIT
