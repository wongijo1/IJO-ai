window.onerror = function (msg, src, line, col, err) {
  try { alert('JS ERROR: ' + msg + ' (line ' + line + ')'); } catch (e) {}
  return false;
};

const loginOverlay = document.getElementById('loginOverlay');
const loginPass = document.getElementById('loginPass');
const loginBtn = document.getElementById('loginBtn');
const loginErr = document.getElementById('loginErr');
const loginSpinner = document.getElementById('loginSpinner');
const postLoader = document.getElementById('postLoader');
const togglePass = document.getElementById('togglePass');

function getToken() { return sessionStorage.getItem('ijo_token'); }
function authHeaders() {
  const t = getToken();
  return t ? { 'Authorization': 'Bearer ' + t } : {};
}
async function doLogin() {
  const pw = (loginPass.value || '').trim();
  if (loginErr) loginErr.textContent = '';
  if (loginBtn) { loginBtn.disabled = true; loginBtn.textContent = 'MEMPROSES...'; }
  if (loginSpinner) loginSpinner.hidden = false;
  try {
    await new Promise(r => setTimeout(r, 400));
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pw }),
    });
    const data = await res.json();
    if (data.ok && data.token) {
      sessionStorage.setItem('ijo_token', data.token);
      if (loginOverlay) loginOverlay.hidden = true;
      if (postLoader) postLoader.hidden = false;
      setTimeout(() => { if (postLoader) postLoader.hidden = true; }, 1300);
    } else {
      if (loginErr) loginErr.textContent = 'Password salah';
    }
  } catch (e) {
    if (loginErr) loginErr.textContent = 'Gagal terhubung';
  } finally {
    if (loginSpinner) loginSpinner.hidden = true;
    if (loginBtn) { loginBtn.disabled = false; loginBtn.textContent = 'MASUK'; }
  }
}
if (loginBtn) loginBtn.addEventListener('click', doLogin);
if (loginPass) loginPass.addEventListener('keydown', (e) => { if (e.key === 'Enter') doLogin(); });
if (togglePass && loginPass) {
  togglePass.addEventListener('click', () => {
    loginPass.type = (loginPass.type === 'password') ? 'text' : 'password';
  });
}

if (!getToken()) {
  if (loginOverlay) loginOverlay.hidden = false;
} else {
  if (loginOverlay) loginOverlay.hidden = true;
}
const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const typing = document.getElementById('typing');
const emptyState = document.getElementById('emptyState');
const modeText = document.getElementById('modeText');
const modeText2 = document.getElementById('modeText2');
const statusText = document.getElementById('statusText');
const clock = document.getElementById('clock');

const settingsBtn = document.getElementById('settingsBtn');
const voiceToggle = document.getElementById('voiceToggle');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const micBtn = document.getElementById('micBtn');
const voiceModeBtn = document.getElementById('voiceModeBtn');
const voiceOverlay = document.getElementById('voiceOverlay');
const voiceBackdrop = document.getElementById('voiceBackdrop');
const voiceClose = document.getElementById('voiceClose');
const voiceOrb = document.getElementById('voiceOrb');
const voiceStatus = document.getElementById('voiceStatus');
const voiceTranscript = document.getElementById('voiceTranscript');
const voiceStart = document.getElementById('voiceStart');
const voiceStop = document.getElementById('voiceStop');

const modal = document.getElementById('settingsModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalClose = document.getElementById('modalClose');
const tabs = document.querySelectorAll('.tab');
const sections = document.querySelectorAll('.modal-section');

// Voice
const voiceEnabledEl = document.getElementById('voiceEnabled');
const voiceSelect = document.getElementById('voiceSelect');
const rateRange = document.getElementById('rateRange');
const pitchRange = document.getElementById('pitchRange');
const testVoiceBtn = document.getElementById('testVoiceBtn');
const voiceNote = document.getElementById('voiceNote');

// World clock
const citySelect = document.getElementById('citySelect');
const addCityBtn = document.getElementById('addCityBtn');
const cityList = document.getElementById('cityList');

let busy = false;
let currentImage = null; // dataURL

// ---------- utils ----------
function now() {
  return new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', hour12: false });
}
function nowTime() {
  const d = new Date();
  return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}
function tickClock() { if (clock) clock.textContent = nowTime(); }
setInterval(tickClock, 1000); tickClock();

// ---------- storage ----------
function loadJSON(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? JSON.stringify(fallback); }
  catch { return fallback; }
}
function saveJSON(key, val) { localStorage.setItem(key, JSON.stringify(val)); }

