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
  drawForecastChart(points);
}

function drawForecastChart(points) {
  const canvas = document.querySelector('#forecast-chart');
  if (!canvas || !points.length) return;
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  const padding = 34;
  const maxAqi = Math.max(300, ...points.map((point) => point.aqi));
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = '#dde3da';
  ctx.lineWidth = 1;
  [100, 200, 300].forEach((aqi) => {
    const y = height - padding - (aqi / maxAqi) * (height - padding * 2);
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    ctx.stroke();
    ctx.fillStyle = '#68736b';
    ctx.fillText(String(aqi), 4, y + 4);
  });
  ctx.strokeStyle = '#166534';
  ctx.lineWidth = 3;
  ctx.beginPath();
  points.forEach((point, index) => {
    const x = padding + (index / Math.max(1, points.length - 1)) * (width - padding * 2);
    const y = height - padding - (point.aqi / maxAqi) * (height - padding * 2);
    if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = '#166534';
  points.forEach((point, index) => {
    const x = padding + (index / Math.max(1, points.length - 1)) * (width - padding * 2);
    const y = height - padding - (point.aqi / maxAqi) * (height - padding * 2);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText(`+${point.horizon_hours}h`, x - 12, height - 8);
  });
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
