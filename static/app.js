const statusEl = document.querySelector('#status');

function setText(selector, text) {
  document.querySelector(selector).textContent = text;
}

function aqiColor(aqi) {
  if (aqi <= 50) return '#15803d';
  if (aqi <= 100) return '#ca8a04';
  if (aqi <= 150) return '#ea580c';
  if (aqi <= 200) return '#dc2626';
  if (aqi <= 300) return '#7e22ce';
  return '#7f1d1d';
}

function adviceForAqi(aqi) {
  if (aqi <= 50) return 'Air is good. Outdoor activity is fine for most people.';
  if (aqi <= 100) return 'Air is moderate. Sensitive people should watch symptoms during long outdoor activity.';
  if (aqi <= 150) return 'Sensitive groups should reduce prolonged outdoor exertion and consider a mask outdoors.';
  if (aqi <= 200) return 'Everyone should reduce prolonged outdoor exertion. Sensitive groups should avoid it.';
  if (aqi <= 300) return 'Avoid outdoor exertion where possible. Use a well-fitting mask if you must go out.';
  return 'Hazardous air. Stay indoors where possible and keep windows closed.';
}

function renderCurrent(current) {
  const color = aqiColor(current.aqi);
  setText('#aqi', current.aqi);
  setText('#category', current.category);
  setText('#pm25', `PM2.5: ${current.pm25} ug/m3`);
  setText('#health-advice', adviceForAqi(current.aqi));
  setText('#updated', `Updated: ${current.timestamp}`);
  setText('#source', current.source ? `Source: ${current.source}` : '');
  document.querySelector('#aqi').style.color = color;
  const category = document.querySelector('#category');
  category.style.background = color;
  category.style.color = '#ffffff';
  const gauge = document.querySelector('#aqi-gauge');
  gauge.style.width = `${Math.min(100, (current.aqi / 500) * 100)}%`;
  gauge.style.background = color;
}

function renderForecast(points) {
  const list = document.querySelector('#forecast');
  list.innerHTML = points.map((point) => `
    <li>
      <span class="horizon">+${point.horizon_hours}h</span>
      <strong style="color:${aqiColor(point.aqi)}">AQI ${point.aqi}</strong>
      <span>PM2.5 ${point.pm25}</span>
      <span>${point.category}</span>
    </li>
  `).join('');
  if (points.length) {
    const worst = points.reduce((max, point) => (point.aqi > max.aqi ? point : max), points[0]);
    setText('#forecast-summary', `Worst: +${worst.horizon_hours}h · AQI ${worst.aqi}`);
  }
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
  const lineColor = aqiColor(Math.max(...points.map((point) => point.aqi)));
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
  ctx.strokeStyle = lineColor;
  ctx.lineWidth = 3;
  ctx.beginPath();
  points.forEach((point, index) => {
    const x = padding + (index / Math.max(1, points.length - 1)) * (width - padding * 2);
    const y = height - padding - (point.aqi / maxAqi) * (height - padding * 2);
    if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  points.forEach((point, index) => {
    const x = padding + (index / Math.max(1, points.length - 1)) * (width - padding * 2);
    const y = height - padding - (point.aqi / maxAqi) * (height - padding * 2);
    ctx.fillStyle = aqiColor(point.aqi);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#68736b';
    ctx.fillText(`+${point.horizon_hours}h`, x - 12, height - 8);
  });
}

function renderStations(stations) {
  const list = document.querySelector('#stations');
  list.innerHTML = stations.map((station) => `
    <li><span><span class="dot"></span>${station.name}</span><span>${station.latitude}, ${station.longitude}</span></li>
  `).join('');
}

async function loadInitial() {
  statusEl.textContent = 'Loading backend data…';
  const [current, forecast, stations] = await Promise.all([
    fetch('/current').then((response) => response.json()),
    fetch('/forecast?hours=24').then((response) => response.json()),
    fetch('/stations').then((response) => response.json()),
  ]);
  renderCurrent(current);
  renderForecast(forecast.forecast);
  renderStations(stations.stations);
  statusEl.textContent = 'Backend data loaded.';
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
  socket.addEventListener('close', () => { statusEl.textContent = 'Showing loaded forecast. Use Refresh for new data.'; });
  socket.addEventListener('error', () => { statusEl.textContent = 'Showing loaded forecast. Use Refresh for new data.'; });
}

document.querySelector('#refresh').addEventListener('click', () => {
  loadInitial().catch(() => { statusEl.textContent = 'Refresh failed. Check the backend and try again.'; });
});

loadInitial()
  .then(connectSocket)
  .catch(() => { statusEl.textContent = 'Backend data is not ready. Run the data fetch and modelling commands first.'; });
