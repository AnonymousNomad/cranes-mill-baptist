# Cranes Mill Baptist Church build notes

## Current state

The original one-file landing-page demo has been split into a responsive public site and a local SQLite-backed content service. The main route is a single-page experience with hash-based views for Home, About, Ministries, Sermons, Events, Give, and Contact. The events view contains the separate month calendar requested by Odinn.

## Content boundaries

- The `church/` directory is the supplied source-of-truth media folder.
- Gallery images are discovered at runtime and served through `/api/gallery`.
- Site settings, ministries, sermons, events, and prayer requests are durable SQLite records.
- Public data is readable without credentials; content creation requires `CHURCH_ADMIN_TOKEN`.
- The private workspace can update site settings and add ministries, sermons, and events; prayer requests remain read-only there.
- Prayer requests are readable only through the token-protected content workspace.
- Seed content is explicitly starter content and requires church confirmation.
- The home layout is intentionally photo-led: hero slideshow, quick links, welcome panel, image-backed event cards, connection cards, then the light footer.
- Footer social URLs are stored in `site_settings`; Facebook is the only verified active link until the church supplies Instagram and YouTube URLs.
- Decorative crosses are CSS-only, pointer-safe, and motion-reduced when the visitor requests reduced motion.
- The current visual pass uses near-white paper surfaces, pale-gold alternate surfaces, gold trim, and a deep-navy footer.
- White theme accents are intentionally pale blue; navy remains reserved for contrast sections and the hero overlay.
- The footer reverses to deep navy so the pale-blue text and gold social pills have clear contrast.
- The gallery heading uses layered CSS banner plates with perspective, trim, depth shadows, and a lower dimensional edge.
- The home events band uses the same banner language, with staggered card perspective that flattens on mobile.
- The events band now uses a cinematic navy/gold treatment with decorative atmosphere, raised image cards, and CSS calendar medallions.
- Hero, gallery, and events display headings use a deliberate CSS extrusion stack with bright faces, gold edge depth, perspective, and cast shadows so the typography presents as raised signage.
- The global theme carries that navy, pale-blue, and gold cinematic treatment through light sections, inner views, cards, controls, and footer surfaces.
- Desktop hero copy is intentionally left-weighted to match the supplied composition; mobile keeps the centered shell spacing.
- The home hero defaults to the cinematic landscape in `assets/hero/` (carved CRANES MILL scene). Hero controls can still reveal church gallery photos as an overlay; returning to Scene restores the landscape.
- Hero video looping was requested but blocked under zero-data-retention; Ken Burns CSS motion is the current living-scene substitute.
- Site music tracks are SQLite-backed (`music_tracks`). Publish them from `/admin.html` with a local path like `/church/song.mp3` or `/assets/music/...`, or an https URL. The floating player stays hidden until at least one valid track exists, tries autoplay on load, and falls back to tap-to-play when the browser blocks sound.
- Inner views (About, Ministries, Sermons, Events, Give, Contact) share the home cinematic language: atmospheric navy washes, gold banner labels, display-3d headings, and raised gold-edged cards/panels.

## Verification boundary

Local structural checks and the standard-library test suite are the evidence in this checkout. No hosted deployment, production database, administrator credential, media-rights review, or church acceptance test has been performed. Do not describe this module as live, released, or complete until Odinn signs off.
