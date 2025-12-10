// frontend/script.js

// =====================================================================
// === SINGLETON API MANAGER ===
// =====================================================================
const ApiManager = (function () {
  const BASE_URL = "http://localhost:5000";

  // Hàm fetch chung
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
    // Hàm điều khiển chung cho cả Đèn và Quạt
    toggleDevice: (type, isOn) =>
      fetchApi("/api/device/toggle", {
        method: "POST",
        body: JSON.stringify({ type: type, isOn: isOn }),
      }),
    getHistory: (type, limit) =>
      fetchApi(`/api/sensor/history?type=${type}&limit=${limit}`),
    // 🔥 API MỚI CHO AI
    getAiPrediction: () => fetchApi("/api/predict/temperature"),
    testConnection: () => fetchApi("/api/test"),
  };
})();

// =====================================================================
// === LOGIC CHÍNH ===
// =====================================================================
let temperatureChart, humidityChart;

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
    animation: { duration: 0 }, // Tắt animation để đỡ lag
  };

  const tempCtx = document.getElementById("temperature-chart");
  if (tempCtx) {
    temperatureChart = new Chart(tempCtx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          { label: "Temp (°C)", data: [], borderColor: "#ff6384", fill: true },
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
            label: "Humidity (%)",
            data: [],
            borderColor: "#36a2eb",
            fill: true,
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

  // Loop cập nhật dữ liệu
  loadData();
  setInterval(loadData, 10000); // 3s/lần

  // Setup Export Button
  const exportBtn = document.getElementById("export-btn");
  if (exportBtn) {
    exportBtn.addEventListener("click", exportCSV);
  }

  // ==========================================================
  // 🔥 PHẦN BẠN CẦN SỬA LÀ Ở ĐÂY 🔥
  // ==========================================================

  // 1. XỬ LÝ ĐÈN (LED)
  // Tìm nút toggle đèn (có thể là id 'toggle-led' hoặc 'toggle-1' tùy code html cũ hay mới)
  const ledBtn =
    document.getElementById("toggle-led") ||
    document.getElementById("toggle-1");
  if (ledBtn) {
    ledBtn.addEventListener("change", async function () {
      // Gọi hàm toggleDevice với type là 'led'
      await ApiManager.toggleDevice("led", this.checked);

      // Cập nhật text trạng thái
      const statusLabel =
        document.getElementById("status-led") ||
        document.getElementById("status-1");
      if (statusLabel) {
        statusLabel.textContent = this.checked ? "ON" : "OFF";
      }
    });
  }

  // 2. XỬ LÝ QUẠT (FAN)
  const fanBtn = document.getElementById("toggle-fan");
  if (fanBtn) {
    fanBtn.addEventListener("change", async function () {
      // Gọi hàm toggleDevice với type là 'fan'
      await ApiManager.toggleDevice("fan", this.checked);

      // Cập nhật text trạng thái
      const statusLabel = document.getElementById("status-fan");
      if (statusLabel) {
        statusLabel.textContent = this.checked ? "ON" : "OFF";
      }
    });
  }
}

async function loadData() {
  // 1. Lấy dữ liệu sensor hiện tại
  const data = await ApiManager.getSensors();
  if (!data.error) {
    // Cập nhật giá trị
    document.getElementById("temperature-value").textContent =
      data.temperature + " °C";
    document.getElementById("humidity-value").textContent =
      data.humidity + " %";
    document.getElementById("light-value").textContent = data.light + " lux";

    // Cập nhật tin nhắn log (nếu có)
    const msgContainer = document.getElementById("message-container");
    if (msgContainer && data.message) {
      // Xóa nội dung cũ và thêm tin nhắn mới nhất
      msgContainer.innerHTML = `<p>${data.message}</p>`;
    }

    // Cảnh báo nhiệt độ
    const alertBox = document.getElementById("temperature-alert");
    if (alertBox) {
      if (data.temperature > 40) {
        alertBox.textContent = "🔥 QUÁ NÓNG";
        alertBox.className = "alert-indicator temperature-alert-high";
      } else if (data.temperature < 15) {
        alertBox.textContent = "❄️ QUÁ LẠNH";
        alertBox.className = "alert-indicator temperature-alert-low";
      } else {
        alertBox.textContent = "Bình thường";
        alertBox.className = "alert-indicator alert-normal";
      }
    }
  }

  // 2. 🔥 Lấy dự báo AI
  const aiData = await ApiManager.getAiPrediction();
  if (aiData.predicted_value) {
    const aiPredictElement = document.getElementById("ai-temp-predict");
    if (aiPredictElement) {
      aiPredictElement.textContent = aiData.predicted_value;
    }
  }

  // 3. Cập nhật biểu đồ (Lấy lịch sử)
  if (temperatureChart) {
    const history = await ApiManager.getHistory("temp", 10);
    if (history.data) {
      updateChart(temperatureChart, history.data);
    }
  }

  if (humidityChart) {
    const hHistory = await ApiManager.getHistory("humi", 10);
    if (hHistory.data) {
      updateChart(humidityChart, hHistory.data);
    }
  }
}

function updateChart(chart, data) {
  const labels = data.map((d) => new Date(d.created_at).toLocaleTimeString());
  const values = data.map((d) => d.value);

  chart.data.labels = labels.reverse(); // Đảo ngược để mới nhất ở phải
  chart.data.datasets[0].data = values.reverse();
  chart.update();
}

function updateTime() {
  const now = new Date();
  const timeElement = document.getElementById("time-date-info");
  if (timeElement) {
    timeElement.textContent = now.toLocaleString("vi-VN");
  }
}

// 🔥 TÍNH NĂNG HTTT: EXPORT CSV
async function exportCSV() {
  const response = await ApiManager.getHistory("temp", 100);
  if (response.data) {
    let csvContent = "data:text/csv;charset=utf-8,Time,Value\n";
    response.data.forEach((row) => {
      csvContent += `${row.created_at},${row.value}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "sensor_report.csv");
    document.body.appendChild(link);
    link.click();
  } else {
    alert("Không có dữ liệu để xuất!");
  }
}
