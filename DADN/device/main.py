# device/main.py
import time
import sys
from Adafruit_IO import MQTTClient
import random

# --- Cấu hình Adafruit IO ---
AIO_FEED_HUMIDITY = "humi"      
AIO_FEED_TEMPERATURE = "temp"            
AIO_FEED_LED = "led"         
AIO_FEED_LIGHT = "lig"
AIO_FEED_FAN = "fan" # Thêm feed quạt

AIO_USERNAME = "2213671"
AIO_KEY = "aio_MBlp35EKYe1nCmzhQBZCFanrlrqB"

def connected(client):
    print("✅ Kết nối MQTT thành công...")
    client.subscribe(AIO_FEED_LED)
    client.subscribe(AIO_FEED_FAN) # Subscribe thêm quạt

def subscribe(client, userdata, mid, granted_qos):
    print("📡 Subscribe thành công...")

def disconnected(client):
    print("❌ Ngắt kết nối MQTT...")
    sys.exit(1)

def message(client, feed_id, payload):
    print(f"📨 Nhận lệnh: {payload} từ {feed_id}")
    if feed_id == AIO_FEED_LED:
        print(f"💡 ĐÈN: {'BẬT' if payload == '1' else 'TẮT'}")
    elif feed_id == AIO_FEED_FAN:
        print(f"💨 QUẠT: {'BẬT' if payload == '1' else 'TẮT'}")

def send_sensor_data():
    # Giả lập dữ liệu (Nhiệt độ hơi cao để test cảnh báo Backend)
    temperature = round(random.uniform(20, 45), 1) 
    humidity = round(random.uniform(40, 90), 1)
    light = random.randint(100, 1000)
    
    client.publish(AIO_FEED_TEMPERATURE, temperature)
    client.publish(AIO_FEED_HUMIDITY, humidity)
    client.publish(AIO_FEED_LIGHT, light)
    
    print(f"📊 Sent: Temp={temperature}, Humi={humidity}, Light={light}")
    # ĐÃ XÓA CODE GỬI CẢNH BÁO TẠI ĐÂY

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

while True:
    send_sensor_data()
    time.sleep(5)