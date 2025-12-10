# backend/app.py
import os
import time
from datetime import datetime # Thêm thư viện này
from flask import Flask, jsonify, request
from flask_cors import CORS
from Adafruit_IO import Client
from ai_model import TemperaturePredictor

app = Flask(__name__)
CORS(app)

# --- CẤU HÌNH ---
AIO_USERNAME = "2213671"
AIO_KEY = "aio_oKZg90V6hW5UW6Zy6me44JrIQSKS"

# --- SINGLETON PATTERN ---
class AdafruitManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdafruitManager, cls).__new__(cls)
            try:
                cls._instance.client = Client(AIO_USERNAME, AIO_KEY)
                print("✅ [Singleton] Đã khởi tạo kết nối Adafruit IO")
            except Exception as e:
                cls._instance.client = None
        return cls._instance
    def get_client(self): return self.client

aio_manager = AdafruitManager()
ai_predictor = TemperaturePredictor()

# --- LƯU TRỮ TIN NHẮN LOCAL (Thay thế Feed Mess) ---
local_messages = [] # List lưu lịch sử tin nhắn

def add_system_message(text):
    """Hàm thêm tin nhắn vào bộ nhớ server"""
    timestamp = datetime.now().isoformat()
    # Thêm vào đầu danh sách
    local_messages.insert(0, {'value': text, 'created_at': timestamp})
    # Chỉ giữ lại 50 tin nhắn mới nhất để không đầy RAM
    if len(local_messages) > 50:
        local_messages.pop()

# Feed Keys (ĐÃ XÓA 'mess')
FEEDS = {
    'temp': 'temp',
    'humi': 'humi',
    'light': 'lig',
    'led': 'led',
    'fan': 'fan' 
}

sensor_cache = {}
CACHE_TIMEOUT = 3 

# =================================================================
# === API ROUTES ===
# =================================================================

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    global sensor_cache
    client = aio_manager.get_client()
    current_time = time.time()
    
    # Check Cache
    if sensor_cache and (current_time - sensor_cache.get('timestamp', 0)) < CACHE_TIMEOUT:
        return jsonify(sensor_cache['data'])

    if not client: return jsonify({'error': 'No Connection'}), 500

    try:
        # Chỉ lấy dữ liệu cảm biến, KHÔNG lấy feed mess
        t = client.receive(FEEDS['temp'])
        h = client.receive(FEEDS['humi'])
        l = client.receive(FEEDS['light'])

        temp_val = float(t.value)
        humi_val = float(h.value)

        # --- LOGIC CẢNH BÁO TỰ ĐỘNG (Backend tự làm) ---
        # Thay vì chờ mạch gửi, Backend tự check và tạo thông báo
        if temp_val > 40: add_system_message("🔥 CẢNH BÁO: NHIỆT ĐỘ QUÁ CAO")
        elif temp_val < 15: add_system_message("❄️ Cảnh báo: Nhiệt độ quá thấp")
        
        if humi_val > 80: add_system_message("💧 Cảnh báo: Độ ẩm quá cao")

        # Lấy tin nhắn mới nhất để hiển thị
        latest_msg = local_messages[0]['value'] if local_messages else "Hệ thống hoạt động bình thường"

        data = {
            'temperature': temp_val,
            'humidity': humi_val,
            'light': float(l.value),
            'message': latest_msg # Trả về tin nhắn từ RAM
        }

        sensor_cache = {'data': data, 'timestamp': current_time}
        return jsonify(data)
    except Exception as e:
        print(f"Lỗi: {e}")
        if sensor_cache: return jsonify(sensor_cache['data'])
        return jsonify({'error': str(e)}), 500

@app.route('/api/device/toggle', methods=['POST'])
def toggle_device():
    client = aio_manager.get_client()
    if not client: return jsonify({'error': 'No Connection'}), 500

    try:
        data = request.json
        is_on = data.get('isOn', False)
        device_type = data.get('type', 'led') 
        
        feed_key = FEEDS.get(device_type)
        if not feed_key: return jsonify({'error': 'Invalid device'}), 400

        val = 1 if is_on else 0
        client.send(feed_key, val)
        
        # --- TỰ ĐỘNG GHI LOG KHI BẬT TẮT ---
        status_text = "BẬT" if is_on else "TẮT"
        device_name = "ĐÈN" if device_type == 'led' else "QUẠT"
        add_system_message(f"Đã {status_text} {device_name}")
        
        return jsonify({'success': True, 'isOn': is_on})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor/history', methods=['GET'])
def get_history():
    client = aio_manager.get_client()
    sensor_type = request.args.get('type', 'temp')
    limit = int(request.args.get('limit', 10))
    
    # --- NẾU LÀ LẤY LỊCH SỬ TIN NHẮN ---
    if sensor_type == 'mess':
        # Trả về list từ RAM thay vì gọi Adafruit
        return jsonify({'data': local_messages[:limit]})

    # Các sensor khác vẫn lấy từ Adafruit
    feed_key = FEEDS.get(sensor_type)
    if not feed_key: return jsonify({'error': 'Invalid type'}), 400
    
    try:
        data = client.data(feed_key, limit=limit)
        history = [{'value': item.value, 'created_at': item.created_at} for item in data]
        return jsonify({'data': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/temperature', methods=['GET'])
def predict_temperature():
    client = aio_manager.get_client()
    try:
        data = client.data(FEEDS['temp'], limit=15)
        predicted_val = ai_predictor.predict_next(data)
        return jsonify({'predicted_value': predicted_val})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_conn():
    if aio_manager.get_client(): return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    add_system_message("🚀 Hệ thống khởi động")
    app.run(host='0.0.0.0', port=5000, debug=True)