let adminToken = '';

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

async function send(path, payload) {
  const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${adminToken}` }, body: JSON.stringify(payload) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.error || 'The request failed.');
  return data;
}

async function checkToken() {
  const response = await fetch('/api/admin/health', { headers: { Accept: 'application/json', Authorization: `Bearer ${adminToken}` } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.error || 'The request failed.');
  return data;
}

async function loadPrayerRequests() {
  const response = await fetch('/api/admin/prayer-requests', { headers: { Accept: 'application/json', Authorization: `Bearer ${adminToken}` } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.error || 'The request failed.');
  $('#prayer-list').innerHTML = data.items.length ? data.items.map((item) => `<article><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.email || 'No email supplied')} · ${escapeHtml(new Date(item.created_at).toLocaleString())}</small><p>${escapeHtml(item.message)}</p></article>`).join('') : '<p class="admin-status">No prayer requests have been received.</p>';
}

async function loadMusicTracks() {
  const response = await fetch('/api/music', { headers: { Accept: 'application/json' } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.error || 'The request failed.');
  $('#music-list').innerHTML = data.items.length
    ? data.items.map((item) => `<article><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.artist || 'Cranes Mill')} · ${escapeHtml(item.audio_url)}</small></article>`).join('')
    : '<p class="admin-status">No music tracks yet. Add one above to show the player on the public site.</p>';
}

async function loadSiteSettings() {
  const response = await fetch('/api/site', { headers: { Accept: 'application/json' } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.error || 'The request failed.');
  const site = data.site || {};
  for (const field of ['address', 'phone', 'email', 'facebook_url', 'instagram_url', 'youtube_url', 'worship_time', 'welcome_heading', 'welcome_body', 'giving_body']) {
    const input = document.querySelector(`#site-form [name="${field}"]`);
    if (input) input.value = site[field] || '';
  }
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function setStatus(target, message, isError = false) {
  $(target).textContent = message;
  $(target).style.color = isError ? '#8b2f2f' : '';
}

$('#token-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  adminToken = $('#admin-token').value.trim();
  if (!adminToken) return;
  try {
    await checkToken();
    $('#content-forms').hidden = false;
    setStatus('#token-status', 'Workspace unlocked.');
    await Promise.all([loadPrayerRequests(), loadSiteSettings(), loadMusicTracks()]);
  } catch (error) {
    adminToken = '';
    setStatus('#token-status', error.message.includes('required') ? 'That token was not accepted.' : 'The server is unavailable.', true);
  }
});

$('#site-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try { await send('/api/admin/site', formPayload(event.currentTarget)); setStatus('#site-status', 'Site details saved.'); }
  catch (error) { setStatus('#site-status', error.message, true); }
});

$('#sermon-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try { await send('/api/admin/sermons', formPayload(event.currentTarget)); event.currentTarget.reset(); setStatus('#sermon-status', 'Sermon saved.'); }
  catch (error) { setStatus('#sermon-status', error.message, true); }
});

$('#event-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try { await send('/api/admin/events', formPayload(event.currentTarget)); event.currentTarget.reset(); setStatus('#event-status', 'Event saved.'); }
  catch (error) { setStatus('#event-status', error.message, true); }
});

$('#ministry-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try { await send('/api/admin/ministries', formPayload(event.currentTarget)); event.currentTarget.reset(); setStatus('#ministry-status', 'Ministry saved.'); }
  catch (error) { setStatus('#ministry-status', error.message, true); }
});

$('#music-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await send('/api/admin/music', formPayload(event.currentTarget));
    event.currentTarget.reset();
    event.currentTarget.querySelector('[name="sort_order"]').value = '10';
    setStatus('#music-status', 'Music track saved.');
    await loadMusicTracks();
  } catch (error) { setStatus('#music-status', error.message, true); }
});
