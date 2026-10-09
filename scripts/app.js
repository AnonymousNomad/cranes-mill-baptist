const state = {
  site: {},
  ministries: [],
  gallery: [],
  sermons: [],
  events: [],
  music: [],
  musicIndex: 0,
  heroItems: [],
  slideIndex: 0,
  galleryIndex: 0,
  slideTimer: null,
  calendarDate: new Date(),
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const fallbackGallery = [
  { name: 'chuech pic.jpg', url: '/church/chuech%20pic.jpg' },
  { name: '20260913_104642.jpg', url: '/church/20260913_104642.jpg' },
  { name: '20260913_104717.jpg', url: '/church/20260913_104717.jpg' },
  { name: '20260913_105819.jpg', url: '/church/20260913_105819.jpg' },
  { name: '20260913_111313.jpg', url: '/church/20260913_111313.jpg' },
  { name: 'IMG_20260902_151936.jpg', url: '/church/IMG_20260902_151936.jpg' },
];
const fallbackSite = {
  address: '10215 FM 2673, Canyon Lake, TX 78133',
  phone: '(830) 899-7936',
  email: 'cmbccl@gvtc.com',
  facebook_url: 'https://www.facebook.com/CMBCCL/',
  instagram_url: '',
  youtube_url: 'https://www.youtube.com/@cranesmillbaptistchurch2673',
  worship_time: 'Sunday worship · 11:00 AM',
  welcome_heading: 'A church that feels like home.',
  welcome_body: "We exist to glorify God, make disciples, and serve our community. At Cranes Mill, you'll find a place to belong, a family to grow with, and a church that cares about Canyon Lake and beyond.",
  giving_body: 'For the current giving options, please contact the church office. We will make sure your gift reaches the right ministry.',
};

async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(path, { ...options, signal: controller.signal, headers: { Accept: 'application/json', ...options.headers } });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

function dateValue(value) {
  return new Date(`${value}T12:00:00`);
}

function formatDate(value, options = { month: 'short', day: 'numeric', year: 'numeric' }) {
  return dateValue(value).toLocaleDateString('en-US', options);
}

function routeFromHash() {
  const route = window.location.hash.replace('#', '');
  return ['home', 'about', 'ministries', 'sermons', 'events', 'give', 'contact'].includes(route) ? route : 'home';
}

function setView(view, updateHistory = true) {
  $$('[data-view]').forEach((panel) => { panel.hidden = panel.dataset.view !== view; });
  $$('[data-route]').forEach((link) => { link.setAttribute('aria-current', link.dataset.route === view ? 'page' : 'false'); });
  if (updateHistory && routeFromHash() !== view) window.history.pushState({}, '', `#${view}`);
  document.title = view === 'home' ? 'Cranes Mill Baptist Church | Canyon Lake, Texas' : `${view[0].toUpperCase()}${view.slice(1)} | Cranes Mill Baptist Church`;
  closeMenu();
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (view === 'events') renderCalendar();
}

function closeMenu() {
  $('#site-nav').classList.remove('open');
  $('.menu-toggle').setAttribute('aria-expanded', 'false');
  document.body.classList.remove('menu-open');
}

function phoneHref(phone) {
  return `tel:${String(phone || '').replace(/[^\d+]/g, '')}`;
}

function safeMediaUrl(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  if (text.startsWith('/') && !text.startsWith('//')) return text;
  try {
    const parsed = new URL(text, window.location.origin);
    return ['http:', 'https:'].includes(parsed.protocol) ? text : '';
  } catch (error) {
    return '';
  }
}

function safeExternalUrl(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  try {
    const parsed = new URL(text);
    return ['http:', 'https:'].includes(parsed.protocol) ? text : '';
  } catch (error) {
    return '';
  }
}

const socialPlatforms = [
  { key: 'facebook_url', label: 'Facebook', icon: '<path d="M14.5 8H17V5h-2.5C12 5 11 6.5 11 8.7V11H9v3h2v5h3v-5h2.5l.5-3H14v-1.8c0-.8.2-1.2.5-1.2Z"/>' },
  { key: 'instagram_url', label: 'Instagram', icon: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>' },
  { key: 'youtube_url', label: 'YouTube', icon: '<path d="M21.6 7.2a2.8 2.8 0 0 0-2-2C17.8 4.7 12 4.7 12 4.7s-5.8 0-7.6.5a2.8 2.8 0 0 0-2 2C2 9 2 12 2 12s0 3 .4 4.8a2.8 2.8 0 0 0 2 2c1.8.5 7.6.5 7.6.5s5.8 0 7.6-.5a2.8 2.8 0 0 0 2-2C22 15 22 12 22 12s0-3-.4-4.8ZM10 15.5v-7l6 3.5-6 3.5Z"/>' },
];

function socialIcon(platform) {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">${platform.icon}</svg>`;
}

function renderSocialLinks(site = state.site) {
  const target = $('#social-links');
  if (!target) return;
  target.innerHTML = socialPlatforms.map((platform) => {
    const href = safeExternalUrl(site[platform.key]);
    const label = `<span class="social-label">${platform.label}</span>`;
    if (!href) return `<span class="social-link is-disabled" aria-disabled="true" title="Add a ${platform.label} URL in the content workspace">${socialIcon(platform)}${label}</span>`;
    return `<a class="social-link" href="${escapeHtml(href)}" target="_blank" rel="noreferrer" aria-label="Cranes Mill Baptist Church on ${platform.label}">${socialIcon(platform)}${label}</a>`;
  }).join('');
}

function renderSiteContent() {
  const site = { ...fallbackSite, ...state.site };
  $('#welcome-heading').textContent = site.welcome_heading || fallbackSite.welcome_heading;
  $('#welcome-body').textContent = site.welcome_body;
  $('#giving-body').textContent = site.giving_body;
  $('#site-address').textContent = site.address;
  $('#site-phone').textContent = site.phone;
  $('#site-phone').href = phoneHref(site.phone);
  $('#site-email').textContent = site.email;
  $('#site-email').href = `mailto:${site.email}`;
  $('#site-worship-time').textContent = site.worship_time;
  $('#footer-address').textContent = site.address;
  $('#footer-phone').textContent = site.phone;
  $('#footer-phone').href = phoneHref(site.phone);
  $('#footer-email').textContent = site.email;
  $('#footer-email').href = `mailto:${site.email}`;
  const youtubeLink = $('#youtube-channel-link');
  const youtubeUrl = safeExternalUrl(site.youtube_url) || fallbackSite.youtube_url;
  if (youtubeLink && youtubeUrl) {
    youtubeLink.href = youtubeUrl.includes('/videos') ? youtubeUrl : `${youtubeUrl.replace(/\/$/, '')}/videos`;
  }
  renderSocialLinks(site);
}

function renderMinistries() {
  const target = $('#ministry-list');
  if (!state.ministries.length) { target.innerHTML = '<div class="empty-state">Ministry details will be added soon.</div>'; return; }
  target.innerHTML = state.ministries.map((ministry, index) => {
    const imageUrl = safeMediaUrl(ministry.image_url);
    const route = ministry.action_route || 'contact';
    return `<article class="ministry-card">${imageUrl ? `<img class="ministry-image" src="${escapeHtml(imageUrl)}" alt="" loading="lazy" />` : ''}<h2>${escapeHtml(ministry.title)}</h2><p>${escapeHtml(ministry.summary)}</p><a class="text-link" href="#${escapeHtml(route)}" data-route="${escapeHtml(route)}">${escapeHtml(ministry.action_label || 'Learn more')} <span aria-hidden="true">→</span></a></article>`;
  }).join('');
}

function galleryPhotos() {
  return state.gallery.filter((item) => item.url).length ? state.gallery.filter((item) => item.url) : fallbackGallery;
}

function renderHero() {
  // Top hero stays a static sunrise image. Keep empty slideshow node for contract.
  state.heroItems = [];
  const heroShow = $('#hero-slideshow');
  if (heroShow) heroShow.innerHTML = '';
  stopSlideShow();
  renderWelcomeSlideshow();
}

function renderWelcomeSlideshow() {
  const photos = galleryPhotos();
  const preferred = photos.find((item) => item.name.toLowerCase() === 'chuech pic.jpg');
  state.heroItems = preferred ? [preferred, ...photos.filter((item) => item !== preferred)] : photos;
  const target = $('#welcome-slideshow');
  if (!target) return;
  target.innerHTML = '<div class="welcome-slide active" id="welcome-slide-image"></div>';
  applyWelcomeSlide(0);
  startSlideShow();
}

function applyWelcomeSlide(index) {
  if (!state.heroItems.length) return;
  state.slideIndex = (index + state.heroItems.length) % state.heroItems.length;
  const item = state.heroItems[state.slideIndex];
  const slide = $('#welcome-slide-image');
  if (!slide) return;
  slide.style.backgroundImage = `url("${item.url}")`;
  const status = $('#welcome-slide-status');
  if (status) status.textContent = `${state.slideIndex + 1} / ${state.heroItems.length}`;
}

function changeSlide(direction) {
  if (state.heroItems.length < 2) return;
  applyWelcomeSlide(state.slideIndex + direction);
}

function startSlideShow() {
  clearInterval(state.slideTimer);
  if (state.heroItems.length < 2) return;
  state.slideTimer = setInterval(() => changeSlide(1), 7000);
}

function stopSlideShow() {
  clearInterval(state.slideTimer);
}

function renderHomeEvents() {
  const target = $('#home-events');
  const events = state.events.filter((event) => dateValue(event.event_date) >= new Date()).slice(0, 3);
  const images = state.gallery.filter((item) => item.url).length ? state.gallery.filter((item) => item.url) : fallbackGallery;
  target.innerHTML = events.length ? events.map((event, index) => {
    const image = images[index % images.length];
    return `<article class="event-card"><img class="event-card-image" src="${escapeHtml(image.url)}" alt="" loading="lazy" /><div class="event-card-body"><time datetime="${escapeHtml(event.event_date)}">${formatDate(event.event_date, { month: 'short', day: 'numeric' })}</time><h3>${escapeHtml(event.title)}</h3><p>${escapeHtml([event.event_time, event.location || 'Cranes Mill Baptist Church'].filter(Boolean).join(' · '))}</p><span class="event-card-icon" aria-hidden="true"></span></div></article>`;
  }).join('') : '<div class="empty-state">The latest events will appear here soon.</div>';
}

function renderGallery() {
  const items = (state.gallery.filter((item) => item.url).length ? state.gallery.filter((item) => item.url) : fallbackGallery).slice(0, 8);
  $('#gallery-grid').innerHTML = items.map((item, index) => `<button class="gallery-item" type="button" data-gallery-index="${index}" aria-label="Open photo ${index + 1}"><img src="${escapeHtml(item.url)}" alt="Cranes Mill church life photo ${index + 1}" loading="lazy" /></button>`).join('');
}

function showGallery(index) {
  const items = state.gallery.filter((item) => item.url).length ? state.gallery.filter((item) => item.url) : fallbackGallery;
  state.galleryIndex = (index + items.length) % items.length;
  const item = items[state.galleryIndex];
  $('#gallery-dialog-image').src = item.url;
  $('#gallery-dialog-image').alt = `Cranes Mill church life photo ${state.galleryIndex + 1}`;
  $('#gallery-dialog-caption').textContent = `${state.galleryIndex + 1} of ${items.length} · ${item.name.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ')}`;
  const dialog = $('#gallery-dialog');
  if (typeof dialog.showModal === 'function' && !dialog.open) dialog.showModal();
  else dialog.setAttribute('open', '');
}

function closeGallery() {
  const dialog = $('#gallery-dialog');
  if (typeof dialog.close === 'function' && dialog.open) dialog.close();
  else dialog.removeAttribute('open');
}

function changeGallery(direction) {
  showGallery(state.galleryIndex + direction);
}

function renderSermonMedia(sermon) {
  const videoUrl = safeMediaUrl(sermon.video_url);
  if (!videoUrl) return '<span class="sermon-meta">Archive entry</span>';
  const escapedVideoUrl = escapeHtml(videoUrl);
  if (/\.(mp4|webm|ogg)(?:[?#]|$)/i.test(videoUrl)) {
    const poster = safeMediaUrl(sermon.image_url);
    return `<div class="sermon-media"><video controls preload="metadata"${poster ? ` poster="${escapeHtml(poster)}"` : ''} aria-label="${escapeHtml(sermon.title)} video"><source src="${escapedVideoUrl}" /></video><a class="text-link" href="${escapedVideoUrl}" target="_blank" rel="noreferrer">Open full message</a></div>`;
  }
  return `<a class="button button-dark" href="${escapedVideoUrl}" target="_blank" rel="noreferrer">Watch message</a>`;
}

function renderSermons() {
  const target = $('#sermon-list');
  if (!state.sermons.length) { target.innerHTML = '<div class="empty-state">The sermon archive is ready for its first message.</div>'; return; }
  target.innerHTML = state.sermons.map((sermon) => `<article class="sermon-card"><figure><img src="${escapeHtml(safeMediaUrl(sermon.image_url) || '/church/IMG_20260902_151936.jpg')}" alt="${escapeHtml(sermon.title)}" loading="lazy" /></figure><div><p class="sermon-meta">${formatDate(sermon.published_on)} · ${escapeHtml(sermon.speaker || 'Cranes Mill Baptist Church')}</p><h2>${escapeHtml(sermon.title)}</h2><p>${escapeHtml(sermon.summary || 'A message from Cranes Mill Baptist Church.')}</p></div>${renderSermonMedia(sermon)}</article>`).join('');
}

function eventsForMonth(date) {
  return state.events.filter((event) => { const eventDate = dateValue(event.event_date); return eventDate.getFullYear() === date.getFullYear() && eventDate.getMonth() === date.getMonth(); });
}

function renderEventList() {
  const events = eventsForMonth(state.calendarDate);
  $('#event-list').innerHTML = events.length ? events.sort((a, b) => a.event_date.localeCompare(b.event_date)).map((event) => `<article class="list-event"><time datetime="${escapeHtml(event.event_date)}">${formatDate(event.event_date, { weekday: 'short', month: 'short', day: 'numeric' })}</time><h3>${escapeHtml(event.title)}</h3><p>${escapeHtml([event.event_time, event.location, event.description].filter(Boolean).join(' · ') || 'Cranes Mill Baptist Church')}</p></article>`).join('') : '<div class="empty-state">No events have been added for this month yet.</div>';
}

function renderCalendar() {
  const date = state.calendarDate;
  const year = date.getFullYear();
  const month = date.getMonth();
  $('#calendar-title').textContent = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const events = eventsForMonth(date);
  const eventDates = new Set(events.map((event) => event.event_date));
  const cells = [];
  for (let index = 0; index < 42; index += 1) {
    const day = index - firstDay + 1;
    const cellDate = new Date(year, month, day);
    const dateString = cellDate.toISOString().slice(0, 10);
    const inMonth = day > 0 && day <= daysInMonth;
    const isToday = dateString === new Date().toISOString().slice(0, 10);
    cells.push(`<button class="calendar-day${inMonth ? '' : ' muted'}${isToday ? ' today' : ''}" type="button" ${inMonth ? `data-calendar-date="${dateString}"` : 'disabled'}><span class="calendar-day-number">${cellDate.getDate()}</span>${eventDates.has(dateString) ? '<span class="calendar-dot" aria-label="Event scheduled"></span>' : ''}</button>`);
  }
  $('#calendar-grid').innerHTML = cells.join('');
  renderEventList();
}

function showDataError(target, message) { $(target).innerHTML = `<div class="empty-state error-state">${escapeHtml(message)}</div>`; }

async function handlePrayerSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const status = $('#prayer-status');
  const payload = Object.fromEntries(new FormData(form).entries());
  status.textContent = 'Sending your note…';
  try {
    await requestJson('/api/prayer-requests', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    form.reset();
    status.textContent = 'Thank you. Your note was received by the church office.';
  } catch (error) {
    status.textContent = error.name === 'AbortError' ? 'The request took too long. Please try again.' : 'We could not send that note right now. Please email the church office instead.';
  }
}

function bindEvents() {
  document.addEventListener('click', (event) => {
    const routeLink = event.target.closest('[data-route]');
    if (routeLink) { event.preventDefault(); setView(routeLink.dataset.route); return; }
    const slideButton = event.target.closest('[data-slide], [data-welcome-slide]');
    if (slideButton) {
      const dir = (slideButton.dataset.slide || slideButton.dataset.welcomeSlide) === 'next' ? 1 : -1;
      changeSlide(dir);
      return;
    }
    const galleryItem = event.target.closest('[data-gallery-index]');
    if (galleryItem) showGallery(Number(galleryItem.dataset.galleryIndex));
    const galleryButton = event.target.closest('[data-gallery]');
    if (galleryButton) {
      const action = galleryButton.dataset.gallery;
      if (action === 'close') closeGallery();
      if (action === 'previous') changeGallery(-1);
      if (action === 'next') changeGallery(1);
    }
    const calendarButton = event.target.closest('[data-calendar]');
    if (calendarButton) { state.calendarDate.setMonth(state.calendarDate.getMonth() + (calendarButton.dataset.calendar === 'next' ? 1 : -1)); renderCalendar(); }
    const calendarDate = event.target.closest('[data-calendar-date]');
    if (calendarDate) { const selected = eventsForMonth(state.calendarDate).filter((item) => item.event_date === calendarDate.dataset.calendarDate); $('#event-list').innerHTML = selected.length ? selected.map((item) => `<article class="list-event"><time>${formatDate(item.event_date, { weekday: 'short', month: 'short', day: 'numeric' })}</time><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml([item.event_time, item.location, item.description].filter(Boolean).join(' · ') || 'Cranes Mill Baptist Church')}</p></article>`).join('') : '<div class="empty-state">No events are listed for this day.</div>'; }
  });
  $('.menu-toggle').addEventListener('click', () => { const open = $('#site-nav').classList.toggle('open'); $('.menu-toggle').setAttribute('aria-expanded', String(open)); document.body.classList.toggle('menu-open', open); });
  const welcomeShow = $('#welcome-slideshow');
  if (welcomeShow) {
    welcomeShow.addEventListener('mouseenter', stopSlideShow);
    welcomeShow.addEventListener('mouseleave', startSlideShow);
    welcomeShow.addEventListener('focusin', stopSlideShow);
    welcomeShow.addEventListener('focusout', startSlideShow);
  }
  $('#gallery-dialog').addEventListener('click', (event) => { if (event.target === event.currentTarget) closeGallery(); });
  $('#open-map')?.addEventListener('click', () => {
    const dialog = $('#map-dialog');
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
  });
  $('#close-map')?.addEventListener('click', () => $('#map-dialog')?.close());
  $('#map-dialog')?.addEventListener('click', (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  $('#prayer-form').addEventListener('submit', handlePrayerSubmit);
  $('#player-toggle')?.addEventListener('click', toggleMusic);
  $('#player-next')?.addEventListener('click', () => loadMusicTrack(state.musicIndex + 1, { autoplay: true }));
  $('#site-audio')?.addEventListener('ended', () => {
    if (state.music.length > 1) loadMusicTrack(state.musicIndex + 1, { autoplay: true });
    else updatePlayerUi(false, false);
  });
  $('#site-audio')?.addEventListener('play', () => updatePlayerUi(true, false));
  $('#site-audio')?.addEventListener('pause', () => { if ($('#site-audio').ended) return; updatePlayerUi(false, false); });
  window.addEventListener('hashchange', () => setView(routeFromHash(), false));
  window.addEventListener('popstate', () => setView(routeFromHash(), false));
}

function currentMusicTrack() {
  return state.music[state.musicIndex] || null;
}

function updatePlayerUi(playing, needsGesture = false) {
  const player = $('#site-player');
  const toggle = $('#player-toggle');
  if (!player || !toggle) return;
  player.classList.toggle('is-playing', playing);
  player.classList.toggle('needs-gesture', needsGesture);
  toggle.setAttribute('aria-pressed', playing ? 'true' : 'false');
  toggle.setAttribute('aria-label', playing ? 'Pause music' : 'Play music');
  toggle.textContent = playing ? '❚❚' : '▶';
}

function loadMusicTrack(index, { autoplay = false } = {}) {
  if (!state.music.length) return;
  state.musicIndex = (index + state.music.length) % state.music.length;
  const track = currentMusicTrack();
  const audio = $('#site-audio');
  const url = safeMediaUrl(track.audio_url);
  if (!audio || !url) return;
  $('#player-title').textContent = track.title || 'Church music';
  $('#player-artist').textContent = track.artist || 'Cranes Mill Baptist Church';
  $('#player-next').hidden = state.music.length < 2;
  if (audio.src !== new URL(url, window.location.origin).href) {
    audio.src = url;
    audio.load();
  }
  if (autoplay) tryAutoplay();
}

async function tryAutoplay() {
  const audio = $('#site-audio');
  if (!audio?.src) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    updatePlayerUi(false, true);
    $('#player-artist').textContent = 'Tap play to listen';
    return;
  }
  try {
    await audio.play();
    updatePlayerUi(true, false);
  } catch {
    updatePlayerUi(false, true);
    $('#player-artist').textContent = 'Tap play to listen';
  }
}

async function toggleMusic() {
  const audio = $('#site-audio');
  if (!audio?.src) return;
  if (audio.paused) {
    try {
      await audio.play();
      updatePlayerUi(true, false);
    } catch {
      updatePlayerUi(false, true);
    }
    return;
  }
  audio.pause();
  updatePlayerUi(false, false);
}

function renderMusicPlayer() {
  const player = $('#site-player');
  const tracks = state.music.filter((item) => safeMediaUrl(item.audio_url));
  state.music = tracks;
  if (!player) return;
  if (!tracks.length) {
    player.hidden = true;
    $('#site-audio')?.pause();
    updatePlayerUi(false, false);
    return;
  }
  player.hidden = false;
  loadMusicTrack(0, { autoplay: true });
}

async function loadData() {
  const results = await Promise.allSettled([requestJson('/api/site'), requestJson('/api/gallery'), requestJson('/api/sermons'), requestJson('/api/events'), requestJson('/api/music')]);
  state.site = results[0].status === 'fulfilled' ? results[0].value.site : fallbackSite;
  state.ministries = results[0].status === 'fulfilled' ? results[0].value.ministries : [];
  state.gallery = results[1].status === 'fulfilled' ? results[1].value.items : fallbackGallery;
  state.sermons = results[2].status === 'fulfilled' ? results[2].value.items : [];
  state.events = results[3].status === 'fulfilled' ? results[3].value.items : [];
  state.music = results[4].status === 'fulfilled' ? results[4].value.items : [];
  renderSiteContent(); renderMinistries(); renderHero(); renderGallery(); renderHomeEvents(); renderSermons(); renderCalendar(); renderMusicPlayer();
  if (results[0].status === 'rejected') showDataError('#ministry-list', 'Site content is temporarily unavailable.');
  if (results[2].status === 'rejected') showDataError('#sermon-list', 'The sermon archive is temporarily unavailable. Please try again soon.');
  if (results[3].status === 'rejected') showDataError('#event-list', 'The event calendar is temporarily unavailable. Please try again soon.');
}

bindEvents();
setView(routeFromHash(), false);
loadData().catch(() => { state.site = fallbackSite; state.gallery = fallbackGallery; renderSiteContent(); renderMinistries(); renderHero(); renderGallery(); });
