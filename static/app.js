const statusEl = document.querySelector('#status');

function setText(selector, text) {
  document.querySelector(selector).textContent = text;
}

function renderCurrent(current) {
  setText('#aqi', current.aqi);
  setText('#category', current.category);
  setText('#pm25', `PM2.5: ${current.pm25} ug/m3`);
  setText('#updated', `Updated: ${current.timestamp}`);
}

function renderForecast(points) {
  const list = document.querySelector('#forecast');
  list.innerHTML = points.map((point) => `
    <li>
      <span>+${point.horizon_hours}h</span>
      <strong>AQI ${point.aqi}</strong>
      <span>${point.category}</span>
    </li>
  `).join('');
}

function renderStations(stations) {
  const list = document.querySelector('#stations');
  list.innerHTML = stations.map((station) => `
    <li><span>${station.name}</span><span>${station.latitude}, ${station.longitude}</span></li>
  `).join('');
}

async function loadInitial() {
  const [current, forecast, stations] = await Promise.all([
    fetch('/current').then((response) => response.json()),
    fetch('/forecast?hours=24').then((response) => response.json()),
    fetch('/stations').then((response) => response.json()),
  ]);
  renderCurrent(current);
  renderForecast(forecast.forecast);
  renderStations(stations.stations);
}

function connectSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${protocol}//${window.location.host}/ws/predictions`);
  socket.addEventListener('open', () => { statusEl.textContent = 'Live backend connected.'; });
  socket.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data);
    renderCurrent(payload.current);
    renderForecast(payload.forecast);
  });
  socket.addEventListener('close', () => { statusEl.textContent = 'Live stream disconnected. Refresh to reconnect.'; });
}

loadInitial()
  .then(connectSocket)
  .catch(() => { statusEl.textContent = 'Backend data is not ready. Run the data fetch and modelling commands first.'; });
