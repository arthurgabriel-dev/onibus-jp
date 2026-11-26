// Service worker do Ônibus JP: deixa o app abrir sem internet (a parte dos dados e do mapa base depende de rede).
// Aumente VERSION sempre que publicar arquivos novos para o celular baixar a versão nova.
const VERSION = 'v5';
const CACHE = 'onibus-jp-' + VERSION;
const SHELL = [
  './', 'index.html', 'sobre.html', 'dados-semob.js', 'manifest.webmanifest',
  'lib/leaflet/leaflet.js', 'lib/leaflet/leaflet.css',
  'lib/leaflet/images/layers.png', 'lib/leaflet/images/layers-2x.png',
  'lib/leaflet/images/marker-icon.png', 'lib/leaflet/images/marker-icon-2x.png', 'lib/leaflet/images/marker-shadow.png',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png', 'icons/favicon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('onibus-jp-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Só mexe em arquivos do próprio site. Mapa (tiles), buscas de endereço e Overpass vão direto para a rede.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {            // página: tenta a rede (versão mais nova); sem rede, usa a guardada
    e.respondWith(
      fetch(req).then(r => { if (r && r.ok) { const c = r.clone(); caches.open(CACHE).then(ch => ch.put(req, c)); } return r; })
        .catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html')).then(r => r || caches.match('./')))
    );
    return;
  }
  e.respondWith(                            // demais arquivos: responde do cache e atualiza em segundo plano
    caches.match(req).then(hit => {
      const net = fetch(req).then(r => { if (r && r.ok) { const c = r.clone(); caches.open(CACHE).then(ch => ch.put(req, c)); } return r; }).catch(() => hit);
      return hit || net;
    })
  );
});
