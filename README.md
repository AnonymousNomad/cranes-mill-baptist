# Cranes Mill Baptist Church

Responsive church website for Cranes Mill Baptist Church in Canyon Lake, Texas.

Includes a cinematic home hero, photo gallery, ministries, sermons, events calendar, giving page, contact/prayer form, floating music player, and a private admin workspace.

## Run locally

Python 3 only. No extra packages required.

```bash
cd cranes-mill-baptist-master
CHURCH_ADMIN_TOKEN='set-a-local-token' python3 server.py
```

Then open:

- Public site: http://127.0.0.1:4173/
- Admin workspace: http://127.0.0.1:4173/admin.html

Use the same `CHURCH_ADMIN_TOKEN` value to unlock publishing forms in admin.

Optional env vars (see `.env.example`):

- `CHURCH_HOST` (default `127.0.0.1`)
- `CHURCH_PORT` (default `4173`)
- `CHURCH_DB_PATH` (default `data/church.sqlite3`)

## What reviewers should check

- Home hero landscape, carved CRANES MILL framing, and quick links
- About, Ministries, Sermons, Events, Give, Contact pages
- Gallery lightbox
- Floating music player (add more tracks in admin under **Add site music**)
- Admin: site details, sermons, events, ministries, music, prayer inbox

## Admin media tips

- Local media paths work, for example `/church/your-photo.jpg` or `/assets/music/welcome.mp3`
- Full `https://...` URLs also work for images/audio/video
- Place audio files in `church/` or `assets/music/`, then publish the path from admin

## Tests

```bash
python3 -m unittest discover -s tests -q
python3 scripts/check_site.py
```

## Notes before public launch

Confirm worship times, phone, email, giving workflow, media rights, and calendar dates with the church. The included SQLite file under `data/` is local starter content and can be deleted to regenerate a fresh database on next server start.
