// frontend/script.js

const ApiManager = (function () {
  const BASE_URL = "http://localhost:5000";
  const fetchApi = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      return { error: error.message };
    }
  };
  return {
    getSensors: () => fetchApi("/api/sensors"),
    toggleDevice: (type, isOn) =>
      fetchApi("/api/device/toggle", {
        method: "POST",
        body: JSON.stringify({ type, isOn }),
      }),
    getHistory: (type, limit) =>
      fetchApi(`/api/sensor/history?type=${type}&limit=${limit}`),
    getPredictions: () => fetchApi("/api/predict/all"),
  };
})();

// === LOGIC CHÍNH ===
let temperatureChart, humidityChart;
let lastDisplayedMessage = ""; // 🔥 Biến quan trọng để chống spam log

document.addEventListener("DOMContentLoaded", function () {
  initLogin();
  initCharts();
});

function initLogin() {
  const btn = document.getElementById("login-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      const user = document.getElementById("username").value;
      const pass = document.getElementById("password").value;
      if (user === "admin" && pass === "123") {
        document.getElementById("login-page").style.display = "none";
        document.getElementById("dashboard-page").style.display = "block";
        startDashboard();
      } else {
        alert("Sai thông tin đăng nhập!");
      }
    });
  }
}

function initCharts() {
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    scales: { x: { ticks: { color: "#333" } } },
  };

  const tempCtx = document.getElementById("temperature-chart");
  if (tempCtx) {
    temperatureChart = new Chart(tempCtx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Thực tế",
            data: [],
            borderColor: "#ff6384",
            fill: true,
            tension: 0.3,
            order: 1,
          },
          {
            label: "AI Dự báo",
            data: [],
            borderColor: "#ffd700",
            backgroundColor: "#ffd700",
            pointRadius: 6,
            showLine: false,
            order: 0,
          },
        ],
      },
      options: commonOptions,
    });
  }

  const humiCtx = document.getElementById("humidity-chart");
  if (humiCtx) {
    humidityChart = new Chart(humiCtx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Thực tế",
            data: [],
            borderColor: "#36a2eb",
            fill: true,
            tension: 0.3,
          },
          {
            label: "AI Dự báo",
            data: [],
            borderColor: "#4bc0c0",
            backgroundColor: "#4bc0c0",
            pointRadius: 6,
            showLine: false,
          },
        ],
      },
      options: commonOptions,
    });
  }
}

async function startDashboard() {
  updateTime();
  setInterval(updateTime, 1000);
  await loadData();
  setInterval(loadData, 10000);

  const exportBtn = document.getElementById("export-btn");
  if (exportBtn) exportBtn.addEventListener("click", exportCSV);

  // Setup nút bấm
  setupToggle("toggle-led", "led", "status-led");
  setupToggle("toggle-fan", "fan", "status-fan");
}

function setupToggle(elementId, type, statusId) {
  const btn = document.getElementById(elementId);
  if (!btn) return;

  btn.addEventListener("change", async function () {
    // Gửi lệnh bật/tắt
    const res = await ApiManager.toggleDevice(type, this.checked);

    // Cập nhật text ON/OFF
    const statusLabel = document.getElementById(statusId);
    if (statusLabel) statusLabel.textContent = this.checked ? "ON" : "OFF";

    // Cập nhật log ngay lập tức
    if (res.message) {
      updateMessageUI(res.message);
    }
  });
}

async function loadData() {
  const data = await ApiManager.getSensors();

  if (!data.error) {
    document.getElementById("temperature-value").textContent =
      data.temperature + " °C";
    document.getElementById("humidity-value").textContent =
      data.humidity + " %";
    document.getElementById("light-value").textContent = data.light + " lux";

    // Đồng bộ nút gạt (Sync)
    syncSwitch("toggle-led", "status-led", data.led_status);
    syncSwitch("toggle-fan", "status-fan", data.fan_status);

    // Cập nhật log (CHỈ KHI CÓ TIN MỚI KHÁC TIN CŨ)
    if (data.message && data.message !== lastDisplayedMessage) {
      updateMessageUI(data.message);
    }

    updateAlerts(data.temperature);
  }

  const [tHist, hHist, aiData] = await Promise.all([
    ApiManager.getHistory("temp", 10),
    ApiManager.getHistory("humi", 10),
    ApiManager.getPredictions(),
  ]);

  if (tHist.data && temperatureChart) {
    updateChartWithAI(temperatureChart, tHist.data, aiData.temp_predict);
    if (aiData.temp_predict)
      document.getElementById("ai-temp-predict").textContent =
        aiData.temp_predict;
  }
  if (hHist.data && humidityChart) {
    updateChartWithAI(humidityChart, hHist.data, aiData.humi_predict);
  }
}

function syncSwitch(elementId, statusId, value) {
  const btn = document.getElementById(elementId);
  const label = document.getElementById(statusId);
  if (btn) {
    const shouldBeOn = value == 1;
    if (btn.checked !== shouldBeOn) {
      btn.checked = shouldBeOn;
      if (label) label.textContent = shouldBeOn ? "ON" : "OFF";
    }
  }
}

function updateMessageUI(msg) {
  if (!msg) return;

  // Lưu lại tin nhắn vừa hiện để lần sau so sánh
  lastDisplayedMessage = msg;

  const container = document.getElementById("message-container");
  if (container) {
    const time = new Date().toLocaleTimeString();
    container.innerHTML =
      `<p><strong>[${time}]</strong> ${msg}</p>` + container.innerHTML;
    if (container.children.length > 10) container.lastElementChild.remove();
  }
}

function updateChartWithAI(chart, historyData, aiValue) {
  const sortedData = historyData.reverse();
  const labels = sortedData.map((d) =>
    new Date(d.created_at).toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    })
  );
  const realValues = sortedData.map((d) => d.value);

  const aiDataPoints = new Array(realValues.length).fill(null);
  if (aiValue !== null && aiValue !== undefined) {
    labels.push("Dự báo");
    realValues.push(null);
    aiDataPoints.push(aiValue);
  }
  chart.data.labels = labels;
  chart.data.datasets[0].data = realValues;
  chart.data.datasets[1].data = aiDataPoints;
  chart.update();
}

function updateAlerts(temp) {
  const box = document.getElementById("temperature-alert");
  if (!box) return;
  if (temp > 40) {
    box.textContent = "🔥 QUÁ NÓNG";
    box.className = "alert-indicator temperature-alert-high";
  } else if (temp < 15) {
    box.textContent = "❄️ QUÁ LẠNH";
    box.className = "alert-indicator temperature-alert-low";
  } else {
    box.textContent = "Bình thường";
    box.className = "alert-indicator alert-normal";
  }
}

function updateTime() {
  const now = new Date();
  const el = document.getElementById("time-date-info");
  if (el) el.textContent = now.toLocaleString("vi-VN");
}

async function exportCSV() {
  const res = await ApiManager.getHistory("temp", 100);
  if (res.data) {
    let csv =
      "Time,Value\n" +
      res.data.map((r) => `${r.created_at},${r.value}`).join("\n");
    const link = document.createElement("a");
    link.href = encodeURI("data:text/csv;charset=utf-8," + csv);
    link.download = "report.csv";
    document.body.appendChild(link);
    link.click();
  } else {
    alert("Không có dữ liệu!");
  }
}
