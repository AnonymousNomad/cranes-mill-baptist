# Cranes Mill Baptist Church

> Faith on the Lake. A single-page landing site for Cranes Mill Baptist Church, Canyon Lake, TX.

Live at: https://anonymousnomad.github.io/cranes-mill-baptist/

A beautiful, responsive, accessible landing page for Cranes Mill Baptist Church — a Bible-believing congregation on the shores of Canyon Lake, Texas. This is a **design showcase / demo** for the church to review.

## Who it's for

- **The church** — a polished, honest web presence to share with Canyon Lake.
- **Visitors** — clear service times, directions, ministries, and a warm welcome in seconds.

## Stack

- Plain HTML5 + CSS custom properties (no framework, no build step, no bundler)
- Vanilla JS for mobile nav, scroll-reveal, smooth anchors
- Google Maps embed (lazy-loaded, no cookie wall)
- 100% static — hosts on any static server, including GitHub Pages

## Sections

1. Hero — "Faith on the Lake," service-time snapshot, visit CTAs
2. About — who we are, Matthew 28:19, guiding values
3. Service Times — Sunday + Wednesday schedule, directions link
4. Ministries — Sunday School, Worship, Fellowship, Youth, Children, Parents Night Out
5. Community — CRRC Meals on Wheels, Family Promise, One Day Academy partnerships
6. Contact — address, phone, email, Facebook, interactive map
7. Footer

## Pages

- `/` — `index.html` (single page)

## Design system

- **Palette:** deep navy `#1B2A4A`, warm gold `#C9A84C`, sky blue `#6BA3BE`, warm cream `#FBF8F1`
- **Type:** Georgia (headings) + system UI stack (body)
- **Motion:** scroll-reveal via IntersectionObserver; respects `prefers-reduced-motion`
- **A11y:** skip-link, `aria-label`/`aria-controls`/`aria-expanded`, `:focus-visible` rings, WCAG-conscious contrast on dark sections

## Local preview

```bash
# From this directory:
python3 -m http.server 4173
# or
npx --yes serve@latest -l 4173
```

Open http://127.0.0.1:4173/

## Roadmap (if the church wants to go further)

- Contact form / prayer request
- Sermon archive (YouTube/Facebook embed)
- Events calendar
- Photo gallery of the congregation and the lake
- Give page

## License

MIT. See [LICENSE](./LICENSE).

## Contact

- Cranes Mill Baptist Church: (830) 899-7936 · cmbccl@gvtc.com · 10215 FM 2673, Canyon Lake, TX 78133
- Facebook: [@CMBCCL](https://www.facebook.com/CMBCCL/)
- Property of the church; maintained by [AnonymousNomad](https://github.com/AnonymousNomad).