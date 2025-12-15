# backend/app.py
import os
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from Adafruit_IO import Client
from ai_model import Predictor

app = Flask(__name__)
CORS(app)

# ==========================================================
# ⚠️ ĐIỀN KEY MỚI CỦA BẠN VÀO ĐÂY NHÉ
# ==========================================================
AIO_USERNAME = "2213671"
AIO_KEY = "aio_pDkB162i2GzD2BAOodNjH8VkC7ul" 

class AdafruitManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdafruitManager, cls).__new__(cls)
            try:
                if "aio_" not in AIO_KEY: # Check sơ bộ key
                    cls._instance.client = None
                else:
                    cls._instance.client = Client(AIO_USERNAME, AIO_KEY)
                    print("✅ Kết nối Adafruit thành công")
            except Exception:
                cls._instance.client = None
        return cls._instance
    def get_client(self): return self.client

aio_manager = AdafruitManager()
temp_predictor = Predictor()
humi_predictor = Predictor()

local_messages = []

def add_system_message(text):
    timestamp = datetime.now().isoformat()
    # Chỉ thêm nếu tin nhắn mới KHÁC tin nhắn gần nhất (Tránh spam server)
    if not local_messages or local_messages[0]['value'] != text:
        local_messages.insert(0, {'value': text, 'created_at': timestamp})
        if len(local_messages) > 50: local_messages.pop()

FEEDS = {'temp': 'temp', 'humi': 'humi', 'light': 'lig', 'led': 'led', 'fan': 'fan'}
sensor_cache = {}
CACHE_TIMEOUT = 5

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    global sensor_cache
    client = aio_manager.get_client()
    current_time = time.time()
    
    if sensor_cache and (current_time - sensor_cache.get('timestamp', 0)) < CACHE_TIMEOUT:
        return jsonify(sensor_cache['data'])

    if not client: return jsonify({'error': 'No Connection'}), 500

    try:
        t = client.receive(FEEDS['temp'])
        h = client.receive(FEEDS['humi'])
        l = client.receive(FEEDS['light'])
        led = client.receive(FEEDS['led'])
        fan = client.receive(FEEDS['fan'])

        temp_val = float(t.value)
        humi_val = float(h.value)
        
        # Logic cảnh báo (Backend tự check)
        if temp_val > 40: add_system_message("🔥 CẢNH BÁO: NHIỆT ĐỘ CAO > 40°C")
        if humi_val > 80: add_system_message("💧 Cảnh báo: Độ ẩm cao > 80%")

        # Lấy tin nhắn mới nhất (hoặc None nếu ko có)
        latest_msg = local_messages[0]['value'] if local_messages else None

        data = {
            'temperature': temp_val,
            'humidity': humi_val,
            'light': float(l.value),
            'led_status': int(led.value),
            'fan_status': int(fan.value),
            'message': latest_msg
        }
        sensor_cache = {'data': data, 'timestamp': current_time}
        return jsonify(data)
    except Exception as e:
        print(f"❌ Lỗi Sensor: {e}")
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
        val = 1 if is_on else 0
        
        client.send(feed_key, val)
        
        # Ghi log bật tắt
        status_text = "BẬT" if is_on else "TẮT"
        name_vn = "ĐÈN" if device_type == 'led' else "QUẠT"
        msg = f"Đã {status_text} {name_vn}"
        add_system_message(msg)
        
        global sensor_cache; sensor_cache = {} 
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor/history', methods=['GET'])
def get_history():
    client = aio_manager.get_client()
    sensor_type = request.args.get('type', 'temp')
    limit = int(request.args.get('limit', 10))
    
    if sensor_type == 'mess':
        return jsonify({'data': local_messages[:limit]})

    try:
        feed_key = FEEDS.get(sensor_type, 'temp')
        data = client.data(feed_key) # Không truyền limit vào đây
        if data: data = data[:limit] # Cắt list thủ công
        history = [{'value': item.value, 'created_at': item.created_at} for item in data]
        return jsonify({'data': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/all', methods=['GET'])
def predict_all():
    client = aio_manager.get_client()
    if not client: return jsonify({'error': 'No Connection'}), 500
    try:
        t_data = client.data(FEEDS['temp'])
        h_data = client.data(FEEDS['humi'])
        
        t_list = t_data[:10] if t_data else []
        h_list = h_data[:10] if h_data else []
        
        return jsonify({
            'temp_predict': temp_predictor.predict_next(t_list),
            'humi_predict': humi_predictor.predict_next(h_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)