// ---------- chat ----------
function makeMsg(role, text, imageUrl) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role === 'user' ? 'user' : 'bot'}`;

  const av = document.createElement('div');
  av.className = 'avatar small';
  av.textContent = (role === 'user' ? 'U' : 'I');
  if (role === 'user') wrap.appendChild(document.createElement('div')); // placeholder order

  // rebuild order properly:
  wrap.innerHTML = '';
  if (role !== 'user') {
    const a = document.createElement('div'); a.className='avatar small'; a.textContent='I'; wrap.appendChild(a);
  }

  const col = document.createElement('div');
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text || '';
  if (imageUrl) {
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.maxWidth = '220px';
    img.style.maxHeight = '220px';
    img.style.borderRadius = '4px';
    img.style.display = 'block';
    img.style.marginBottom = '6px';
    bubble.prepend(img);
  }
  col.appendChild(bubble);
  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = now();
  col.appendChild(meta);
  wrap.appendChild(col);

  if (role === 'user') {
    const a = document.createElement('div'); a.className='avatar small'; a.textContent='U'; wrap.appendChild(a);
  }
  return wrap;
}

function appendMsg(role, text, imageUrl) {
  if (emptyState && emptyState.parentNode) emptyState.remove();
  chat.appendChild(makeMsg(role, text, imageUrl));
  chat.scrollTop = chat.scrollHeight;
}

function setTyping(v) { typing.hidden = !v; }

// ---------- TTS ----------
let voiceEnabled = loadJSON('ijo_voice_enabled', false);
let voiceName = loadJSON('ijo_voice_name', '');
let voiceRate = parseFloat(loadJSON('ijo_voice_rate', 1.0));
let voicePitch = parseFloat(loadJSON('ijo_voice_pitch', 0.85));

function applyVoiceSettingsToUI() {
  voiceEnabledEl.checked = !!voiceEnabled;
  voiceToggle.textContent = voiceEnabled ? '🔊' : '🔇';
  voiceToggle.style.opacity = voiceEnabled ? '1' : '0.5';
  rateRange.value = voiceRate;
  pitchRange.value = voicePitch;
}
applyVoiceSettingsToUI();

function getVoices() {
  return window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

function populateVoices() {
  const voices = getVoices();
  voiceSelect.innerHTML = '';
  voices.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.name;
    opt.textContent = `${v.name} (${v.lang})`;
    if (v.name === voiceName) opt.selected = true;
    voiceSelect.appendChild(opt);
  });
  if (!voiceName && voices.length) {
    // prefer male-ish or Indonesian
    const preferred = voices.find(v => /male|david|paul|mark|james|daniel/i.test(v.name))
      || voices.find(v => v.lang && v.lang.startsWith('id'))
      || voices[0];
    voiceName = preferred.name;
    saveJSON('ijo_voice_name', voiceName);
    voiceSelect.value = voiceName;
  }
  // note
  const maleCount = voices.filter(v => /male|david|paul|mark|james|daniel/i.test(v.name)).length;
  voiceNote.textContent = `Tersedia ${voices.length} suara. (${maleCount} terdeteksi male-ish). Nada rendah dipakai agar terdengar cowok.`;
}
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = populateVoices;
  populateVoices();
}
setTimeout(populateVoices, 500);

function speak(text, onEnd) {
  if (!window.speechSynthesis || !text) { if (onEnd) onEnd(); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const voices = getVoices();
  const v = voices.find(x => x.name === voiceName) || voices[0];
  if (v) u.voice = v;
  u.lang = v ? v.lang : 'id-ID';
  u.rate = voiceRate;
  u.pitch = voicePitch;
  u.volume = 1;
  if (onEnd) {
    u.onend = () => onEnd();
    u.onerror = () => onEnd();
  }
  window.speechSynthesis.speak(u);
}

// voice events
voiceEnabledEl.addEventListener('change', () => {
  voiceEnabled = voiceEnabledEl.checked;
  saveJSON('ijo_voice_enabled', voiceEnabled);
  applyVoiceSettingsToUI();
});
voiceSelect.addEventListener('change', () => {
  voiceName = voiceSelect.value;
  saveJSON('ijo_voice_name', voiceName);
});
rateRange.addEventListener('input', () => { voiceRate = parseFloat(rateRange.value); saveJSON('ijo_voice_rate', voiceRate); });
pitchRange.addEventListener('input', () => { voicePitch = parseFloat(pitchRange.value); saveJSON('ijo_voice_pitch', voicePitch); });
testVoiceBtn.addEventListener('click', () => {
  voiceEnabled = true; applyVoiceSettingsToUI(); voiceEnabledEl.checked = true; saveJSON('ijo_voice_enabled', true);
  speak('Halo, saya IJO. Ini suara saya. Semoga terdengar maskulin.');
});
voiceToggle.addEventListener('click', () => {
  voiceEnabled = !voiceEnabled;
  saveJSON('ijo_voice_enabled', voiceEnabled);
  applyVoiceSettingsToUI();
  if (voiceEnabled) speak('Suara diaktifkan.');
});

// ---------- World clock ----------
const DEFAULT_CITIES = ['Asia/Jakarta','Asia/Tokyo','Europe/London','America/New_York','Australia/Sydney','Asia/Dubai'];
let selectedCities = loadJSON('ijo_cities', DEFAULT_CITIES);
if (!Array.isArray(selectedCities)) selectedCities = DEFAULT_CITIES.slice();
saveJSON('ijo_cities', selectedCities);

const CITY_OPTIONS = [
  {name:'Jakarta (WIB)', tz:'Asia/Jakarta'},
  {name:'Tokyo', tz:'Asia/Tokyo'},
  {name:'Singapore', tz:'Asia/Singapore'},
  {name:'Dubai', tz:'Asia/Dubai'},
  {name:'London', tz:'Europe/London'},
  {name:'Paris', tz:'Europe/Paris'},
  {name:'New York', tz:'America/New_York'},
  {name:'Los Angeles', tz:'America/Los_Angeles'},
  {name:'Sydney', tz:'Australia/Sydney'},
  {name:'Auckland', tz:'Pacific/Auckland'},
  {name:'Seoul', tz:'Asia/Seoul'},
  {name:'Beijing', tz:'Asia/Shanghai'},
];

function populateCitySelect() {
  citySelect.innerHTML = '';
  CITY_OPTIONS.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.tz;
    opt.textContent = c.name;
    citySelect.appendChild(opt);
  });
}
populateCitySelect();

function renderCities() {
  cityList.innerHTML = '';
  selectedCities.forEach(tz => {
    const opt = CITY_OPTIONS.find(c => c.tz === tz);
    const name = opt ? opt.name : tz;
    const row = document.createElement('div');
    row.className = 'city-row';
    row.innerHTML = `<span class="city-name">${name}</span><span class="city-time" data-tz="${tz}">--:--:--</span><button class="mini-btn remove-city" data-tz="${tz}">✕</button>`;
    cityList.appendChild(row);
  });
  cityList.querySelectorAll('.remove-city').forEach(btn => {
    btn.addEventListener('click', () => {
      selectedCities = selectedCities.filter(t => t !== btn.dataset.tz);
      saveJSON('ijo_cities', selectedCities);
      renderCities();
    });
  });
}
renderCities();

function updateCityTimes() {
  document.querySelectorAll('.city-time').forEach(el => {
    const tz = el.dataset.tz;
    try {
      const s = new Intl.DateTimeFormat('id-ID', {
        timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
      }).format(new Date());
      el.textContent = s;
    } catch { el.textContent = '--:--:--'; }
  });
}
setInterval(updateCityTimes, 1000); updateCityTimes();

addCityBtn.addEventListener('click', () => {
  const tz = citySelect.value;
  if (!selectedCities.includes(tz)) {
    selectedCities.push(tz);
    saveJSON('ijo_cities', selectedCities);
    renderCities();
    updateCityTimes();
  }
});

// ---------- settings modal ----------
function openModal() { modal.hidden = false; }
function closeModal() { modal.hidden = true; }
settingsBtn.addEventListener('click', openModal);
modalBackdrop.addEventListener('click', closeModal);
modalClose.addEventListener('click', closeModal);

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    sections.forEach(s => {
      s.hidden = s.dataset.section !== tab.dataset.tab;
    });
  });
});

// ---------- autosize ----------
function isNearBottom() {
  return (chat.scrollHeight - chat.scrollTop - chat.clientHeight) < 80;
}
function autosize() {
  const anchor = isNearBottom();
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 96) + 'px';
  if (anchor) chat.scrollTop = chat.scrollHeight;
}

window.handleKeyDown = function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send(input.value);
    return false;
  }
  return true;
};
input.onkeydown = window.handleKeyDown;
input.addEventListener('input', autosize);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send(input.value);
  }
});
sendBtn.addEventListener('click', () => send(input.value));

// ---------- image upload ----------
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  const f = fileInput.files && fileInput.files[0];
  if (!f) return;
  if (f.size > 6 * 1024 * 1024) { alert('Gambar terlalu besar (max 6MB).'); fileInput.value=''; return; }
  const reader = new FileReader();
  reader.onload = (e) => {
    currentImage = e.target.result;
    // auto send with optional text
    send(input.value, currentImage);
    currentImage = null;
    fileInput.value = '';
  };
  reader.readAsDataURL(f);
});

// ---------- speech recognition (input suara) ----------
let recognition = null;
let listening = false;
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  recognition = new SR();
  recognition.lang = 'id-ID';
  recognition.interimResults = true;
  recognition.continuous = false;
  let finalTranscript = '';
  recognition.onstart = () => { listening = true; if (micBtn) { micBtn.classList.add('listening'); } };
  recognition.onresult = (e) => {
    let interim = '';
    finalTranscript = '';
    for (let i = 0; i < e.results.length; i++) {
      const r = e.results[i];
      if (r.isFinal) finalTranscript += r[0].transcript + ' ';
      else interim += r[0].transcript;
    }
    if (voiceMode) {
      vmFinal = (finalTranscript + interim).trim();
      vmSetStatus('Mendengarkan: ' + (vmFinal || '...'));
    } else {
      input.value = (finalTranscript + interim).trim();
      autosize();
    }
  };
  recognition.onend = () => {
    listening = false;
    if (micBtn) micBtn.classList.remove('listening');
    if (voiceMode) {
      vmSetOrb(null);
      if (vmFinal.trim() && !vmProcessing) {
        vmProcess(vmFinal.trim());
      } else if (voiceMode && !vmProcessing) {
        vmStartListening();
      }
    } else if (finalTranscript.trim()) {
      input.value = finalTranscript.trim();
      autosize();
    }
  };
  recognition.onerror = (e) => {
    listening = false;
    if (micBtn) micBtn.classList.remove('listening');
    if (e.error && e.error !== 'no-speech') appendMsg('bot', 'Gagal input suara: ' + e.error);
  };
} else {
  if (micBtn) micBtn.style.display = 'none';
}
function toggleMic() {
  if (!recognition) return;
  if (listening) recognition.stop();
  else { try { recognition.start(); } catch (e) {} }
}
if (micBtn) micBtn.addEventListener('click', toggleMic);

// ---------- voice mode (like Grok) ----------
let voiceMode = false;
let vmProcessing = false;
let vmFinal = '';

function vmSetStatus(t) { if (voiceStatus) voiceStatus.textContent = t; }
function vmSetOrb(state) {
  if (!voiceOrb) return;
  voiceOrb.classList.remove('listening', 'speaking');
  if (state) voiceOrb.classList.add(state);
}
function openVoiceMode() {
  if (!voiceOverlay) return;
  voiceOverlay.hidden = false;
  voiceMode = true;
  if (micBtn) micBtn.disabled = true;
  if (uploadBtn) uploadBtn.disabled = true;
  if (voiceTranscript) voiceTranscript.innerHTML = '';
  vmProcessing = false;
  vmFinal = '';
  vmSetStatus('Tekan MULAI lalu bicara');
  vmSetOrb(null);
}
function closeVoiceMode() {
  voiceMode = false;
  vmProcessing = false;
  try { if (recognition) recognition.stop(); } catch (e) {}
  try { if (window.speechSynthesis) window.speechSynthesis.cancel(); } catch (e) {}
  if (voiceOverlay) voiceOverlay.hidden = true;
  if (micBtn) micBtn.disabled = false;
  if (uploadBtn) uploadBtn.disabled = false;
  vmSetOrb(null);
}
function vmStartListening() {
  if (!voiceMode) return;
  if (vmProcessing) return;
  if (!recognition) { vmSetStatus('Browser tidak mendukung suara'); return; }
  vmFinal = '';
  try { recognition.start(); } catch (e) {}
  vmSetStatus('Mendengarkan...');
  vmSetOrb('listening');
}
function vmProcess(text) {
  if (!text) { vmStartListening(); return; }
  vmProcessing = true;
  vmFinal = '';
  vmSetStatus('IJO sedang berpikir...');
  vmSetOrb(null);
  if (voiceTranscript) {
    const line = document.createElement('div');
    line.innerHTML = '<b>Kamu:</b> ' + text;
    voiceTranscript.appendChild(line);
  }
  appendMsg('user', text);
  const body = { message: text };
  fetch('/api/send', { method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, authHeaders()), body: JSON.stringify(body) })
    .then(r => r.json())
    .then(data => {
      const reply = data.reply || '';
      if (voiceTranscript) {
        const botLine = document.createElement('div');
        botLine.innerHTML = '<b>IJO:</b> ' + reply;
        voiceTranscript.appendChild(botLine);
      }
      appendMsg('bot', reply);
      vmSetStatus('IJO sedang berbicara...');
      vmSetOrb('speaking');
      speak(reply, () => {
        vmProcessing = false;
        vmSetOrb(null);
        if (voiceMode) vmStartListening();
      });
    })
    .catch(e => {
      vmProcessing = false;
      vmSetStatus('Gagal terhubung');
      vmSetOrb(null);
      if (voiceMode) vmStartListening();
    });
}
if (voiceModeBtn) voiceModeBtn.addEventListener('click', openVoiceMode);
if (voiceBackdrop) voiceBackdrop.addEventListener('click', closeVoiceMode);
if (voiceClose) voiceClose.addEventListener('click', closeVoiceMode);
if (voiceStart) voiceStart.addEventListener('click', vmStartListening);
if (voiceStop) voiceStop.addEventListener('click', () => { try { recognition && recognition.stop(); } catch(e){} vmProcessing = false; vmSetStatus('Dihentikan'); vmSetOrb(null); });

// ---------- send ----------
async function send(text, image) {
  text = (text || '').trim();
  const img = image || null;
  if (!text && !img) return;
  if (busy) return;
  busy = true;
  sendBtn.disabled = true; uploadBtn.disabled = true;
  appendMsg('user', text || (img ? '(gambar)' : ''), img);
  input.value = '';
  autosize();
  setTyping(true);

  try {
    const body = { message: text };
    if (img) body.image = img;
    const res = await fetch('/api/send', {
      method: 'POST',
      headers: Object.assign({ 'Content-Type': 'application/json' }, authHeaders()),
      body: JSON.stringify(body),
    });
    if (res.status === 401) {
      if (loginOverlay) loginOverlay.hidden = false;
      setTyping(false);
      throw new Error('unauthorized');
    }
    const data = await res.json();
    setTyping(false);
    if (data.error) {
      appendMsg('bot', 'Terjadi kesalahan: ' + data.error);
    } else {
      const reply = data.reply || '';
      appendMsg('bot', reply);
      if (data.status === 'exit') {
        statusText.textContent = 'OFFLINE';
        input.disabled = true;
      }
    }
  } catch (e) {
    setTyping(false);
    appendMsg('bot', 'Gagal terhubung ke server.');
  } finally {
    busy = false;
    sendBtn.disabled = false; uploadBtn.disabled = false;
    input.focus();
  }
}

document.querySelectorAll('[data-cmd]').forEach(btn => {
  btn.addEventListener('click', () => send(btn.dataset.cmd));
});
document.querySelectorAll('[data-text]').forEach(btn => {
  btn.addEventListener('click', () => send(btn.dataset.text));
});

// load info
fetch('/api/info', { headers: authHeaders() }).then(r => r.json()).then(d => {
  const m = (d.mode || 'offline').toUpperCase();
  if (modeText) modeText.textContent = m;
  if (modeText2) modeText2.textContent = m;
}).catch(() => {});

autosize();
input.focus();

// auto-open voice mode if summoned via hotkey
try {
  const params = new URLSearchParams(window.location.search);
  if (params.get('voice') === '1' && getToken()) {
    setTimeout(() => { if (typeof openVoiceMode === 'function') openVoiceMode(); }, 900);
  }
} catch (e) {}
