# backend/ai_model.py
import numpy as np
from sklearn.linear_model import LinearRegression

class TemperaturePredictor:
    def __init__(self):
        self.model = LinearRegression()

    def predict_next(self, history_data):
        """
        Dự đoán nhiệt độ tiếp theo dựa trên lịch sử.
        history_data: List các dict [{'value': '25', ...}, ...] lấy từ Adafruit IO
        """
        # Cần ít nhất 5 điểm dữ liệu để dự đoán
        if not history_data or len(history_data) < 5:
            return None

        try:
            # 1. Tiền xử lý dữ liệu
            # Lấy giá trị value, chuyển sang float
            # Dữ liệu từ Adafruit thường mới nhất trước -> đảo ngược lại để thành chuỗi thời gian tăng dần
            y = np.array([float(item.value) for item in history_data][::-1])
            
            # X là trục thời gian giả lập (0, 1, 2, ...)
            X = np.array(range(len(y))).reshape(-1, 1)

            # 2. Huấn luyện model (Online Learning)
            self.model.fit(X, y)

            # 3. Dự đoán bước tiếp theo (index = len(y))
            next_index = np.array([[len(y)]])
            prediction = self.model.predict(next_index)
            
            return round(prediction[0], 2)
            
        except Exception as e:
            print(f"Lỗi dự đoán AI: {e}")
            return None