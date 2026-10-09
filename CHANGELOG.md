# Changelog

## 2026-10-08

- Cleaned ship package: removed cache files and unused hero reference assets; refreshed README run instructions for reviewers.
- Synced About, Ministries, Sermons, Events, Give, and Contact with the home cinematic treatment: atmospheric backgrounds, carved display titles, gold banner labels, and raised 3D cards/panels.
- Added a floating site music player with public `/api/music`, admin publishing for tracks, autoplay-with-click fallback, and local demo audio at `/assets/music/welcome.mp3`.
- Rebuilt the home hero as a full-viewport cinematic landscape with carved stone CRANES MILL lettering, Ken Burns motion, mist/glow atmosphere, and a glass call-to-action panel.
- Deepened immersive 3D treatment across quick links, welcome imagery, feature cards, gallery tiles, and section banners while keeping church photo browsing available from the hero controls.
- Replaced the original single-file demo with a mobile-first multi-view church site matching the supplied visual direction.
- Added hero photo rotation, responsive family gallery, About, Ministries, Sermons, Events, Give, and Contact views.
- Added a separate month calendar with event list and month navigation.
- Added Python standard-library server with bounded JSON input, path traversal refusal, symlink escape refusal, no-store JSON responses, and same-origin static serving.
- Added SQLite persistence for sermons, events, and prayer requests with private-token-protected content creation routes.
- Preserved the supplied `church/` media directory and added the private content workspace at `/admin.html`.
- Added structural and API tests. Hosted deployment, final church content, media-rights review, and Odinn sign-off remain pending.
- Extended the hero into an autoplaying slideshow over all browser-ready gallery images with pause controls and added an accessible photo viewer for the full set.
- Added authorized prayer-request listing to the private content workspace and explicit unavailable responses for read failures.
- Added durable site settings and ministry records, public `/api/site` content loading, and authenticated admin forms for updating site details and adding ministry cards.
- Added safe media URL validation, inline MP4 playback for local sermon records, event time/location details in visitor views, and SQLite indexes for the archive and calendar sort paths.
- Reworked the home experience around the supplied mobile-first reference: added Sermons, Prayer Requests, and Get Involved feature cards with responsive imagery and navigation.
- Tuned the feature-card layout for tablet and mobile breakpoints, preserved the 66 browser-ready image slideshow, and escaped gallery image URLs before rendering.
- Updated the seeded welcome heading to use the church name in the welcome panel.
- Corrected endpoint failure states so service errors remain visible after fallback rendering, and applied the same media guard to ministry card images.
- Refined the home page to follow the supplied reference sequence with a Canyon Lake location cue, photo-backed event cards, a simpler connection-card section, and a light footer.
- Prioritized the supplied church exterior as the first hero slide without changing the source media inventory.
- Added a flexbox footer social group with a verified Facebook link, database-backed Instagram and YouTube slots, accessible SVG icons, pill buttons, and a soft glow/lift hover treatment.
- Added three subtle CSS 3D cross forms that drift at different page positions without covering or intercepting content.
- Warmed the light surfaces to pale gold, strengthened gold trim across cards and controls, and added multi-step drift-and-bounce motion to the floating crosses.
- Changed the remaining paper-white surface layer to pale blue so the light theme balances the gold surfaces and trim.
- Replaced the remaining white text and translucent accents with pale blue so the entire light palette stays consistent.
- Deepened the pale-blue paper layer so the quick-link banner, gallery, and footer no longer read as white on screen.
- Restored near-white paper surfaces and changed the footer to deep navy with pale-blue text and gold social pills.
- Added layered 3D banner treatments to the gallery label, heading, and supporting copy.
- Extended the dimensional banner treatment to Upcoming Events and added staggered perspective, shadow depth, and hover lift to event cards.
- Rebuilt the events band toward the supplied cinematic reference with navy atmosphere, split gold typography, glowing CTA treatment, larger raised cards, and calendar medallions.
- Added high-contrast display lettering with ivory and gold faces, layered bronze extrusion, bevel highlights, perspective tilt, and cast shadows for the hero and major banner headings.
- Extended the cinematic navy/gold/pale-blue treatment across the complete page theme, including quick links, welcome, gallery, feature cards, content views, forms, and navigation surfaces.
- Repositioned the desktop hero copy to the left side of the viewport so the large open space no longer sits beside the message.
